"""Validate an incoming research batch without modifying or publishing anything."""
import argparse
import json
import sys
from pathlib import Path
from build import read_json, validate_batch

sys.stdout.reconfigure(encoding='utf-8')
parser=argparse.ArgumentParser()
parser.add_argument('path',type=Path)
args=parser.parse_args()
try:
    batch=json.loads(args.path.read_text(encoding='utf-8'))
    sources={s['id']:s for s in read_json('data/sources.json')}
    validate_batch(batch,sources)
except (ValueError,KeyError,TypeError) as error:
    print(f'Invalid research batch: {error}',file=sys.stderr)
    sys.exit(1)
print(json.dumps({'valid':True,'topic':batch['topic'],'findings':len(batch['findings']),'publishing_status':batch['publishing_status']},ensure_ascii=False))
