import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from install_jev import install


class ExistingBrainInstall(unittest.TestCase):
    def test_install_preserves_notes_rules_and_backups_then_disables(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'wiki').mkdir();(root/'raw').mkdir()
            preserved={'wiki/person.md':b'Private alias [[Title Case]]\r\n','raw/source.md':b'Original immutable evidence\r\n','log.md':b'Past entry\r\n'}
            for name,data in preserved.items():(root/name).write_bytes(data)
            schema='Domain: personal. Links [[Title Case]]. No web-source floor.\n'
            (root/'CLAUDE.md').write_text(schema,encoding='utf-8',newline='')
            old_script=root/'scripts/bsb_jev.py';old_script.parent.mkdir();old_script.write_bytes(b'previous local helper\n')
            manifest=install(root,enabled=True,hooks=True)
            for name,data in preserved.items():self.assertEqual((root/name).read_bytes(),data)
            self.assertTrue((root/'CLAUDE.md').read_text().startswith(schema))
            self.assertEqual((Path(manifest['backups'])/'scripts/bsb_jev.py').read_bytes(),b'previous local helper\n')
            self.assertEqual(json.loads((root/'.bsb-jev/config.json').read_text())['enabled'],True)
            install(root,enabled=False)
            self.assertEqual((root/'CLAUDE.md').read_text().count('<!-- bsb-jev:start -->'),1)
            self.assertEqual(json.loads((root/'.bsb-jev/config.json').read_text())['enabled'],False)
            for name,data in preserved.items():self.assertEqual((root/name).read_bytes(),data)

    def test_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'wiki').mkdir()
            before=list(root.rglob('*'))
            result=install(root,dry_run=True)
            self.assertEqual(result['status'],'dry_run')
            self.assertEqual(list(root.rglob('*')),before)

if __name__=='__main__':unittest.main()
