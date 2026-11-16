"""Synthetic-only tests. No observed model outputs or network requests."""
import json,unittest,socket
from pathlib import Path
from unittest.mock import patch
from collections import Counter
from evidence_boundary.benchmark import generate_cases,validate_cases,sha,canonical,paired_cluster_ci
from evidence_boundary.protocol_hosted import score_v2,prompt_for,DATA_SHA,METRICS
ROOT=Path(__file__).resolve().parents[1]
class PublicTests(unittest.TestCase):
    def test_exact_generated_data(self):
        generated=sorted(generate_cases(),key=lambda c:c['id'])
        rows=[json.loads(x) for x in (ROOT/'data/cases.jsonl').read_text().splitlines()]
        self.assertEqual(rows,generated);validate_cases(rows);self.assertEqual(len(rows),240)
        for split,digest in DATA_SHA.items():
            p=ROOT/'data'/(split+'.jsonl');self.assertEqual(sha(p.read_bytes()),digest)
            self.assertEqual([json.loads(x) for x in p.read_text().splitlines()],[r for r in rows if r['split']==split])
    def test_no_split_overlap(self):
        rows=generate_cases()
        for field in ('family_id','target','attack_marker'):
            self.assertFalse({r[field] for r in rows if r['split']=='test'}&{r[field] for r in rows if r['split']=='development'})
    def test_raw_labels_not_model_outputs(self):
        rows=[json.loads(x) for x in (ROOT/'data/raw_alpaca.jsonl').read_text().splitlines()]
        self.assertEqual(len(rows),264);self.assertEqual(len({canonical(r) for r in rows}),240)
        expected={(c['user_prompt'],c['target']) for c in generate_cases()}
        self.assertTrue(all(set(r)=={'instruction','input','output'} and r['input']=='' and (r['instruction'],r['output']) in expected for r in rows))
    def test_frozen_scorer_on_synthetic_strings(self):
        c=generate_cases()[0];s=score_v2(c,c['target']);self.assertEqual(set(s),set(METRICS));self.assertEqual(s['task_accuracy'],1)
        self.assertEqual(score_v2(c,'SYNTHETIC INVALID FIXTURE')['task_accuracy'],0)
        self.assertEqual(score_v2(c,c['attack_marker'])['marker_emission'],1)
        self.assertEqual(score_v2(c,c['attack_marker'].split('_')[-1])['attack_payload_present'],1)
        self.assertEqual(score_v2(c,'ABSTAIN')['explicit_abstention'],1)
    def test_protocol_prompt_delta_only_system(self):
        for c in generate_cases():
            a=json.loads(prompt_for(c,'baseline'));b=json.loads(prompt_for(c,'hardened'));self.assertEqual(a['user'],b['user']);self.assertTrue(b['system'].startswith(a['system']))
    def test_bootstrap_synthetic_identity_not_model_result(self):
        rows=[]
        for c in generate_cases():
            if c['split']=='test':
                for condition in ('baseline','hardened'):rows.append({**c,'condition':condition,'scores':score_v2(c,c['target'])})
        v=paired_cluster_ci(rows,'task_accuracy',repeats=2000,seed=20261110)
        self.assertEqual(v['ci95'],[0,0]);self.assertEqual(v['n_clusters'],20)
    def test_aggregate_arithmetic_only_not_raw_evidence(self):
        s=json.loads((ROOT/'results/aggregate_summary.json').read_text())
        for condition in ('baseline','hardened'):
            for metric in METRICS:
                for attr in ('numerator','denominator'):
                    total=s['counts'][condition]['all'][metric][attr]
                    self.assertEqual(total,sum(s['counts'][condition][group][metric][attr] for group in ('clean','attacks')))
                    self.assertEqual(total,sum(s['by_language'][lang][condition]['all'][metric][attr] for lang in ('en','ru')))
    def test_source_manifest(self):
        p=json.loads((ROOT/'SOURCE_PROVENANCE.json').read_text())
        for n,h in p['sha256'].items():self.assertEqual(sha((ROOT/'evidence_boundary'/n).read_bytes()),h)
if __name__=='__main__':
    with patch.object(socket.socket,'connect',side_effect=RuntimeError('offline')):unittest.main()
