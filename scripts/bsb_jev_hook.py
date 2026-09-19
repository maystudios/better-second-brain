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
- Permissive for reading files (view_file, View, ReadLocalFile) so shortlisted pages are never locked out
- Unrestricted shell bypass: shell commands (run_command, Bash) cannot be securely parsed
  without risking false positives on legitimate commands (such as running python scripts/bsb_jev.py);
  this limitation is documented and acknowledged.
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
    from scripts.bsb_jev import is_enabled, resolve_repo_root
except ImportError:
    from bsb_jev import is_enabled, resolve_repo_root

IMMUTABLE_ROOTS = {"raw"}
IMMUTABLE_FILES = {"claude.md", "bsb.config.md", "agents.md", "log.md", "index.md", "roadmap.md"}


def is_wiki_or_protected_path(target_path_str: str, repo_root: Path) -> Tuple[bool, str]:
    """Checks if a target file is within wiki/, raw/, or is a protected schema file."""
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

        return False, ""
    except Exception:
        return False, ""


def is_wiki_search(search_path_str: str, repo_root: Path) -> bool:
    """Checks if a search target path targets the wiki directory."""
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

        rel = p.relative_to(repo_root).as_posix()
        return rel == "." or rel.lower() == "wiki" or rel.lower().startswith("wiki/")
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
    write_tools = {
        "write_to_file", "replace_file_content", "multi_replace_file_content",
        "edit", "write", "notebookeditcell"
    }

    if t_name_lower in write_tools:
        target_path = (
            tool_args.get("TargetFile")
            or tool_args.get("file_path")
            or tool_args.get("path")
            or ""
        )
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

    # 3. Search Tools (Route wiki search through gateway)
    # Antigravity: grep_search
    # Claude Code / Codex: Grep
    search_tools = {"grep_search", "grep"}
    if t_name_lower in search_tools:
        search_path = tool_args.get("SearchPath") or tool_args.get("path") or ""
        if is_wiki_search(str(search_path), root):
            return make_deny(
                "Direct wiki search intercepted by bsb-jev gateway. Use 'python scripts/bsb_jev.py query \"<query>\"' "
                "for deterministic candidate retrieval and Jev semantic reranking."
            )

    # 4. Read tools (view_file, View, ReadLocalFile)
    # Permitted: reading shortlisted pages must work, no lockout.
    # 5. Other tools (run_command, etc.)
    # Return neutral {} (never return allow to avoid unwanted auto-grants)
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
                data["bsb-jev"] = {"PreToolUse": [{"matcher": "write_to_file|replace_file_content|multi_replace_file_content|grep_search", "hooks": [{"type": "command", "command": command, "timeout": 20}]}]}
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
                retained.append({"matcher": "Edit|Write|Grep|apply_patch", "hooks": [{"type": "command", "command": command, "timeout": 20}]})
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
