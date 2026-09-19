import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts import bsb_jev as b


class RetrievalContract(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);(self.root/'wiki').mkdir()
        for i in range(7):(self.root/f'wiki/doc{i}.md').write_text('needle common evidence\n'*20,encoding='utf-8')
        (self.root/'wiki/rare.md').write_text('needle quokka distinctive source',encoding='utf-8')

    def answer(self,payload,*args):
        return {'model':b.DEFAULT_MODEL,'answers':{k:{'type':'choice','choice':'low','confidence':0.9,'probabilities':{'high':0.01,'medium':0.01,'unknown':0.08,'low':0.9}} for k in payload['questions']},'usage':{'input_tokens':12}}

    def test_default_retains_low_ranked_counterevidence_and_distinct_documents(self):
        b.configure_gateway(self.root,enabled=True)
        out=b.query('needle quokka',self.root,limit=2,transport=self.answer,api_key='test')
        self.assertEqual(out['status'],'recommended')
        self.assertEqual(len(out['selected']),8)
        self.assertEqual(len({x['path'] for x in out['selected']}),8)
        self.assertEqual(out['selected'][0]['path'],'wiki/rare.md')
        self.assertEqual(out['metrics']['deferred_bytes'],0)
        self.assertFalse(out['coverage']['global_absence_proven'])

    def test_disabled_and_dry_run_do_not_load_credentials_or_call_transport(self):
        with patch.object(b,'load_api_key',side_effect=AssertionError('credential read')):
            b.query('needle',self.root,transport=lambda *a:self.fail('network'))
            b.configure_gateway(self.root,enabled=True)
            b.query('needle',self.root,dry_run=True,transport=lambda *a:self.fail('network'))

    def test_missing_question_falls_back_without_pruning(self):
        b.configure_gateway(self.root,enabled=True)
        out=b.query('needle',self.root,limit=1,prune=True,transport=lambda *a:{'model':b.DEFAULT_MODEL,'answers':{}},api_key='test')
        self.assertEqual(out['status'],'fallback');self.assertEqual(len(out['selected']),8)

    def test_invalid_probability_and_usage_rejected(self):
        for probs,usage in [({'high':float('nan'),'low':1},None),({'high':-0.1,'low':1.1},None),({'high':1,'surprise':0},None),({'high':1,'low':0},{'input_tokens':-1}),({'high':'1','low':0},None)]:
            raw={'model':b.DEFAULT_MODEL,'answers':{'q':{'type':'choice','choice':'high','confidence':0.9,'probabilities':probs}},'usage':usage}
            with self.subTest(probs=probs),self.assertRaises(ValueError):b.validate_choice_response(raw,['high','low'])

    def test_bad_config_types_and_bounds_are_visible(self):
        p=self.root/'.bsb-jev/config.json';p.parent.mkdir()
        for fields in [{'enabled':'false'},{'timeout':-1},{'search_roots':['../outside']},{'model':False}]:
            p.write_text(json.dumps(fields))
            with self.subTest(fields=fields),self.assertRaises(ValueError):b.get_config(self.root)


if __name__=='__main__':unittest.main()
