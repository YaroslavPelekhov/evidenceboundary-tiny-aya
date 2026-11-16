"""Optional dependency integration test. Exports only into temporary storage."""
import importlib.util,json,tempfile,unittest,socket
from pathlib import Path
from evidence_boundary.auditkit_smoke import run_smoke,network_disabled
from evidence_boundary.protocol_hosted import score_v2,METRICS
@unittest.skipUnless(importlib.util.find_spec('auditkit'),'Optional auditkit dependency not installed')
class AuditSmokeTests(unittest.TestCase):
    def test_native_fixture_scores_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d,network_disabled():
            p=Path(d)/'new-fixture-output';m=run_smoke(p)
            self.assertEqual(m['model_observations'],0);self.assertFalse(m['historical_evidence'])
            rows=[json.loads(x) for x in (p/'fixture_rows.jsonl').read_text().splitlines()];native=json.loads((p/'fixture_auditkit.json').read_text())
            self.assertEqual(len(rows),20);self.assertEqual(len(native['predictions']),20)
            lookup={r['id']+'::'+r['condition']:r for r in rows}
            for pred in native['predictions']:
                r=lookup[pred['sample_id']];self.assertTrue(r['is_fixture']);self.assertEqual(pred['raw_output'],r['target']);self.assertEqual({s['name']:s['value'] for s in pred['metadata']['scores']},score_v2(r,r['target']))
            before={x.name:x.read_bytes() for x in p.iterdir()}
            with self.assertRaises(FileExistsError):run_smoke(p)
            self.assertEqual(before,{x.name:x.read_bytes() for x in p.iterdir()})
    def test_network_guard(self):
        with network_disabled(),self.assertRaisesRegex(RuntimeError,'Network disabled'):socket.create_connection(('example.invalid',443))
