#!/usr/bin/env python3
"""Better Second Brain (BSB) - Native Host PreToolUse Hook Handler.

Supports:
1. Google Antigravity (.agents/hooks.json):
   - Input: {"toolCall": {"name": str, "args": dict}, "workspacePaths": list, "conversationId": str}
   - Output: {"decision": "deny", "reason": str} or {} (neutral verify)
2. Claude Code (.claude/settings.json):
   - Input: {"tool_name": str, "tool_input": dict, "cwd": str}
   - Output: {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": str}} or {}
3. OpenAI Codex (.codex/hooks.json):
   - Input: {"tool_name": str, "tool_input": dict, ...}
   - Output: same deny structure as Claude Code

Enforcement scope:
- Guards against direct native wiki edits (write_to_file, replace_file_content, Edit, Write, apply_patch)
- Guards against immutable raw/ and schema modifications (CLAUDE.md, bsb.config.md, log.md)
- Routes wiki searches (grep_search, Grep) through the BSB Jev semantic query gateway
- In the opt-in ``enforce_reads`` mode, blocks native reads of wiki content and
  arbitrary native shell commands, allowing only exact argv forms for the gateway
- Immutable ``raw/`` evidence reads remain available as a narrowly scoped
  source-grounding exception; native raw searches and writes remain blocked
- Keeps schema/roadmap bootstrap reads and outside-brain reads available

The strict mode is a host guard, not an OS sandbox.  It can only inspect native
PreToolUse events delivered by a configured host.  An outer wrapper such as
``functions.exec`` is outside this hook's event contract and is intentionally not
claimed as covered here.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Set

# Ensure repository root is in sys.path
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

try:
    from scripts.bsb_jev import get_config, is_enabled, resolve_repo_root
except ImportError:
    from bsb_jev import get_config, is_enabled, resolve_repo_root

IMMUTABLE_ROOTS = {"raw"}
IMMUTABLE_FILES = {"claude.md", "bsb.config.md", "agents.md", "log.md", "index.md", "roadmap.md"}

# Strict mode protects the gateway's own state and host hook configuration as
# well as the knowledge inputs.  Without this, a native Write could simply
# flip enabled/enforce_reads off or remove the hook before making a change.
GATEWAY_STATE_ROOTS = {".bsb-jev"}
HOST_CONFIG_FILES = {
    ".agents/hooks.json",
    ".claude/settings.json",
    ".codex/hooks.json",
}
GATEWAY_CODE_FILES = {
    "scripts/bsb_jev.py",
    "scripts/bsb_jev_hook.py",
    "scripts/bsb_jev_focus.py",
    "scripts/bsb_jev_navigation.py",
    "scripts/bsb_jev_search.py",
    "scripts/install_jev.py",
}

READ_TOOL_NAMES = {
    "read",
    "read_file",
    "readfile",
    "readlocalfile",
    "read_local_file",
    "read_text",
    "view",
    "view_file",
    "open_file",
}
SEARCH_TOOL_NAMES = {
    "find",
    "grep",
    "grep_search",
    "glob",
    "ripgrep",
    "search",
}
SHELL_TOOL_NAMES = {
    "bash",
    "exec_command",
    "run_command",
    "shell",
    "terminal",
}
WRITE_TOOL_NAMES = {
    "delete",
    "delete_file",
    "edit",
    "edit_file",
    "insert_file",
    "move",
    "move_file",
    "multi_replace_file_content",
    "notebookeditcell",
    "remove_file",
    "rename",
    "rename_file",
    "replace_file_content",
    "write",
    "write_file",
    "write_to_file",
}

READ_ONLY_GATEWAY_COMMANDS = {
    "advise",
    "find",
    "navigate",
    "next",
    "query",
    "read",
    "source",
}
MUTATING_GATEWAY_COMMANDS = {"apply", "plan", "rollback"}

# Native shell syntax is deliberately rejected before argv parsing.  Quoted
# values can contain punctuation (for example a query with a semicolon); the
# parser treats that punctuation as data, never as syntax.
_SHELL_SYNTAX = frozenset(";&|<>`$(){}[]*?!%\n\r\x00")


def is_wiki_or_protected_path(target_path_str: str, repo_root: Path) -> Tuple[bool, str]:
    """Checks configured knowledge roots, raw/, or protected schema files."""
    if not target_path_str or not target_path_str.strip():
        return False, ""

    try:
        norm = str(target_path_str).replace("\\", "/").strip().strip('"')
        p = Path(norm)
        lexical = Path(os.path.abspath(p if p.is_absolute() else repo_root / p))
        for candidate in (lexical, lexical.resolve()):
            if not candidate.is_relative_to(repo_root):
                continue
            rel = candidate.relative_to(repo_root).as_posix().lower()
            first_segment = rel.split('/')[0]
            if first_segment == 'wiki':
                return True, 'wiki'
            if first_segment == 'raw':
                return True, 'raw'
            if rel in IMMUTABLE_FILES:
                return True, 'schema'
            try:
                configured = get_config(repo_root).get('search_roots', ['wiki'])
            except Exception:
                configured = ['wiki']
            for search_root in configured:
                normalized_root = str(search_root).replace('\\', '/').strip('/').lower()
                if rel == normalized_root or rel.startswith(normalized_root + '/'):
                    return True, 'search'

        return False, ""
    except Exception:
        return False, ""


def _repo_relative_paths(target_path_str: str, repo_root: Path) -> Set[str]:
    """Return safe, normalized repo-relative spellings for a candidate path."""
    if not target_path_str or not str(target_path_str).strip():
        return set()
    try:
        norm = str(target_path_str).replace("\\", "/").strip().strip('"')
        p = Path(norm)
        lexical = Path(os.path.abspath(p if p.is_absolute() else repo_root / p))
        relative: Set[str] = set()
        for candidate in (lexical, lexical.resolve()):
            if candidate.is_relative_to(repo_root):
                relative.add(candidate.relative_to(repo_root).as_posix().lower())
        return relative
    except Exception:
        return set()


def is_strict_control_path(target_path_str: str, repo_root: Path) -> Tuple[bool, str]:
    """Classify gateway state/code and managed host config paths for strict mode."""
    relatives = _repo_relative_paths(target_path_str, repo_root)
    if not relatives:
        return False, ""
    for rel in relatives:
        if rel in HOST_CONFIG_FILES:
            return True, "host-config"
        if rel in GATEWAY_CODE_FILES:
            return True, "gateway-code"
        if rel in GATEWAY_STATE_ROOTS or any(rel.startswith(root + "/") for root in GATEWAY_STATE_ROOTS):
            return True, "gateway-state"
    return False, ""


def is_strict_protected_path(target_path_str: str, repo_root: Path) -> Tuple[bool, str]:
    """Classify all paths strict mode must keep behind the gateway."""
    protected, zone = is_wiki_or_protected_path(target_path_str, repo_root)
    if protected:
        return True, zone
    return is_strict_control_path(target_path_str, repo_root)


def is_enforce_reads_enabled(repo_root: Optional[Path | str] = None) -> bool:
    """Return true only for the explicit opt-in strict setting while Jev is on."""
    root = resolve_repo_root(repo_root)
    if not is_enabled(root):
        return False
    # ``get_config`` performs the project's corruption/type checks.  Strict
    # mode intentionally requires a literal JSON true, just like ``enabled``.
    return get_config(root).get("enforce_reads") is True


def _first_arg(args: Any, *names: str) -> Any:
    if not isinstance(args, dict):
        return None
    for name in names:
        if name in args:
            return args[name]
    return None


def _write_target_values(args: Any) -> List[str]:
    """Extract path-bearing fields used by native write/move/delete tools."""
    if not isinstance(args, dict):
        return []
    names = (
        "TargetFile",
        "target_file",
        "file_path",
        "filePath",
        "path",
        "Path",
        "source",
        "source_path",
        "destination",
        "destination_path",
        "from",
        "to",
        "old_path",
        "new_path",
    )
    values: List[str] = []
    for name in names:
        value = args.get(name)
        if isinstance(value, str) and value.strip():
            values.append(value)
    return values


def is_wiki_search(search_path_str: str, repo_root: Path) -> bool:
    """Checks if a search target path targets any configured knowledge root."""
    if not search_path_str or not search_path_str.strip():
        search_path_str = "."

    try:
        p = Path(search_path_str)
        if not p.is_absolute():
            p = (repo_root / p).resolve()
        else:
            p = p.resolve()

        if not p.is_relative_to(repo_root):
            return False

        rel = p.relative_to(repo_root).as_posix().lower()
        if rel == ".":
            return True
        try:
            roots = get_config(repo_root).get('search_roots', ['wiki'])
        except Exception:
            roots = ['wiki']
        return any(rel == str(item).replace('\\', '/').strip('/').lower()
                   or rel.startswith(str(item).replace('\\', '/').strip('/').lower() + '/')
                   for item in roots)
    except Exception:
        return False


def check_patch_targets_wiki(patch_content: str, repo_root=None) -> bool:
    """Detects if an apply_patch unified diff targets wiki, raw, or schema files."""
    if not patch_content:
        return False
    root = resolve_repo_root(repo_root)
    for line in patch_content.splitlines():
        match = re.match(r'^\*\*\* (?:(?:Add|Update|Delete) File|Move (?:to|from)): (.+)$', line)
        if match:
            target = match.group(1)
        elif line.startswith(('--- ', '+++ ')):
            target = line[4:].split('\t', 1)[0].strip('"')
            if target.startswith(('a/', 'b/')):
                target = target[2:]
        else:
            continue
        if is_wiki_or_protected_path(target, root)[0]:
            return True
    return False


def check_patch_targets_strict(patch_content: str, repo_root=None) -> bool:
    """Detect strict-mode edits to knowledge, gateway state, or host config."""
    if not patch_content:
        return False
    root = resolve_repo_root(repo_root)
    for line in patch_content.splitlines():
        match = re.match(r'^\*\*\* (?:(?:Add|Update|Delete) File|Move (?:to|from)): (.+)$', line)
        if match:
            target = match.group(1)
        elif line.startswith(('--- ', '+++ ')):
            target = line[4:].split('\t', 1)[0].strip('"')
            if target.startswith(('a/', 'b/')):
                target = target[2:]
        else:
            continue
        if is_strict_protected_path(target, root)[0]:
            return True
    return False


def _parse_native_argv(command: Any) -> Optional[List[str]]:
    """Parse a host shell string into argv without invoking shell semantics."""
    if isinstance(command, (list, tuple)):
        if not command or not all(isinstance(item, str) and item for item in command):
            return None
        if any("\x00" in item for item in command):
            return None
        return list(command)
    if not isinstance(command, str) or not command.strip():
        return None

    tokens: List[str] = []
    current: List[str] = []
    quote: Optional[str] = None

    def flush() -> None:
        if current:
            tokens.append("".join(current))
            current.clear()

    for char in command:
        if quote is not None:
            # Bash and PowerShell evaluate these even within double quotes.
            # This parser never attempts to interpret escaping or expansion.
            if quote == '"' and char in '$`':
                return None
            if char == quote:
                quote = None
            else:
                current.append(char)
            continue
        if char in ("'", '"'):
            quote = char
        elif char.isspace():
            flush()
        elif char in _SHELL_SYNTAX:
            return None
        else:
            current.append(char)
    if quote is not None:
        return None
    flush()
    return tokens or None


def _same_path(left: Path | str, right: Path | str) -> bool:
    try:
        return os.path.normcase(str(Path(left).resolve(strict=False))) == os.path.normcase(
            str(Path(right).resolve(strict=False))
        )
    except Exception:
        return False


def _is_allowed_python_executable(token: str) -> bool:
    normalized = token.strip().casefold()
    if normalized in {"python", "python3", "python.exe", "python3.exe", "py", "py.exe"}:
        return True
    return _same_path(token, Path(sys.executable))


def _is_gateway_script(token: str, root: Path) -> bool:
    normalized = token.replace("\\", "/").strip()
    if not normalized or any(part == ".." for part in normalized.split("/")):
        return False
    if normalized.startswith("./"):
        normalized = normalized[2:]
    if normalized.casefold() == "scripts/bsb_jev.py":
        return True
    return _same_path(token, root / "scripts/bsb_jev.py")


def _validate_gateway_args(command: str, args: List[str]) -> bool:
    """Validate one gateway subcommand's small, explicit argv grammar."""
    specs = {
        "find": (1, 1, {"--dry-run"}, {"--need", "--max-calls", "--max-pages"}, {"--need"}),
        "query": (1, 1, {"--dry-run", "--json", "--prune"}, {"--candidate-limit", "--limit", "--roots"}, set()),
        "navigate": (1, 1, {"--dry-run"}, {"--need"}, {"--need"}),
        "source": (1, 1, {"--dry-run"}, set(), set()),
        "read": (2, 2, set(), set(), set()),
        "next": (1, 1, {"--dry-run"}, {"--need"}, {"--need"}),
        "advise": (2, 2, {"--dry-run", "--json"}, set(), set()),
        "plan": (1, 1, {"--dry-run"}, {"--out"}, set()),
        "apply": (1, 1, {"--approve", "--dry-run"}, set(), set()),
        "rollback": (1, 1, set(), set(), set()),
        "configure": (0, 0, {"--status"}, set(), set()),
    }
    spec = specs.get(command)
    if spec is None:
        return False
    minimum, maximum, flags, valued, repeatable = spec
    positional: List[str] = []
    seen: Set[str] = set()
    index = 0
    while index < len(args):
        item = args[index]
        if item.startswith("-"):
            if item in flags:
                if item in seen:
                    return False
                seen.add(item)
                index += 1
                continue
            if item not in valued:
                return False
            if item not in repeatable and item in seen:
                return False
            if index + 1 >= len(args) or not args[index + 1] or args[index + 1].startswith("-"):
                return False
            value = args[index + 1]
            if item in {"--limit", "--candidate-limit", "--max-calls", "--max-pages"} and not re.fullmatch(r"[0-9]+", value):
                return False
            if item == "--need" and len([x for x in args[:index] if x == "--need"]) >= 6:
                return False
            seen.add(item)
            index += 2
            continue
        positional.append(item)
        index += 1

    if not minimum <= len(positional) <= maximum:
        return False
    if command == "navigate" and not any(item == "--need" for item in args):
        return False
    if command == "apply" and "--approve" not in seen:
        return False
    if command == "configure" and "--status" not in seen:
        return False
    return True


def is_allowed_gateway_command(command: Any, repo_root: Path, cwd: Optional[Path | str] = None) -> bool:
    """Return whether a native shell argv is an exact approved gateway call."""
    argv = _parse_native_argv(command)
    if not argv or len(argv) < 3:
        return False
    if not _is_allowed_python_executable(argv[0]) or not _is_gateway_script(argv[1], repo_root):
        return False
    # A relative script name is safe only when the host will execute from the
    # brain root. Otherwise ``scripts/bsb_jev.py`` could resolve to an unrelated
    # directory even though the argv text looks like an approved gateway call.
    if cwd is not None and not Path(argv[1]).is_absolute() and not _same_path(cwd, repo_root):
        return False

    index = 2
    if argv[index] == "--root":
        if index + 1 >= len(argv) or not _same_path(argv[index + 1], repo_root):
            return False
        index += 2
    elif argv[index].startswith("--root="):
        if not _same_path(argv[index][len("--root="):], repo_root):
            return False
        index += 1
    if index >= len(argv):
        return False
    subcommand = argv[index].casefold()
    if subcommand == "configure":
        return _validate_gateway_args(subcommand, argv[index + 1:])
    if subcommand not in READ_ONLY_GATEWAY_COMMANDS | MUTATING_GATEWAY_COMMANDS:
        return False
    return _validate_gateway_args(subcommand, argv[index + 1:])


def evaluate_tool_call(
    input_data: Dict[str, Any],
    host: Optional[str] = None,
    repo_root: Optional[Path | str] = None,
) -> Dict[str, Any]:
    """Evaluates incoming tool call and returns deny decision or neutral {}."""
    root = resolve_repo_root(repo_root)

    # If gateway is disabled, return neutral {} immediately
    if not is_enabled(root):
        return {}
    strict = is_enforce_reads_enabled(root)

    # Detect host format
    is_antigravity = "toolCall" in input_data
    is_claude_or_codex = "tool_name" in input_data

    if host == "antigravity" or (is_antigravity and not host):
        tool_call = input_data.get("toolCall", {})
        tool_name = tool_call.get("name", "")
        tool_args = tool_call.get("args", {})
        detected_host = "antigravity"
    elif host in ("claude", "codex") or (is_claude_or_codex and not host):
        tool_name = input_data.get("tool_name", "")
        tool_args = input_data.get("tool_input", {})
        detected_host = "claude"
    else:
        tool_name = input_data.get("name", "")
        tool_args = input_data.get("args", {})
        detected_host = "antigravity"

    def make_deny(reason: str) -> Dict[str, Any]:
        if detected_host in ("claude", "codex"):
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        return {"decision": "deny", "reason": reason}

    t_name_lower = tool_name.lower()

    # 1. File Modification Tools (Block direct wiki / raw / schema edits)
    # Antigravity: write_to_file, replace_file_content, multi_replace_file_content
    # Claude Code: Edit, Write, NotebookEditCell
    # Codex: apply_patch, edit, write
    if t_name_lower in WRITE_TOOL_NAMES:
        target_paths = _write_target_values(tool_args)
        if strict and not target_paths:
            return make_deny(
                "Strict Jev enforcement cannot identify this native write target. "
                "Use the gateway CLI for bounded changes."
            )
        for target_path in target_paths:
            is_prot, zone = is_wiki_or_protected_path(str(target_path), root)
            if is_prot:
                if zone == "raw":
                    return make_deny(
                        "Direct raw/ edits blocked by BSB schema §1: raw sources are immutable curated inputs."
                    )
                elif zone == "schema":
                    return make_deny(
                        "Direct schema/log edits blocked by BSB schema §7: propose changes in roadmap.md or consult §7."
                    )
                else:
                    return make_deny(
                        "Direct wiki edits blocked by bsb-jev gateway. Use 'python scripts/bsb_jev.py plan <request.json>' "
                        "and 'apply <plan.json> --approve' to stage and apply verified, citation-backed mutations."
                    )
            if strict:
                control, control_zone = is_strict_control_path(str(target_path), root)
                if control:
                    return make_deny(
                        f"Strict Jev enforcement blocks direct {control_zone} edits. "
                        "Use the gateway CLI for knowledge changes and leave gateway state/hooks managed by Jev."
                    )

    # 2. Codex apply_patch tool
    if t_name_lower == "apply_patch":
        patch_text = (
            tool_args.get("patch")
            or tool_args.get("command")
            or tool_args.get("input")
            or ""
        )
        if check_patch_targets_wiki(patch_text, root):
            return make_deny(
                "Direct patch application to wiki/raw/schema blocked by bsb-jev gateway. "
                "Use 'python scripts/bsb_jev.py plan <request.json>' and 'apply <plan.json> --approve'."
            )
        if strict and check_patch_targets_strict(patch_text, root):
            return make_deny(
                "Strict Jev enforcement blocks direct patches to knowledge, gateway state, or host hooks. "
                "Use the gateway CLI for bounded changes."
            )

    # 3. Search Tools (Route wiki search through gateway)
    # Antigravity: grep_search
    # Claude Code / Codex: Grep
    if t_name_lower in SEARCH_TOOL_NAMES:
        raw_search_path = _first_arg(tool_args, "SearchPath", "search_path", "path", "Path", "directory")
        if strict and raw_search_path is not None and not isinstance(raw_search_path, str):
            return make_deny(
                "Strict Jev enforcement cannot validate this native search scope. Use the gateway find command."
            )
        search_path = raw_search_path or ""
        searches_wiki = is_wiki_search(str(search_path), root)
        searches_raw = is_wiki_or_protected_path(str(search_path), root)[1] == "raw"
        if searches_wiki or (strict and searches_raw):
            return make_deny(
                "Direct wiki search intercepted by bsb-jev gateway. Use 'python scripts/bsb_jev.py find \"<query>\"' "
                "for catalog-first branching retrieval and full selected pages."
            )

    # 4. Read tools.  Legacy mode remains permissive so existing Jev installs
    # do not lock agents out.  Strict mode routes wiki full-page reads to the
    # gateway's receipt-backed read command.  Immutable raw reads remain
    # available for source grounding; raw search and write paths stay guarded.
    if strict and t_name_lower in READ_TOOL_NAMES:
        target_path = _first_arg(
            tool_args,
            "AbsolutePath",
            "absolute_path",
            "file_path",
            "filePath",
            "path",
            "Path",
        )
        if not isinstance(target_path, str) or not target_path.strip():
            return make_deny(
                "Strict Jev enforcement cannot identify this native read. Use the gateway read command with a receipt."
            )
        protected, zone = is_wiki_or_protected_path(target_path, root)
        if protected and zone in {"wiki", "search"}:
            return make_deny(
                "Strict Jev enforcement blocks direct wiki reads. Use gateway find for full selected pages, or source/read for literal lookup."
            )

    # 5. Shell tools.  Strict mode is intentionally fail-closed: only the
    # exact gateway executable/script argv grammar is admitted.  This rejects
    # shell operators, interpreters, alternate scripts, and configure/off.
    if strict and t_name_lower in SHELL_TOOL_NAMES:
        command = _first_arg(tool_args, "command", "cmd", "Command", "input", "script")
        working_dir = _first_arg(tool_args, "cwd", "Cwd", "workdir", "working_directory")
        if working_dir is None:
            working_dir = input_data.get("cwd")
        if not is_allowed_gateway_command(command, root, working_dir):
            return make_deny(
                "Strict Jev enforcement blocks arbitrary native shell commands. "
                "Use an exact python scripts/bsb_jev.py gateway command; only configure --status is permitted."
            )

    # Return neutral {} (never return allow to avoid unwanted auto-grants).
    return {}


# -----------------------------------------------------------------------------
# Hook Installer & Uninstaller
# -----------------------------------------------------------------------------

def _load_json_file_or_empty(path: Path) -> Dict[str, Any]:
    """Loads existing JSON file or returns empty dict. Raises ValueError if corrupt."""
    if not path.is_file():
        return {}
    raw_content = path.read_text(encoding="utf-8").strip()
    if not raw_content:
        return {}
    try:
        data = json.loads(raw_content)
        if not isinstance(data, dict):
            raise ValueError(f"Top-level JSON in {path} must be an object")
        return data
    except Exception as e:
        raise ValueError(f"Corrupt JSON in {path}: {e}")


def _hook_files(root):
    return [(root / ".agents/hooks.json", "antigravity"),
            (root / ".claude/settings.json", "claude"),
            (root / ".codex/hooks.json", "codex")]


def _ours(group):
    # Only remove our generated handlers, preserving other handlers in a group.
    return "bsb_jev_hook.py" in str(group.get("command", ""))


def _configure_hooks(repo_root, install):
    import copy
    import tempfile
    root = Path(repo_root).resolve()
    # AGY on Windows invokes cmd.exe: a quoted first token is double-escaped by
    # that host. An unquoted executable (or PATH Python) avoids that host bug.
    executable = Path(sys.executable).as_posix()
    if os.name == "nt":
        executable = executable if not any(c.isspace() for c in executable) else "python"
    else:
        import shlex
        executable = shlex.quote(executable)
    changes = []
    for path, host in _hook_files(root):
        old = path.read_bytes() if path.exists() else None
        data = copy.deepcopy(_load_json_file_or_empty(path))
        if host == "antigravity":
            if install:
                # AGY runs project hook commands in .agents/ and its Windows
                # launcher escapes quotes literally. Relative paths also work
                # when the vault directory contains spaces.
                command = f'{executable} ../scripts/bsb_jev_hook.py --host {host}'
                data["bsb-jev"] = {"PreToolUse": [{"matcher": "write_to_file|replace_file_content|multi_replace_file_content|grep_search|view_file|read_file|readfile|Read|ReadLocalFile|delete|delete_file|move|move_file|rename|rename_file|run_command|exec_command|Bash|Shell|terminal", "hooks": [{"type": "command", "command": command, "timeout": 20}]}]}
            else:
                data.pop("bsb-jev", None)
        else:
            events = data.setdefault("hooks", {})
            if not isinstance(events, dict):
                raise ValueError("hooks must be an object")
            groups = events.get("PreToolUse", [])
            if not isinstance(groups, list):
                raise ValueError("PreToolUse must be an array")
            retained = []
            for group in groups:
                if not isinstance(group, dict):
                    raise ValueError("Invalid hook group")
                if _ours(group):
                    continue  # remove legacy flat BSB handler only
                if "hooks" in group:
                    if not isinstance(group["hooks"], list):
                        raise ValueError("Invalid hook handlers")
                    handlers = [h for h in group["hooks"] if not _ours(h)]
                    if not handlers:
                        continue
                    group = dict(group, hooks=handlers)
                retained.append(group)
            if install:
                command = f'{executable} "{(root / "scripts/bsb_jev_hook.py").as_posix()}" --root "{root.as_posix()}" --host {host}'
                retained.append({"matcher": "Edit|Write|WriteFile|NotebookEditCell|Grep|grep|find|search|glob|Read|read_file|readfile|view_file|ReadLocalFile|View|Delete|delete_file|Move|move_file|Rename|rename_file|apply_patch|run_command|exec_command|Bash|Shell|terminal", "hooks": [{"type": "command", "command": command, "timeout": 20}]})
            events["PreToolUse"] = retained
        changes.append((path, old, json.dumps(data, indent=2).encode("utf-8")))
    # Validate every existing host config before mutating any of them.
    written = []
    try:
        for path, old, new in changes:
            if old == new or (old is None and not install):
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as temp:
                temp.write(new)
                temp_path = Path(temp.name)
            try:
                os.replace(temp_path, path)
            finally:
                temp_path.unlink(missing_ok=True)
            written.append((path, old))
    except Exception:
        for path, old in reversed(written):
            if old is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(old)
        raise


def install_hooks_configs(repo_root: Path) -> None:
    """Merge host-specific native hooks without touching unrelated handlers."""
    _configure_hooks(repo_root, True)


def uninstall_hooks_configs(repo_root: Path) -> None:
    """Remove only BSB handlers; corrupt host configs remain untouched."""
    _configure_hooks(repo_root, False)


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--root")
    parser.add_argument("--host", choices=["claude", "codex", "antigravity"])
    args = parser.parse_args()
    try:
        raw_input = sys.stdin.buffer.read(1048577)
        if len(raw_input) > 1048576:
            raise ValueError("Hook input too large")
        input_data = json.loads(raw_input.decode('utf-8-sig'))
        if not isinstance(input_data, dict):
            raise ValueError("Hook input must be an object")
        root = args.root or str(Path(__file__).resolve().parent.parent)
        if not root and input_data.get("workspacePaths"):
            root = input_data["workspacePaths"][0]
        decision = evaluate_tool_call(input_data, host=args.host, repo_root=root)
    except Exception:
        # Supported hosts treat exit 2 as blocking; JSON supports agy too.
        reason = "BSB Jev hook could not validate this call; check local config and retry."
        if args.host == "antigravity":
            print(json.dumps({"decision": "deny", "reason": reason}))
        else:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": reason}}))
        print(reason, file=sys.stderr)
        return 2
    print(json.dumps(decision))
    return 0


if __name__ == "__main__":
    sys.exit(main())
