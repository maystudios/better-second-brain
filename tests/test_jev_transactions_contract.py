"""Independent data-preservation checks using only synthetic local evidence."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import bsb_jev as b


class TransactionContract(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        (self.root/'CLAUDE.md').write_text('Synthetic schema')
        (self.root/'wiki').mkdir();(self.root/'raw').mkdir()
        (self.root/'raw/source.md').write_bytes(b'Synthetic note states that blue is a color.\n')
    def request(self,name='wiki/note.md',content='Blue is a color.\n[[raw/source]]\n'):
        return {'mutations':[{'action':'insert','path':name,'content':content,'citations':['raw/source.md']}]}
    def delete_plan(self):
        p=self.root/'wiki/old.md';p.write_bytes(b'Old synthetic note\n')
        return b.create_plan({'mutations':[{'action':'delete','path':'wiki/old.md','base_hash':hashlib.sha256(p.read_bytes()).hexdigest()}]},self.root)

    def test_windows_newline_roundtrip_exact_bytes(self):
        request=self.request(content='Unicode: München “quoted” 🧠\r\n[[raw/source]]\r\n')
        plan=b.create_plan(request,self.root)
        b.apply_plan(plan,self.root,approve=True)
        self.assertEqual((self.root/'wiki/note.md').read_bytes(),request['mutations'][0]['content'].encode())
        b.rollback_plan(plan['plan_id'],self.root)
        self.assertFalse((self.root/'wiki/note.md').exists())

    def test_rollback_never_overwrites_recreated_deleted_file(self):
        plan=self.delete_plan();b.apply_plan(plan,self.root,approve=True)
        target=self.root/'wiki/old.md';target.write_bytes(b'New user work')
        with self.assertRaises((ValueError,RuntimeError)):b.rollback_plan(plan['plan_id'],self.root)
        self.assertEqual(target.read_bytes(),b'New user work')

    def test_duplicate_paths_rejected_before_any_write(self):
        request=self.request();request['mutations']*=2
        with self.assertRaises(ValueError):b.create_plan(request,self.root)
        self.assertFalse((self.root/'wiki/note.md').exists())

    def test_unsigned_plan_cannot_bypass_enabled_consultation(self):
        b.configure_gateway(self.root,enabled=True)
        forged={'plan_id':'plan-fake','mutations':self.request()['mutations']}
        with self.assertRaises((ValueError,RuntimeError,FileNotFoundError)):b.apply_plan(forged,self.root,approve=True)
        self.assertFalse((self.root/'wiki/note.md').exists())

    def test_offline_plan_is_not_accepted_after_enabling(self):
        plan=b.create_plan(self.request(),self.root)
        b.configure_gateway(self.root,enabled=True)
        with patch.object(b,'load_api_key',return_value=None):
            with self.assertRaises((ValueError,RuntimeError)):b.apply_plan(plan,self.root,approve=True)
        self.assertFalse((self.root/'wiki/note.md').exists())

    def test_dry_run_never_decrypts_or_calls_network(self):
        b.configure_gateway(self.root,enabled=True)
        with patch.object(b,'load_api_key',side_effect=AssertionError('key loaded')):
            result=b.create_plan(self.request(),self.root,dry_run=True,transport=lambda *a: (_ for _ in ()).throw(AssertionError('network')))
        self.assertFalse((self.root/'.bsb-jev/plans').exists())
        self.assertFalse((self.root/'wiki/note.md').exists())

    def test_index_reference_prevents_delete(self):
        (self.root/'index.md').write_text('[[wiki/old]]')
        with self.assertRaises(ValueError):self.delete_plan()

    def test_evidence_change_prevents_stale_apply(self):
        plan=b.create_plan(self.request(),self.root)
        (self.root/'raw/source.md').write_bytes(b'Different evidence\n')
        with self.assertRaises((ValueError,RuntimeError)):b.apply_plan(plan,self.root,approve=True)
        self.assertFalse((self.root/'wiki/note.md').exists())

    def test_mid_transaction_failure_restores_all_original_bytes(self):
        names=['wiki/one.md','wiki/two.md'];old=b'Original\r\n'
        for name in names:(self.root/name).write_bytes(old)
        request={'mutations':[{'action':'edit','path':name,'base_hash':hashlib.sha256(old).hexdigest(),'content':'Changed\n','citations':['raw/source.md']} for name in names]}
        plan=b.create_plan(request,self.root);atomic=b._atomic;failed=False
        def fail_once(path,data):
            nonlocal failed
            if path==self.root/names[1] and not failed:
                failed=True;raise OSError('synthetic disk failure')
            return atomic(path,data)
        with patch.object(b,'_atomic',side_effect=fail_once):
            with self.assertRaisesRegex(RuntimeError,'rollback completed'):b.apply_plan(plan,self.root,approve=True)
        for name in names:self.assertEqual((self.root/name).read_bytes(),old)

    def test_apply_dry_run_checks_but_never_changes_notes(self):
        plan=b.create_plan(self.request(),self.root)
        out=b.apply_plan(plan,self.root,approve=True,dry_run=True)
        self.assertEqual(out['status'],'dry_run')
        self.assertFalse((self.root/'wiki/note.md').exists())
        self.assertFalse((self.root/'.bsb-jev/backups'/plan['plan_id']).exists())

if __name__=='__main__':unittest.main()
