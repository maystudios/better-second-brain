import json
import shutil
import subprocess
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import bsb_jev
import bsb_jev_hook as hook


class HostContract(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'CLAUDE.md').write_text('schema')

    def test_host_configs_use_nested_handlers_and_are_idempotent(self):
        hook.install_hooks_configs(self.root)
        first = {p: p.read_bytes() for p in [self.root/'.claude/settings.json', self.root/'.codex/hooks.json', self.root/'.agents/hooks.json']}
        hook.install_hooks_configs(self.root)
        for p, data in first.items():
            self.assertEqual(p.read_bytes(), data)
            parsed = json.loads(data)
            events = parsed['bsb-jev'] if p.parent.name == '.agents' else parsed['hooks']
            for group in events['PreToolUse']:
                self.assertIsInstance(group.get('hooks'), list)
                command = group['hooks'][0]['command']
                if p.parent.name == '.agents':
                    self.assertIn('../scripts/bsb_jev_hook.py',command)
                    self.assertNotIn('"',command)
                else:
                    self.assertIn('--root', command)
                    self.assertIn(str(self.root).replace('\\','/'), command)

    def test_unrelated_hooks_preserved_and_corrupt_file_not_overwritten(self):
        p=self.root/'.claude/settings.json';p.parent.mkdir()
        existing={'hooks':{'PreToolUse':[{'matcher':'Read','hooks':[{'type':'command','command':'other.py'}]}]},'permissions':{'deny':['Bash(rm *)']}}
        p.write_text(json.dumps(existing))
        hook.install_hooks_configs(self.root)
        hook.uninstall_hooks_configs(self.root)
        self.assertEqual(json.loads(p.read_text()),existing)
        p.write_text('broken')
        before=(self.root/'.agents/hooks.json').read_bytes()
        with self.assertRaises(ValueError): hook.install_hooks_configs(self.root)
        self.assertEqual(p.read_text(),'broken')
        self.assertEqual((self.root/'.agents/hooks.json').read_bytes(),before)

    def test_search_root_and_default_path_cannot_skip_gateway(self):
        bsb_jev.configure_gateway(self.root,enabled=True)
        for args in ({'pattern':'query'}, {'pattern':'query','path':'.'}):
            result=hook.evaluate_tool_call({'tool_name':'Grep','tool_input':args},repo_root=self.root)
            self.assertEqual(result.get('hookSpecificOutput',{}).get('permissionDecision'),'deny')

    def test_codex_real_patch_headers_and_moves_are_blocked(self):
        bsb_jev.configure_gateway(self.root,enabled=True)
        for header in ['*** Add File: wiki/new.md', '*** Update File: wiki/page.md',
                       '*** Delete File: wiki/page.md', '*** Move to: wiki/moved.md',
                       f'*** Update File: {self.root.as_posix()}/wiki/a page.md',
                       '*** Move from: wiki/protected.md', '*** Update File: "wiki/spaced title.md"']:
            patch='*** Begin Patch\n'+header+'\n+text\n*** End Patch'
            result=hook.evaluate_tool_call({'tool_name':'apply_patch','tool_input':{'command':patch}},host='codex',repo_root=self.root)
            with self.subTest(header=header):
                self.assertEqual(result.get('hookSpecificOutput',{}).get('permissionDecision'),'deny')

    def test_external_and_nonwiki_paths_are_not_intercepted(self):
        for name in [str(self.root.parent/'other-project/raw/x.md'),str(self.root.parent/'other-project/index.md'),'docs/index.md']:
            self.assertFalse(hook.is_wiki_or_protected_path(name,self.root)[0])
        self.assertFalse(hook.is_wiki_search('wiki/../tests',self.root))

    def test_agy_hook_process_from_config_directory_with_spaces(self):
        root=self.root/'brain with spaces ü🧠';(root/'scripts').mkdir(parents=True)
        (root/'CLAUDE.md').write_text('synthetic schema')
        source=Path(__file__).resolve().parents[1]/'scripts'
        for name in ['bsb_jev.py','bsb_jev_hook.py']:
            shutil.copy2(source/name,root/'scripts'/name)
        bsb_jev.configure_gateway(root,enabled=True)
        hook.install_hooks_configs(root)
        payload={'toolCall':{'name':'write_to_file','args':{'TargetFile':str(root/'wiki/note.md')}}}
        proc=subprocess.run([sys.executable,'../scripts/bsb_jev_hook.py','--host','antigravity'],cwd=root/'.agents',input=json.dumps(payload,ensure_ascii=False).encode('utf-8'),capture_output=True,timeout=10)
        self.assertEqual(proc.returncode,0,proc.stderr)
        self.assertEqual(json.loads(proc.stdout)['decision'],'deny')

if __name__=='__main__': unittest.main()
