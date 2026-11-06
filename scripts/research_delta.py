"""Classify incoming sources without changing the catalog or publishing."""
import argparse
import json
from pathlib import Path
import sys
from build import read_json, validate_batch
from source_identity import source_identity, source_keys

sys.stdout.reconfigure(encoding='utf-8')
parser=argparse.ArgumentParser()
parser.add_argument('path',type=Path)
args=parser.parse_args()
catalog=read_json('data/sources.json')
by_id={source['id']:source for source in catalog}
by_key={key:source for source in catalog for key in source_keys(source)}
batch=json.loads(args.path.read_text(encoding='utf-8'))
validate_batch(batch,by_id)
results=[]
seen=set()
for finding in batch['findings']:
    key=source_identity(finding['original_url'])
    existing=by_id.get(finding['source_id']) or by_key.get(key)
    status='duplicate_within_batch' if key in seen else 'existing_source_compare_claims' if existing else 'new_source_review_required'
    seen.add(key)
    results.append({'source_id':finding['source_id'],'identity':key,'status':status,'existing_source_id':existing['id'] if existing else None,'proposed_change_type':finding['change_type'],'original_url':finding['original_url']})
print(json.dumps({'schema_version':1,'topic':batch['topic'],'findings':results,'note':'Identity matching detects duplicate sources. It does not decide whether a claim is new, true or worth publishing.'},ensure_ascii=False,indent=2))
