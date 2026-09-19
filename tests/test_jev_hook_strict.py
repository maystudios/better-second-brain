"""Contract tests for the opt-in strict Jev host guard.

These tests intentionally exercise the hook as a host policy adapter.  The
guard is useful for ordinary native tool calls, but it is not an OS sandbox
and cannot see a wrapper such as ``functions.exec`` around another command.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import bsb_jev_hook as hook


class StrictHookContract(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="bsb_jev_hook_strict_")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "CLAUDE.md").write_text("# Schema\n", encoding="utf-8")
        (self.root / "bsb.config.md").write_text("# Config\n", encoding="utf-8")
        (self.root / "roadmap.md").write_text("# Roadmap\n", encoding="utf-8")
        (self.root / "wiki").mkdir()
        (self.root / "wiki/page.md").write_text("wiki evidence\n", encoding="utf-8")
        (self.root / "raw").mkdir()
        (self.root / "raw/source.md").write_text("raw evidence\n", encoding="utf-8")
        (self.root / ".bsb-jev").mkdir()
        self._write_config(enabled=True, enforce_reads=True)

    def _write_config(self, *, enabled: bool, enforce_reads: bool, roots=None) -> None:
        (self.root / ".bsb-jev/config.json").write_text(
            json.dumps(
                {
                    "enabled": enabled,
                    "enforce_reads": enforce_reads,
                    "search_roots": roots or ["wiki"],
                    "model": "jev-1.13.0",
                    "timeout": 1.0,
                }
            ),
            encoding="utf-8",
        )

    def _call(self, name: str, args: dict, *, host: str = "claude") -> dict:
        if host == "antigravity":
            payload = {
                "toolCall": {"name": name, "args": args},
                "workspacePaths": [str(self.root)],
            }
        else:
            payload = {"tool_name": name, "tool_input": args, "cwd": str(self.root)}
        return hook.evaluate_tool_call(
            payload,
            host=host,
            repo_root=self.root,
        )

    def _assert_denied(self, result: dict) -> None:
        output = result.get("hookSpecificOutput", {})
        self.assertTrue(
            output.get("permissionDecision") == "deny" or result.get("decision") == "deny",
            result,
        )

    def test_strict_reads_block_wiki_but_allow_raw_evidence_schema_roadmap_and_external(self):
        for name, args in (
            ("Read", {"file_path": str(self.root / "wiki/page.md")}),
            ("view_file", {"AbsolutePath": str(self.root / "wiki/page.md")}),
        ):
            with self.subTest(name=name, args=args):
                self._assert_denied(self._call(name, args))

        for name, args in (
            ("read_file", {"path": str(self.root / "raw/source.md")}),
            ("ReadLocalFile", {"path": "raw/source.md"}),
        ):
            with self.subTest(name=name, args=args):
                self.assertEqual(self._call(name, args), {})

        for path in ("CLAUDE.md", "bsb.config.md", "roadmap.md"):
            with self.subTest(path=path):
                self.assertEqual(self._call("Read", {"file_path": path}), {})

        outside = self.root.parent / "outside-native-read.txt"
        outside.write_text("outside\n", encoding="utf-8")
        self.assertEqual(self._call("Read", {"file_path": str(outside)}), {})

    def test_strict_search_blocks_wiki_raw_and_broad_native_search(self):
        for path in ("wiki", "raw", "."):
            with self.subTest(path=path):
                self._assert_denied(self._call("Grep", {"pattern": "evidence", "path": path}))

    def test_strict_writes_protect_gateway_state_and_code(self):
        protected = (
            ".bsb-jev/config.json",
            "scripts/bsb_jev.py",
            "scripts/bsb_jev_hook.py",
            ".claude/settings.json",
        )
        for path in protected:
            with self.subTest(path=path):
                self._assert_denied(self._call("Write", {"file_path": path, "content": "tamper"}))

    def test_strict_shell_requires_exact_gateway_cli_and_rejects_configuration_or_embedded_commands(self):
        allowed = (
            'python scripts/bsb_jev.py query "wiki topic"',
            'python scripts/bsb_jev.py navigate "source literal" --need "What matters?"',
            'python scripts/bsb_jev.py source "https://example.test/source"',
            'python scripts/bsb_jev.py read session-abc wiki/page.md',
            'python scripts/bsb_jev.py next session-abc --need "What next?"',
            'python scripts/bsb_jev.py configure --status',
            'python scripts/bsb_jev.py advise placement "new page" --json',
            'python scripts/bsb_jev.py plan request.json --out plan.json',
            'python scripts/bsb_jev.py apply plan.json --approve',
            'python scripts/bsb_jev.py rollback plan-0123456789abcdef0123456789abcdef',
        )
        for command in allowed:
            with self.subTest(command=command):
                self.assertEqual(self._call("Bash", {"command": command}), {})

        absolute = (
            f'"{sys.executable}" "{self.root / "scripts/bsb_jev.py"}" '
            f'--root "{self.root}" source "source literal"'
        )
        self.assertEqual(self._call("Bash", {"command": absolute}), {})

        denied = (
            "git status",
            'python -c "print(1)"',
            "python scripts/other.py query topic",
            "python scripts/../scripts/bsb_jev.py query topic",
            "python -m scripts.bsb_jev query topic",
            "python scripts/bsb_jev.py status",
            "python scripts/bsb_jev.py configure",
            "python scripts/bsb_jev.py configure --status --enabled off",
            'python scripts/bsb_jev.py --root "C:/other-brain" query topic',
            "python scripts/bsb_jev.py configure --enabled off",
            'python scripts/bsb_jev.py query "topic"; type wiki/page.md',
            'python scripts/bsb_jev.py query "topic" && type wiki/page.md',
            'python scripts/bsb_jev.py query "topic" | type wiki/page.md',
        )
        for command in denied:
            with self.subTest(command=command):
                self._assert_denied(self._call("Bash", {"command": command}))

        self._assert_denied(self._call("exec_command", {"cmd": "git status"}))
        self._assert_denied(self._call("run_command", {"command": "git status"}, host="antigravity"))

    def test_strict_mode_is_opt_in_and_disabled_gateway_is_neutral(self):
        self._write_config(enabled=True, enforce_reads=False)
        self.assertEqual(self._call("Read", {"file_path": "wiki/page.md"}), {})
        self.assertEqual(self._call("Bash", {"command": "git status"}), {})

        self._write_config(enabled=False, enforce_reads=True)
        self.assertEqual(self._call("Read", {"file_path": "wiki/page.md"}), {})
        self.assertEqual(self._call("Bash", {"command": "git status"}), {})

    def test_functions_exec_wrapper_is_outside_this_hook_contract(self):
        # The outer functions.exec API is not a native tool event delivered to
        # this hook.  Keep this explicit so callers do not mistake host policy
        # for an unbypassable OS sandbox.
        self.assertEqual(
            self._call("functions.exec", {"cmd": "git status"}),
            {},
        )

    def test_relative_gateway_script_requires_brain_working_directory(self):
        self._assert_denied(self._call("Bash", {
            "command": "python scripts/bsb_jev.py source topic",
            "cwd": str(self.root.parent),
        }))
        self.assertEqual(self._call("Bash", {
            "command": "python scripts/bsb_jev.py source topic",
            "cwd": str(self.root),
        }), {})

    def test_strict_mode_protects_navigation_and_installer_code(self):
        for path in ("scripts/bsb_jev_focus.py", "scripts/bsb_jev_navigation.py", "scripts/install_jev.py"):
            with self.subTest(path=path):
                self._assert_denied(self._call("Write", {"file_path": path, "content": "tamper"}))

    def test_strict_mode_uses_custom_search_roots(self):
        (self.root / 'observations').mkdir()
        (self.root / 'observations/note.md').write_text('evidence', encoding='utf-8')
        self._write_config(enabled=True, enforce_reads=True, roots=['observations'])
        self._assert_denied(self._call('Read', {'file_path': 'observations/note.md'}))
        self._assert_denied(self._call('Grep', {'path': 'observations', 'pattern': 'evidence'}))
        self._assert_denied(self._call('Write', {'file_path': 'observations/note.md', 'content': 'x'}))

    def test_installed_matchers_include_strict_native_tool_names(self):
        hook.install_hooks_configs(self.root)
        claude = json.loads((self.root / ".claude/settings.json").read_text(encoding="utf-8"))
        codex = json.loads((self.root / ".codex/hooks.json").read_text(encoding="utf-8"))
        agents = json.loads((self.root / ".agents/hooks.json").read_text(encoding="utf-8"))
        matchers = [
            group.get("matcher", "")
            for group in claude["hooks"]["PreToolUse"] + codex["hooks"]["PreToolUse"]
        ]
        antigravity_matchers = [
            group.get("matcher", "")
            for group in agents["bsb-jev"]["PreToolUse"]
        ]
        for matcher in matchers + antigravity_matchers:
            self.assertIn("Read", matcher)
            self.assertIn("Bash", matcher)
            self.assertIn("exec_command", matcher)


if __name__ == "__main__":
    unittest.main()
