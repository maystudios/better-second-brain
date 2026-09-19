"""Branch-search host contracts; synthetic events do not prove live interception."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts import bsb_jev_hook as hook
from scripts import init_brain, install_jev


class BranchHostContract(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'wiki').mkdir()
        (self.root / '.bsb-jev').mkdir()
        (self.root / '.bsb-jev/config.json').write_text(json.dumps({
            'enabled': True, 'enforce_reads': True, 'search_roots': ['wiki'],
        }), encoding='utf-8')

    def event(self, command, host='claude'):
        if host == 'antigravity':
            payload = {'toolCall': {'name': 'run_command', 'args': {'command': command}},
                       'workspacePaths': [str(self.root)]}
        else:
            payload = {'tool_name': 'Bash', 'tool_input': {'command': command},
                       'cwd': str(self.root)}
        return hook.evaluate_tool_call(payload, host=host, repo_root=self.root)

    def test_find_optional_needs_and_budgets_allowed_for_all_native_host_events(self):
        for host in ('claude', 'codex', 'antigravity'):
            for suffix in ('"Why delayed?"',
                           '"Why delayed?" --need "cause" --need "fix" --max-calls 7 --max-pages 3 --dry-run'):
                with self.subTest(host=host, suffix=suffix):
                    self.assertEqual(self.event('python scripts/bsb_jev.py find ' + suffix, host), {})

    def test_find_rejects_invalid_grammar_configuration_and_shell_injection(self):
        bad = ('', 'one two', 'topic --max-calls nope', 'topic --max-pages 1.5',
               'topic --max-calls -1', 'topic --max-pages 2 --max-pages 3',
               'topic --need', 'topic --enabled off', 'topic --root elsewhere',
               'topic --dry-run --dry-run', 'topic; type wiki/private.md',
               '"$(Get-Content wiki/private.md)"', '"`whoami`"')
        for suffix in bad:
            with self.subTest(suffix=suffix):
                result = self.event('python scripts/bsb_jev.py find ' + suffix)
                self.assertEqual(result.get('hookSpecificOutput', {}).get('permissionDecision'), 'deny')
        self.assertEqual(self.event('python scripts/bsb_jev.py find "topic; punctuation"'), {})

    def test_parser_rejects_expansion_even_in_an_existing_allowed_command(self):
        for suffix in ('"$(Get-Content wiki/private.md)"', '"`whoami`"'):
            with self.subTest(suffix=suffix):
                self.assertFalse(hook.is_allowed_gateway_command(
                    'python scripts/bsb_jev.py source ' + suffix, self.root))

    def test_search_module_is_protected_from_native_writes_and_patches(self):
        path = 'scripts/bsb_jev_search.py'
        for name, args in (('Write', {'file_path': path, 'content': 'tamper'}),
                           ('apply_patch', {'patch': '*** Begin Patch\n*** Delete File: ' + path + '\n*** End Patch'})):
            result = hook.evaluate_tool_call({'tool_name': name, 'tool_input': args},
                                            repo_root=self.root)
            self.assertEqual(result.get('hookSpecificOutput', {}).get('permissionDecision'), 'deny')

    def test_installer_copies_search_module_preserves_rules_and_runs_find_offline(self):
        original = 'Read index.md first. Preserve my source rules.\n'
        (self.root / 'CLAUDE.md').write_text(original, encoding='utf-8')
        result = install_jev.install(self.root, enabled=False)
        module = self.root / 'scripts/bsb_jev_search.py'
        self.assertTrue(module.is_file())
        self.assertEqual(result['hashes']['scripts/bsb_jev_search.py'],
                         hashlib.sha256(module.read_bytes()).hexdigest())
        rules = (self.root / 'CLAUDE.md').read_text(encoding='utf-8')
        self.assertTrue(rules.startswith(original))
        self.assertIn('bsb_jev.py find', rules)
        self.assertIn('index-first', rules)
        self.assertIn('full-page', rules)
        self.assertIn('unresolved', rules)
        process = subprocess.run([sys.executable, 'scripts/bsb_jev.py', 'find', 'test'],
                                 cwd=self.root, capture_output=True, text=True, timeout=15)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(json.loads(process.stdout)['status'], 'disabled')

    def test_first_run_explains_enabled_route_and_catalog_ownership(self):
        text = init_brain.first_run('software', None, ['jev'], '2026-09-19')
        self.assertIn('bsb_jev.py find', text)
        self.assertIn('full-page', text)
        self.assertIn('unresolved', text)
        self.assertIn('gateway', init_brain.fresh_index('software', '2026-09-19'))


if __name__ == '__main__':
    unittest.main()
