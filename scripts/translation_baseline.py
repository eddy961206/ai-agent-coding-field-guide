"""Track which Korean source revision was reviewed for each English translation."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]

def fingerprint(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest()

def expected_baseline(root):
    result={'schema_version':1,'sources':{},'methods':{},'recipes':{},'prompts':{},'templates':{}}
    sources=json.loads((root/'data/sources.json').read_text(encoding='utf-8'))
    for source in sources:
        result['sources'][source['id']]=fingerprint({k:source.get(k) for k in ('title','evidence','date_basis','review_scope','takeaway','author','category')})
    for name in ('methods','recipes','prompts'):
        records=json.loads((root/f'data/{name}.json').read_text(encoding='utf-8'))
        result[name]={record['id']:fingerprint(record) for record in records}
    for path in [root/'src/intro.html',root/'src/outro.html',*sorted((root/'src/sections').glob('*.html'))]:
        result['templates'][path.relative_to(root).as_posix()]=fingerprint(path.read_text(encoding='utf-8'))
    result['ui']=fingerprint(json.loads((root/'data/ui.json').read_text(encoding='utf-8')))
    return result

def check_baseline(root):
    path=root/'data/en/translation-baseline.json'
    if not path.is_file():raise ValueError('Missing reviewed English translation baseline')
    actual=json.loads(path.read_text(encoding='utf-8'))
    expected=expected_baseline(root)
    changed=[]
    for group in ('sources','methods','recipes','prompts','templates'):
        keys=set(expected[group])|set(actual.get(group,{}))
        changed.extend(group+'/'+key for key in sorted(keys) if expected[group].get(key)!=actual.get(group,{}).get(key))
    if expected['ui']!=actual.get('ui'):changed.append('ui')
    if changed:raise ValueError('English translation review required: '+', '.join(changed))

def reject_untranslated_copy(original,translated,fields):
    for key in fields:
        value=original.get(key)
        if isinstance(value,str) and re.search('[가-힣]',value) and translated.get(key)==value:
            raise ValueError(f'Untranslated English field: {original["id"]}.{key}')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--record-reviewed',action='store_true',help='Record the current Korean baseline only after reviewing/updating the English counterparts')
    args=parser.parse_args()
    if args.record_reviewed:
        (ROOT/'data/en/translation-baseline.json').write_text(json.dumps(expected_baseline(ROOT),ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
        print('Recorded the explicitly reviewed Korean revision baseline for English translations')
    else:
        try:check_baseline(ROOT)
        except ValueError as error:
            print(error,file=sys.stderr);sys.exit(1)
        print('English translation baseline is current')
