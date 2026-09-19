from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import bsb_jev
import init_brain


class InitModes(unittest.TestCase):
    def test_omitted_flag_preserves_enabled_but_explicit_off_disables(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'CLAUDE.md').write_text('schema');(root/'wiki').mkdir()
            bsb_jev.configure_gateway(root,enabled=True)
            init_brain.main(['--root',tmp,'--no-git'])
            self.assertTrue(bsb_jev.is_enabled(root))
            init_brain.main(['--root',tmp,'--no-git','--jev','off'])
            self.assertFalse(bsb_jev.is_enabled(root))
            bsb_jev.configure_gateway(root,enabled=True)
            init_brain.main(['--root',tmp,'--no-git','--fresh','--yes'])
            self.assertFalse(bsb_jev.is_enabled(root))

    def test_git_init_still_runs_and_dry_run_never_configures(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'CLAUDE.md').write_text('schema');(root/'wiki').mkdir()
            with patch.object(init_brain.subprocess,'run') as run:
                init_brain.main(['--root',tmp,'--jev','on','--dry-run'])
                run.assert_not_called()
                self.assertFalse((root/'.bsb-jev').exists())
                init_brain.main(['--root',tmp,'--jev','off'])
                self.assertEqual(run.call_args.args[0],['git','init','-b','main'])

if __name__=='__main__': unittest.main()
