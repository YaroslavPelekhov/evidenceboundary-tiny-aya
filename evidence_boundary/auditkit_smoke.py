"""New public offline integration smoke test, NOT historical model evidence.

Adapted from this project's AuditKIT pipeline. Uses generator-created target
labels as fixture responses. No model backend, service client or network call.
"""
from __future__ import annotations
import argparse
from contextlib import contextmanager
import json,socket
from pathlib import Path
from unittest.mock import patch
from .benchmark import generate_cases,canonical
from .protocol_hosted import score_v2,prompt_for,METRICS,SETTINGS

@contextmanager
def network_disabled():
    def denied(*args,**kwargs):raise RuntimeError('Network disabled: synthetic integration smoke test')
    with patch.object(socket.socket,'connect',denied),patch.object(socket.socket,'connect_ex',denied),patch.object(socket,'create_connection',denied),patch.object(socket,'getaddrinfo',denied):yield

def run_smoke(output:Path):
    output=output.resolve()
    if output.exists():raise FileExistsError('Choose a NEW local output directory; existing evidence is never overwritten')
    with network_disabled():
        import auditkit as ak
        from auditkit.model import CallableModel
        cases=[c for c in generate_cases() if c['family_id']=='F01']
        rows=[{**c,'condition':condition,'output':c['target'],'scores':score_v2(c,c['target']),'is_fixture':True,'is_model_evaluation':False} for c in cases for condition in ('baseline','hardened')]
        lookup={prompt_for(r,r['condition']):r['output'] for r in rows}
        samples=[ak.Sample(id=r['id']+'::'+r['condition'],input=prompt_for(r,r['condition']),target=r['target'],metadata=r) for r in rows]
        scorers=[]
        for metric in METRICS:
            def factory(name):
                def scorer(sample,answer):return score_v2(sample.metadata,answer)[name]
                scorer.__name__=name;return scorer
            scorers.append(ak.scorer(direction=ak.Direction.MINIMIZE if metric in ('marker_emission','explicit_abstention','attack_payload_present') else ak.Direction.MAXIMIZE)(factory(metric)))
        model=CallableModel(lambda prompts:[lookup[p] for p in prompts],name='SYNTHETIC-TARGET-LOOKUP-NOT-A-MODEL');model.threadsafe=False
        result=ak.evaluate(samples,model=model,scorers=scorers,config=ak.RunConfig(seed=SETTINGS['evaluation_seed'],batch_size=1,concurrency=1,max_retries=0,track_performance=False),cache=False)
        if result.errors or result.failed_count or len(result.predictions)!=20:raise RuntimeError('Incomplete smoke test')
        meta={'status':'SYNTHETIC_INTEGRATION_SMOKE_ONLY','historical_evidence':False,'model_observations':0,'fixture_predictions':20,'network_disabled':True,'warning':'New public integration test. Perfect target-lookup scores are not model performance.'}
        result.metadata['public_smoke']=meta
        output.mkdir(parents=True,exist_ok=False)
        result.save(str(output/'fixture_auditkit.json'))
        native=json.loads((output/'fixture_auditkit.json').read_text());expected={r['id']+'::'+r['condition']:r for r in rows};ids=[p['sample_id'] for p in native['predictions']]
        if len(ids)!=len(set(ids)) or set(ids)!=set(expected):raise RuntimeError('Native fixture coverage mismatch')
        for pred in native['predictions']:
            r=expected[pred['sample_id']];scores=pred['metadata']['scores']
            if pred['raw_output']!=r['output'] or len(scores)!=6 or {s['name'] for s in scores}!=set(METRICS) or {s['name']:s['value'] for s in scores}!=r['scores']:raise RuntimeError('Native fixture scores/output mismatch')
        (output/'fixture_rows.jsonl').write_text(''.join(canonical(r)+'\n' for r in rows))
        (output/'manifest.json').write_text(json.dumps(meta,indent=2)+'\n')
        return meta

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(run_smoke(a.output),indent=2))
