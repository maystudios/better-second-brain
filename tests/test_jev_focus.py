import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import bsb_jev
from scripts import bsb_jev_focus


CHOICES = ["direct", "partial", "contrary", "none", "unknown"]


class FocusPlannerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="bsb_focus_")
        self.root = Path(self.tmp.name)
        (self.root / "wiki").mkdir()
        (self.root / "CLAUDE.md").write_text("# test brain\n", encoding="utf-8")
        (self.root / "bsb.config.md").write_text("# config\n", encoding="utf-8")
        self.set_enabled(False)

    def tearDown(self):
        self.tmp.cleanup()

    def set_enabled(self, enabled):
        state = self.root / ".bsb-jev"
        state.mkdir(exist_ok=True)
        (state / "config.json").write_text(
            json.dumps(
                {
                    "enabled": bool(enabled),
                    "search_roots": ["wiki"],
                    "model": bsb_jev.DEFAULT_MODEL,
                    "timeout": 1.0,
                }
            ),
            encoding="utf-8",
        )

    def add_doc(self, name, text, title=None):
        if title:
            text = f"---\ntitle: {title}\n---\n{text}"
        path = self.root / "wiki" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def response_for(self, payload, classifier):
        answers = {}
        docs = payload["state"]["documents"]
        needs = payload["state"]["needs"]
        for qid, question in payload["questions"].items():
            doc_id, need_id = qid.rsplit(":", 1)
            choice = classifier(docs[doc_id]["text"], needs[need_id]["text"], doc_id, need_id)
            probabilities = {item: 0.0 for item in CHOICES}
            probabilities[choice] = 1.0
            answers[qid] = {
                "type": "choice",
                "choice": choice,
                "confidence": 0.95,
                "probabilities": probabilities,
            }
        return {
            "model": bsb_jev.DEFAULT_MODEL,
            "answers": answers,
            "usage": {"input_tokens": 10, "output_tokens": len(answers)},
        }

    def test_exact_facet_beats_broad_decoy_and_lower_ranked_config_page_is_selected(self):
        self.add_doc(
            "overview.md",
            "Configuration settings are documented here. This broad overview mentions configuration many times.\n"
            * 4,
            title="Configuration Overview",
        )
        exact = self.add_doc(
            "database.md",
            "Database configuration\n\nThe connection pool timeout is 45 seconds and applies to idle connections.\n",
            title="Database Configuration",
        )
        self.set_enabled(True)
        calls = []

        def transport(payload, key, model, timeout):
            calls.append(payload)
            return self.response_for(
                payload,
                lambda text, need, *_: "direct" if "connection pool timeout" in text.lower() else "none",
            )

        plan = bsb_jev_focus.focus(
            "configuration",
            ["What is the connection pool timeout?"],
            repo_root=self.root,
            candidate_limit=2,
            transport=transport,
            api_key="test-key",
        )
        self.assertEqual(plan["status"], "recommended")
        self.assertEqual([item["path"] for item in plan["initial"]], ["wiki/database.md"])
        self.assertEqual(plan["outstanding_needs"], [])
        self.assertEqual(len(calls), 1)
        self.assertGreaterEqual(len(plan["excerpts"][0]["windows"]), 1)
        self.assertEqual(plan["excerpts"][1]["hash"], hashlib.sha256(exact.read_bytes()).hexdigest())

    def test_supported_question_fields_carry_doc_and_need_reference(self):
        self.add_doc("one.md", "topic one\n")
        self.add_doc("two.md", "topic two\n")
        self.set_enabled(True)
        payloads = []

        def transport(payload, key, model, timeout):
            payloads.append(payload)
            return self.response_for(payload, lambda *_: "unknown")

        bsb_jev_focus.focus(
            "topic",
            ["What is one?", "What is two?"],
            repo_root=self.root,
            candidate_limit=2,
            transport=transport,
            api_key="test-key",
        )
        self.assertEqual(len(payloads), 1)
        questions = payloads[0]["questions"]
        self.assertEqual(set(questions), {"c1:n1", "c1:n2", "c2:n1", "c2:n2"})
        for question_id, question in questions.items():
            self.assertEqual(set(question), {"type", "instructions", "criteria"})
            doc_id, need_id = question_id.split(":")
            self.assertIn(f"document id {doc_id}", question["instructions"])
            self.assertIn(f"need id {need_id}", question["instructions"])

    def test_packets_are_bounded_and_redact_linked_paths(self):
        self.add_doc("one.md", "topic evidence [[wiki/linked-page]] and raw/private.md\n")
        self.set_enabled(True)
        seen = []

        def transport(payload, key, model, timeout):
            encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            seen.append((payload, encoded))
            return self.response_for(payload, lambda *_: "unknown")

        bsb_jev_focus.focus(
            "topic",
            ["Which topic setting is documented?"],
            repo_root=self.root,
            transport=transport,
            api_key="test-key",
        )
        self.assertTrue(seen)
        for payload, encoded in seen:
            self.assertLessEqual(len(encoded), bsb_jev.MAX_PAYLOAD_SIZE_BYTES)
            serialized = encoded.decode("utf-8")
            self.assertNotIn("wiki/linked-page", serialized)
            self.assertNotIn("raw/private.md", serialized)

    def test_complementary_pages_cover_two_needs(self):
        self.add_doc("auth.md", "Authentication uses an expiring session token.\n")
        self.add_doc("storage.md", "Storage uses encrypted object retention.\n")
        self.set_enabled(True)

        def transport(payload, key, model, timeout):
            return self.response_for(
                payload,
                lambda text, need, *_: (
                    "direct"
                    if ("authentication" in need.lower() and "authentication" in text.lower())
                    or ("storage" in need.lower() and "storage" in text.lower())
                    else "none"
                ),
            )

        plan = bsb_jev_focus.focus(
            "authentication storage",
            ["How does authentication work?", "How does storage work?"],
            repo_root=self.root,
            candidate_limit=2,
            transport=transport,
            api_key="test-key",
        )
        self.assertEqual({item["path"] for item in plan["initial"]}, {"wiki/auth.md", "wiki/storage.md"})
        self.assertEqual(plan["outstanding_needs"], [])

    def test_all_contrary_evidence_is_initial(self):
        self.add_doc("support.md", "The service uses a short session timeout.\n")
        self.add_doc("contrary.md", "Contrary evidence: the service uses no session timeout.\n")
        self.set_enabled(True)

        def transport(payload, key, model, timeout):
            return self.response_for(
                payload,
                lambda text, need, *_: "contrary" if "contrary" in text.lower() else "direct",
            )

        plan = bsb_jev_focus.focus(
            "session timeout",
            ["What is the session timeout?"],
            repo_root=self.root,
            candidate_limit=2,
            transport=transport,
            api_key="test-key",
        )
        initial = {item["path"] for item in plan["initial"]}
        self.assertEqual(initial, {"wiki/support.md", "wiki/contrary.md"})
        self.assertTrue(plan["provisional_coverage"]["n1"]["contrary"])

    def test_direct_candidate_is_not_deferred_behind_selected_partial_page(self):
        self.add_doc("conflict.md", "topic context with a partial answer and contradiction.")
        self.add_doc("exact.md", "topic exact setting value 42.")
        self.set_enabled(True)

        def transport(payload, key, model, timeout):
            answers = {}
            for qid in payload["questions"]:
                document_id, need_id = qid.rsplit(":", 1)
                if document_id == "c1" and need_id == "n1":
                    choice = "partial"
                elif document_id == "c1" and need_id == "n2":
                    choice = "contrary"
                elif document_id == "c2" and need_id == "n1":
                    choice = "direct"
                else:
                    choice = "none"
                probabilities = {item: 0.0 for item in CHOICES}
                probabilities[choice] = 1.0
                answers[qid] = {"type": "choice", "choice": choice, "confidence": 0.9, "probabilities": probabilities}
            return {"model": bsb_jev.DEFAULT_MODEL, "answers": answers, "usage": {"input_tokens": 1, "output_tokens": 1}}

        plan = bsb_jev_focus.focus(
            "topic", ["What is the exact setting?", "What conflicts?"],
            repo_root=self.root, candidate_limit=2, transport=transport, api_key="test-key",
        )
        self.assertIn("wiki/exact.md", {item["path"] for item in plan["initial"]})
        self.assertEqual(plan["provisional_coverage"]["n1"]["status"], "covered_provisionally")

    def test_unknown_evidence_reports_gap_and_next_read_reaches_deferred_page(self):
        self.add_doc("maybe.md", "This page mentions the topic but does not answer the subquestion.\n")
        self.add_doc("later.md", "Another page mentions the topic without the exact setting.\n")
        self.set_enabled(True)

        def transport(payload, key, model, timeout):
            return self.response_for(payload, lambda *_: "unknown")

        plan = bsb_jev_focus.focus(
            "topic",
            ["What exact setting controls the topic?"],
            repo_root=self.root,
            candidate_limit=2,
            transport=transport,
            api_key="test-key",
        )
        self.assertEqual([item["id"] for item in plan["initial"]], ["c1"])
        self.assertEqual(plan["outstanding_needs"], ["What exact setting controls the topic?"])
        offered = bsb_jev_focus.next_read(plan, ["c1"], missing_needs=["What exact setting controls the topic?"])
        self.assertEqual([item["id"] for item in offered], ["c2"])

    def test_disabled_and_dry_run_do_not_load_key_or_call_transport(self):
        self.add_doc("page.md", "A small page about topic.\n")
        transport = unittest.mock.Mock(side_effect=AssertionError("transport must not be used"))
        with patch.object(bsb_jev, "load_api_key", side_effect=AssertionError("key must not be loaded")):
            disabled = bsb_jev_focus.focus("topic", ["What is topic?"], repo_root=self.root, transport=transport)
            self.set_enabled(True)
            dry = bsb_jev_focus.focus(
                "topic", ["What is topic?"], repo_root=self.root, dry_run=True, transport=transport
            )
        self.assertEqual(disabled["status"], "disabled")
        self.assertEqual(dry["status"], "dry_run")
        self.assertEqual(transport.call_count, 0)

    def test_later_batch_failure_falls_back_to_every_candidate(self):
        for index in range(16):
            self.add_doc(f"page-{index:02}.md", "topic detail " + ("x" * 1800) + "\n")
        self.set_enabled(True)
        calls = []

        def transport(payload, key, model, timeout):
            calls.append(payload)
            if len(calls) == 2:
                raise RuntimeError("simulated outage")
            return self.response_for(payload, lambda *_: "direct")

        plan = bsb_jev_focus.focus(
            "topic",
            ["What is the topic detail?"],
            repo_root=self.root,
            candidate_limit=16,
            transport=transport,
            api_key="test-key",
        )
        self.assertEqual(plan["status"], "fallback")
        self.assertEqual(len(plan["initial"]), 16)
        self.assertEqual(plan["deferred"], [])
        self.assertGreaterEqual(len(calls), 2)

    def test_next_read_rejects_unknown_or_modified_paths_and_oversized_requests(self):
        self.add_doc("page.md", "topic evidence\n")
        plan = bsb_jev_focus.focus("topic", ["What is topic?"], repo_root=self.root)
        with self.assertRaises(ValueError):
            bsb_jev_focus.next_read(plan, ["not-an-id"])
        tampered = json.loads(json.dumps(plan))
        tampered["candidate_catalog"][0]["path"] = "../outside.md"
        with self.assertRaises(ValueError):
            bsb_jev_focus.next_read(tampered, [])
        with self.assertRaises(ValueError):
            bsb_jev_focus.focus("x" * 4097, ["What is x?"], repo_root=self.root)
        with self.assertRaises(ValueError):
            bsb_jev_focus.focus("topic", ["q"] * 7, repo_root=self.root)

    def test_symlink_candidate_is_rejected_when_platform_allows_symlinks(self):
        target = self.add_doc("real.md", "topic evidence\n")
        link = self.root / "wiki" / "linked.md"
        try:
            link.symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation is unavailable")
        plan = bsb_jev_focus.focus(
            "topic",
            ["What is topic?"],
            repo_root=self.root,
            candidates=["wiki/linked.md"],
        )
        self.assertEqual(plan["status"], "fallback")
        self.assertEqual(plan["blocked_candidates"][0]["path"], "wiki/linked.md")

    def test_unreadable_candidate_returns_safe_fallback_instead_of_crashing(self):
        self.add_doc("good.md", "topic evidence\n")
        self.add_doc("secret.md", "-----BEGIN RSA PRIVATE KEY-----\nnot sent\n")
        plan = bsb_jev_focus.focus(
            "topic", ["What is topic?"], repo_root=self.root, candidate_limit=2,
            candidates=["wiki/good.md", "wiki/secret.md"],
        )
        self.assertEqual(plan["status"], "fallback")
        self.assertEqual([item["path"] for item in plan["initial"]], ["wiki/good.md"])
        self.assertEqual(plan["blocked_candidates"][0]["path"], "wiki/secret.md")

    def test_focus_cli_out_is_contained_and_non_destructive(self):
        self.add_doc("page.md", "topic evidence\n")
        target = self.root / "wiki" / "page.md"
        before = target.read_bytes()
        request = self.root / "request.json"
        request.write_text(json.dumps({"query": "topic", "needs": ["What is topic?"]}), encoding="utf-8")
        self.assertEqual(
            bsb_jev_focus.main([str(request), "--root", str(self.root), "--dry-run", "--out", "jev-focus.json"]),
            0,
        )
        self.assertEqual(target.read_bytes(), before)
        self.assertEqual(
            bsb_jev_focus.main([str(request), "--root", str(self.root), "--dry-run", "--out", "wiki/page.md"]),
            1,
        )


if __name__ == "__main__":
    unittest.main()
