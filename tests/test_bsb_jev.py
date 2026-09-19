#!/usr/bin/env python3
"""Comprehensive test suite for Better Second Brain (BSB) Jev integration.

Tests cover:
- Disabled mode (zero network calls, clean status)
- Deterministic candidate generation and Jev reranking
- Contradiction / counterevidence preservation
- Secret redaction and credential handling
- Redirect protection, timeouts, and bounded payload/response
- Mutation safety (immutable raw/schema, path traversal, stale hashes, backlink checks, atomic rollback)
- Native hook interception (Antigravity & Claude formats, reading allowed, direct wiki edits blocked)
- Configuration and hook installer merging (preserving unrelated settings)
"""

import datetime
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

# Ensure repository root is in sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from scripts import bsb_jev
    from scripts import bsb_jev_hook
    MODULES_IMPORTED = True
except ImportError:
    MODULES_IMPORTED = False


class TestModuleImport(unittest.TestCase):
    """Verify modules exist and are importable."""

    def test_imports_succeed(self):
        self.assertTrue(MODULES_IMPORTED, "scripts.bsb_jev and scripts.bsb_jev_hook must be importable")


class TestBSBJevConfigAndDisabled(unittest.TestCase):
    """Test configuration management and disabled state."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="bsb_jev_test_")
        self.root = Path(self.test_dir)
        (self.root / "CLAUDE.md").write_text("# Schema\n", encoding="utf-8")
        (self.root / "bsb.config.md").write_text(
            "# Config\n\n| layer | status | enable with |\n|---|---|---|\n| graphify | off | ... |\n",
            encoding="utf-8"
        )
        (self.root / "wiki").mkdir()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_default_is_disabled(self):
        if not MODULES_IMPORTED:
            self.skipTest("bsb_jev not implemented yet")
        self.assertFalse(bsb_jev.is_enabled(self.root))
        cfg = bsb_jev.get_config(self.root)
        self.assertFalse(cfg.get("enabled", False))

    def test_configure_enables_and_disables(self):
        if not MODULES_IMPORTED:
            self.skipTest("bsb_jev not implemented yet")
        # Enable
        res = bsb_jev.configure_gateway(self.root, enabled=True, roots=["wiki", "moc"])
        self.assertTrue(res["enabled"])
        self.assertTrue(bsb_jev.is_enabled(self.root))
        cfg = bsb_jev.get_config(self.root)
        self.assertTrue(cfg["enabled"])
        self.assertEqual(cfg["search_roots"], ["wiki", "moc"])

        # Disable
        res2 = bsb_jev.configure_gateway(self.root, enabled=False)
        self.assertFalse(res2["enabled"])
        self.assertFalse(bsb_jev.is_enabled(self.root))

    def test_disabled_query_makes_zero_network_calls(self):
        if not MODULES_IMPORTED:
            self.skipTest("bsb_jev not implemented yet")
        # Add sample file so lexical candidates exist
        (self.root / "wiki" / "sample.md").write_text(
            "---\ntype: concept\ntitle: Test Search Concept\n---\nTest search content.\n",
            encoding="utf-8"
        )
        # Query when disabled must not call any transport or network
        network_called = []

        def failing_transport(*args, **kwargs):
            network_called.append(True)
            raise RuntimeError("Network should not be called when disabled")

        res = bsb_jev.query("test search", repo_root=self.root, transport=failing_transport)
        self.assertEqual(len(network_called), 0)
        self.assertEqual(res["status"], "disabled")


class TestBSBJevQueryAndRerank(unittest.TestCase):
    """Test candidate extraction, snippet extraction, and reranking."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="bsb_jev_query_")
        self.root = Path(self.test_dir)
        (self.root / "CLAUDE.md").write_text("# Schema\n", encoding="utf-8")
        wiki = self.root / "wiki"
        wiki.mkdir()
        (wiki / "concepts").mkdir()
        (wiki / "sources").mkdir()

        # Create sample pages
        (wiki / "concepts" / "lean-fill.md").write_text(
            "---\ntype: concept\ntitle: Lean Fill Method\naliases: [lean-fill, lean]\n---\n"
            "# Lean Fill\n"
            "Lean fill populates pages with dense citations ([[wiki/sources/lean-src]]).\n"
            "It reduces reading cost by ~66% without quality degradation.\n",
            encoding="utf-8"
        )
        (wiki / "concepts" / "counter-example.md").write_text(
            "---\ntype: concept\ntitle: Verbose Fill\n---\n"
            "# Verbose Fill\n"
            "Contradicts lean fill by repeating entire source prose verbatim.\n",
            encoding="utf-8"
        )
        (wiki / "sources" / "lean-src.md").write_text(
            "---\ntype: source\ntitle: Source on Lean Filling\n---\n"
            "## Key claims\n"
            "- Lean fill yields 66% token reduction.\n",
            encoding="utf-8"
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_deterministic_lexical_candidate_generation(self):
        if not MODULES_IMPORTED:
            self.skipTest("bsb_jev not implemented yet")
        candidates = bsb_jev.extract_lexical_candidates(
            query="lean fill",
            repo_root=self.root,
            roots=["wiki"],
            max_candidates=16
        )
        self.assertGreaterEqual(len(candidates), 1)
        paths = [c["path"] for c in candidates]
        self.assertTrue(any("lean-fill.md" in p for p in paths))
        # Check snippet structure
        c0 = candidates[0]
        self.assertIn("line_start", c0)
        self.assertIn("line_end", c0)
        self.assertIn("text", c0)
        self.assertIn("file_sha256", c0)

    def test_query_with_mock_transport_rerank(self):
        if not MODULES_IMPORTED:
            self.skipTest("bsb_jev not implemented yet")
        bsb_jev.configure_gateway(self.root, enabled=True)

        def mock_transport(payload, api_key, model, timeout):
            # Inspect payload structure
            self.assertEqual(model, bsb_jev.DEFAULT_MODEL)
            self.assertIn("state", payload)
            self.assertIn("questions", payload)
            questions = payload["questions"]

            # Return answers
            answers = {}
            for qid in questions:
                answers[qid] = {
                    "type": "choice",
                    "choice": "high" if "lean" in qid.lower() or "c1" in qid.lower() else "low",
                    "confidence": 0.95,
                    "probabilities": {
                        "high": 0.95 if "lean" in qid.lower() or "c1" in qid.lower() else 0.05,
                        "medium": 0.02,
                        "low": 0.02 if "lean" in qid.lower() or "c1" in qid.lower() else 0.92,
                        "unknown": 0.01,
                    }
                }
            return {
                "model": model,
                "usage": {"input_tokens": 120, "output_tokens": 40},
                "answers": answers,
            }

        res = bsb_jev.query("lean fill token reduction", repo_root=self.root, limit=2, transport=mock_transport, api_key="dummy-key")
        self.assertEqual(res["status"], "recommended")
        self.assertGreaterEqual(len(res["selected"]), 1)
        self.assertIn("metrics", res)
        self.assertIn("reduction_ratio", res["metrics"])
        self.assertIn("usage", res)

    def test_contradiction_not_discarded(self):
        if not MODULES_IMPORTED:
            self.skipTest("bsb_jev not implemented yet")
        bsb_jev.configure_gateway(self.root, enabled=True)

        # Contradiction classification should be treated as high-priority evidence
        def mock_transport(payload, api_key, model, timeout):
            answers = {}
            for qid in payload["questions"]:
                answers[qid] = {
                    "type": "choice",
                    "choice": "high",  # Classified high because it's relevant counterevidence
                    "confidence": 0.9,
                    "probabilities": {"high": 0.9, "medium": 0.05, "low": 0.03, "unknown": 0.02}
                }
            return {
                "model": model,
                "usage": {"input_tokens": 100, "output_tokens": 30},
                "answers": answers,
            }

        res = bsb_jev.query("does verbose fill contradict lean fill", repo_root=self.root, limit=4, transport=mock_transport, api_key="dummy-key")
        self.assertEqual(res["status"], "recommended")
        paths = [s["path"] for s in res["selected"]]
        self.assertTrue(any("counter-example.md" in p for p in paths))


class TestBSBSecretRedactionAndLimits(unittest.TestCase):
    """Test security: secret redaction, DPAPI loading, bounded limits."""

    def test_redact_secrets(self):
        if not MODULES_IMPORTED:
            self.skipTest("bsb_jev not implemented yet")
        secret = "secret-token-xyz-12345"
        text = f"Error with Bearer {secret} and api_key = {secret}"
        sanitized = bsb_jev.sanitize_text(text, secret=secret)
        self.assertNotIn(secret, sanitized)
        self.assertIn("[REDACTED]", sanitized)

    def test_safe_redirect_handler_blocks_untrusted_host(self):
        if not MODULES_IMPORTED:
            self.skipTest("bsb_jev not implemented yet")
        handler = bsb_jev.SafeRedirectHandler()
        with self.assertRaises(urllib.error.HTTPError):
            handler.redirect_request(None, None, 302, "Found", {}, "http://untrusted.com/steal")
        with self.assertRaises(urllib.error.HTTPError):
            handler.redirect_request(None, None, 302, "Found", {}, "https://evil-site.com/api")

    def test_missing_api_key_returns_graceful_status(self):
        if not MODULES_IMPORTED:
            self.skipTest("bsb_jev not implemented yet")
        # Ensure no env var
        with patch.dict(os.environ, {}, clear=True):
            with patch("scripts.bsb_jev.load_api_key", return_value=None):
                res = bsb_jev.query("test query", repo_root=Path("."), api_key=None)
                # Should fail open with fallback or clear status, never crash
                self.assertIn(res["status"], ("fallback", "needs_orchestrator", "disabled", "completed"))
                self.assertFalse(res.get("error_unhandled", False))


class TestBSBJevMutationPlanAndApply(unittest.TestCase):
    """Test plan creation, preflight invariants, backlink checks, atomic apply, and rollback."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="bsb_jev_mutation_")
        self.root = Path(self.test_dir)
        (self.root / "CLAUDE.md").write_text("# Schema\n", encoding="utf-8")
        (self.root / "bsb.config.md").write_text("# Config\n", encoding="utf-8")
        raw = self.root / "raw"
        raw.mkdir()
        (raw / "source.txt").write_text("Immutable raw source", encoding="utf-8")

        wiki = self.root / "wiki"
        wiki.mkdir()
        (wiki / "concepts").mkdir()
        (wiki / "sources").mkdir()

        (wiki / "sources" / "src1.md").write_text(
            "---\ntype: source\ntitle: Src1\n---\nReal source facts.\n",
            encoding="utf-8"
        )
        (wiki / "concepts" / "page-a.md").write_text(
            "---\ntype: concept\ntitle: Page A\n---\n"
            "Page A references [[wiki/concepts/page-b]] and [[wiki/sources/src1]].\n",
            encoding="utf-8"
        )
        (wiki / "concepts" / "page-b.md").write_text(
            "---\ntype: concept\ntitle: Page B\n---\n"
            "Page B body with citations ([[wiki/sources/src1]]).\n",
            encoding="utf-8"
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_immutable_raw_rejected(self):
        if not MODULES_IMPORTED:
            self.skipTest("bsb_jev not implemented yet")
        request = {
            "mutations": [
                {
                    "action": "insert",
                    "path": "raw/new_source.txt",
                    "content": "Trying to modify raw directly",
                    "citations": ["wiki/sources/src1"]
                }
            ]
        }
        with self.assertRaises(ValueError) as ctx:
            bsb_jev.create_plan(request, repo_root=self.root)
        self.assertIn("immutable", str(ctx.exception).lower())

    def test_immutable_schema_rejected(self):
        if not MODULES_IMPORTED:
            self.skipTest("bsb_jev not implemented yet")
        request = {
            "mutations": [
                {
                    "action": "edit",
                    "path": "CLAUDE.md",
                    "content": "# Tampered Schema\n",
                    "base_hash": hashlib.sha256((self.root / "CLAUDE.md").read_bytes()).hexdigest(),
                    "citations": ["wiki/sources/src1"]
                }
            ]
        }
        with self.assertRaises(ValueError) as ctx:
            bsb_jev.create_plan(request, repo_root=self.root)
        self.assertIn("schema", str(ctx.exception).lower())

    def test_path_traversal_rejected(self):
        if not MODULES_IMPORTED:
            self.skipTest("bsb_jev not implemented yet")
        request = {
            "mutations": [
                {
                    "action": "insert",
                    "path": "../outside.md",
                    "content": "escape attempt",
                    "citations": ["wiki/sources/src1"]
                }
            ]
        }
        with self.assertRaises(ValueError) as ctx:
            bsb_jev.create_plan(request, repo_root=self.root)
        self.assertIn("path", str(ctx.exception).lower())

    def test_deletion_with_live_backlinks_refused(self):
        if not MODULES_IMPORTED:
            self.skipTest("bsb_jev not implemented yet")
        # page-a links to page-b; attempt to delete page-b must be refused!
        b_hash = hashlib.sha256((self.root / "wiki" / "concepts" / "page-b.md").read_bytes()).hexdigest()
        request = {
            "mutations": [
                {
                    "action": "delete",
                    "path": "wiki/concepts/page-b.md",
                    "base_hash": b_hash
                }
            ]
        }
        with self.assertRaises(ValueError) as ctx:
            bsb_jev.create_plan(request, repo_root=self.root)
        self.assertIn("backlink", str(ctx.exception).lower())

    def test_successful_insert_and_stale_hash_protection(self):
        if not MODULES_IMPORTED:
            self.skipTest("bsb_jev not implemented yet")
        new_path = "wiki/concepts/page-c.md"
        request = {
            "mutations": [
                {
                    "action": "insert",
                    "path": new_path,
                    "content": "---\ntype: concept\ntitle: Page C\n---\nPage C ([[wiki/sources/src1]])\n",
                    "citations": ["wiki/sources/src1"]
                }
            ]
        }
        plan = bsb_jev.create_plan(request, repo_root=self.root)
        self.assertEqual(plan["status"], "planned")

        # Refusal without approve
        with self.assertRaises(ValueError):
            bsb_jev.apply_plan(plan, repo_root=self.root, approve=False)

        # Successful apply with approve
        res = bsb_jev.apply_plan(plan, repo_root=self.root, approve=True)
        self.assertEqual(res["status"], "applied")
        self.assertTrue((self.root / new_path).is_file())

        # Now test edit with stale base hash
        curr_hash = hashlib.sha256((self.root / new_path).read_bytes()).hexdigest()
        wrong_hash = "0123456789abcdef" * 4
        edit_request = {
            "mutations": [
                {
                    "action": "edit",
                    "path": new_path,
                    "content": "Edited content",
                    "base_hash": wrong_hash,
                    "citations": ["wiki/sources/src1"]
                }
            ]
        }
        with self.assertRaises(ValueError) as ctx:
            bsb_jev.create_plan(edit_request, repo_root=self.root)
        self.assertIn("hash", str(ctx.exception).lower())

    def test_audit_log_appended(self):
        if not MODULES_IMPORTED:
            self.skipTest("bsb_jev not implemented yet")
        new_path = "wiki/concepts/page-d.md"
        request = {
            "mutations": [
                {
                    "action": "insert",
                    "path": new_path,
                    "content": "---\ntype: concept\ntitle: Page D\n---\nPage D content ([[wiki/sources/src1]])\n",
                    "citations": ["wiki/sources/src1"]
                }
            ]
        }
        plan = bsb_jev.create_plan(request, repo_root=self.root)
        bsb_jev.apply_plan(plan, repo_root=self.root, approve=True)
        audit_file = self.root / ".bsb-jev" / "audit.jsonl"
        self.assertTrue(audit_file.is_file())
        lines = audit_file.read_text(encoding="utf-8").strip().splitlines()
        self.assertGreaterEqual(len(lines), 1)
        last_rec = json.loads(lines[-1])
        self.assertEqual(last_rec["plan_id"], plan["plan_id"])
        self.assertEqual(last_rec["action"], "apply")


class TestBSBJevHooks(unittest.TestCase):
    """Test Antigravity and Claude hook decision enforcement."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="bsb_jev_hooks_")
        self.root = Path(self.test_dir)
        (self.root / "CLAUDE.md").write_text("# Schema\n", encoding="utf-8")
        (self.root / "wiki").mkdir()
        (self.root / "raw").mkdir()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_hooks_neutral_when_disabled(self):
        if not MODULES_IMPORTED:
            self.skipTest("bsb_jev not implemented yet")
        # Ensure disabled
        bsb_jev.configure_gateway(self.root, enabled=False)

        # Antigravity tool call
        call = {
            "toolCall": {
                "name": "write_to_file",
                "args": {"TargetFile": str(self.root / "wiki" / "concepts" / "test.md")}
            },
            "workspacePaths": [str(self.root)]
        }
        resp = bsb_jev_hook.evaluate_tool_call(call, host="antigravity", repo_root=self.root)
        self.assertEqual(resp, {})

    def test_antigravity_hook_blocks_wiki_and_raw_edits(self):
        if not MODULES_IMPORTED:
            self.skipTest("bsb_jev not implemented yet")
        bsb_jev.configure_gateway(self.root, enabled=True)

        # Block write_to_file in wiki
        call1 = {
            "toolCall": {
                "name": "write_to_file",
                "args": {"TargetFile": str(self.root / "wiki" / "concepts" / "direct.md")}
            },
            "workspacePaths": [str(self.root)]
        }
        resp1 = bsb_jev_hook.evaluate_tool_call(call1, host="antigravity", repo_root=self.root)
        self.assertEqual(resp1.get("decision"), "deny")
        self.assertIn("gateway", resp1.get("reason", "").lower())

        # Block replace_file_content in raw
        call2 = {
            "toolCall": {
                "name": "replace_file_content",
                "args": {"TargetFile": str(self.root / "raw" / "source.txt")}
            },
            "workspacePaths": [str(self.root)]
        }
        resp2 = bsb_jev_hook.evaluate_tool_call(call2, host="antigravity", repo_root=self.root)
        self.assertEqual(resp2.get("decision"), "deny")

    def test_antigravity_hook_allows_view_file(self):
        if not MODULES_IMPORTED:
            self.skipTest("bsb_jev not implemented yet")
        bsb_jev.configure_gateway(self.root, enabled=True)

        # view_file must be allowed (neutral {})
        call = {
            "toolCall": {
                "name": "view_file",
                "args": {"AbsolutePath": str(self.root / "wiki" / "concepts" / "page.md")}
            },
            "workspacePaths": [str(self.root)]
        }
        resp = bsb_jev_hook.evaluate_tool_call(call, host="antigravity", repo_root=self.root)
        self.assertEqual(resp, {})

    def test_claude_hook_format(self):
        if not MODULES_IMPORTED:
            self.skipTest("bsb_jev not implemented yet")
        bsb_jev.configure_gateway(self.root, enabled=True)

        call = {
            "tool_name": "Edit",
            "tool_input": {"file_path": str(self.root / "wiki" / "concepts" / "direct.md")},
            "cwd": str(self.root)
        }
        resp = bsb_jev_hook.evaluate_tool_call(call, host="claude", repo_root=self.root)
        self.assertIn("hookSpecificOutput", resp)
        self.assertEqual(resp["hookSpecificOutput"]["permissionDecision"], "deny")


class TestHookInstallerMerging(unittest.TestCase):
    """Test installer merges hook configs while preserving existing unrelated keys."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="bsb_jev_install_")
        self.root = Path(self.test_dir)
        (self.root / "CLAUDE.md").write_text("# Schema\n", encoding="utf-8")

        # Create existing .agents/hooks.json with existing custom hook
        agents_dir = self.root / ".agents"
        agents_dir.mkdir()
        (agents_dir / "hooks.json").write_text(json.dumps({
            "existing-tool": {
                "PreToolUse": [{"matcher": "other_tool", "hooks": [{"command": "echo hello"}]}]
            }
        }, indent=2), encoding="utf-8")

        # Create existing .claude/settings.json with existing custom setting
        claude_dir = self.root / ".claude"
        claude_dir.mkdir()
        (claude_dir / "settings.json").write_text(json.dumps({
            "customSetting": True,
            "hooks": {
                "PreToolUse": [{"command": "echo existing-claude-hook"}]
            }
        }, indent=2), encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_merge_and_uninstall(self):
        if not MODULES_IMPORTED:
            self.skipTest("bsb_jev not implemented yet")
        # Install hooks
        bsb_jev.configure_gateway(self.root, install_hooks=True)

        # Check .agents/hooks.json
        agents_hooks = json.loads((self.root / ".agents" / "hooks.json").read_text(encoding="utf-8"))
        self.assertIn("existing-tool", agents_hooks)
        self.assertIn("bsb-jev", agents_hooks)

        # Check .claude/settings.json
        claude_settings = json.loads((self.root / ".claude" / "settings.json").read_text(encoding="utf-8"))
        self.assertTrue(claude_settings.get("customSetting"))
        claude_hooks = claude_settings.get("hooks", {}).get("PreToolUse", [])
        self.assertTrue(any("bsb_jev_hook" in str(h.get("hooks")) for h in claude_hooks))
        self.assertTrue(any("existing-claude-hook" in str(h.get("command")) for h in claude_hooks))

        # Uninstall hooks
        bsb_jev.configure_gateway(self.root, uninstall_hooks=True)
        agents_hooks_after = json.loads((self.root / ".agents" / "hooks.json").read_text(encoding="utf-8"))
        self.assertIn("existing-tool", agents_hooks_after)
        self.assertNotIn("bsb-jev", agents_hooks_after)

        claude_settings_after = json.loads((self.root / ".claude" / "settings.json").read_text(encoding="utf-8"))
        self.assertTrue(claude_settings_after.get("customSetting"))
        claude_hooks_after = claude_settings_after.get("hooks", {}).get("PreToolUse", [])
        self.assertFalse(any("bsb_jev_hook" in str(h.get("hooks")) for h in claude_hooks_after))
        self.assertTrue(any("existing-claude-hook" in str(h.get("command")) for h in claude_hooks_after))


class TestInitBrainJevIntegration(unittest.TestCase):
    """Test init_brain.py --jev on/off installer integration."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="bsb_jev_init_")
        self.root = Path(self.test_dir)
        (self.root / "CLAUDE.md").write_text("# Schema\n\n**Domain (this instance):** x\n**Litmus:** x\n", encoding="utf-8")
        (self.root / "bsb.config.md").write_text("# Config\n\nDOMAIN: x\nLITMUS: x\n\n| link-style | `full-path` |\n", encoding="utf-8")
        (self.root / "wiki").mkdir()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_init_brain_with_jev_on(self):
        from scripts.init_brain import main as init_main
        ret = init_main(["--root", str(self.root), "--jev", "on", "--yes"])
        self.assertEqual(ret, 0)
        self.assertTrue(bsb_jev.is_enabled(self.root))
        # Hooks should be installed
        self.assertTrue((self.root / ".agents" / "hooks.json").is_file())
        self.assertTrue((self.root / ".claude" / "settings.json").is_file())

    def test_init_brain_with_jev_off_default(self):
        from scripts.init_brain import main as init_main
        ret = init_main(["--root", str(self.root), "--yes"])
        self.assertEqual(ret, 0)
        self.assertFalse(bsb_jev.is_enabled(self.root))


class TestCodexHooksAndRollbackProtection(unittest.TestCase):
    """Test Codex hooks, rollback protection against subsequent edits, and tampered plan detection."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="bsb_jev_codex_")
        self.root = Path(self.test_dir)
        (self.root / "CLAUDE.md").write_text("# Schema\n", encoding="utf-8")
        (self.root / "wiki").mkdir()
        (self.root / 'wiki/sources').mkdir()
        (self.root / 'wiki/sources/s.md').write_text('Local test evidence for Init.',encoding='utf-8')

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_codex_hook_apply_patch_denied(self):
        bsb_jev.configure_gateway(self.root, enabled=True)
        call = {
            "tool_name": "apply_patch",
            "tool_input": {"patch": "*** wiki/concepts/foo.md\n--- a/wiki/concepts/foo.md\n+++ b/wiki/concepts/foo.md\n"}
        }
        resp = bsb_jev_hook.evaluate_tool_call(call, host="codex", repo_root=self.root)
        self.assertIn("hookSpecificOutput", resp)
        self.assertEqual(resp["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_codex_hooks_installer_merge(self):
        bsb_jev.configure_gateway(self.root, install_hooks=True)
        codex_path = self.root / ".codex" / "hooks.json"
        self.assertTrue(codex_path.is_file())
        data = json.loads(codex_path.read_text(encoding="utf-8"))
        self.assertIn("PreToolUse", data.get("hooks", {}))

    def test_rollback_refuses_when_subsequent_edits_exist(self):
        new_path = "wiki/concepts/page-roll.md"
        request = {
            "mutations": [
                {
                    "action": "insert",
                    "path": new_path,
                    "content": "---\ntype: concept\ntitle: Roll\n---\nInit ([[wiki/sources/s]])\n",
                    "citations": ["wiki/sources/s"]
                }
            ]
        }
        plan = bsb_jev.create_plan(request, repo_root=self.root)
        bsb_jev.apply_plan(plan, repo_root=self.root, approve=True)

        # Tamper / subsequent edit on disk
        (self.root / new_path).write_text("Subsequent edit occurred!", encoding="utf-8")

        # Rollback should refuse
        with self.assertRaises(ValueError) as ctx:
            bsb_jev.rollback_plan(plan["plan_id"], repo_root=self.root)
        self.assertIn("subsequent", str(ctx.exception).lower())

    def test_tampered_plan_detected_at_apply(self):
        new_path = "wiki/concepts/page-tamper.md"
        request = {
            "mutations": [
                {
                    "action": "insert",
                    "path": new_path,
                    "content": "---\ntype: concept\ntitle: Tamper\n---\nInit ([[wiki/sources/s]])\n",
                    "citations": ["wiki/sources/s"]
                }
            ]
        }
        plan = bsb_jev.create_plan(request, repo_root=self.root)
        # Tamper the plan content
        plan["mutations"][0]["content"] = "Hacked content without new signature!"

        with self.assertRaises(ValueError) as ctx:
            bsb_jev.apply_plan(plan, repo_root=self.root, approve=True)
        self.assertIn("tamper", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()
