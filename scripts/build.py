"""Build a standalone HTML guide and agent-readable exports using the stdlib."""
import argparse
import datetime as dt
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlparse
from source_identity import source_identity, source_keys
from render import render_language
from translation_baseline import check_baseline, reject_untranslated_copy

ROOT = Path(__file__).resolve().parents[1]

def read_json(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))

def required_text(record, keys, context):
    for key in keys:
        if not isinstance(record.get(key), str) or not record[key].strip():
            raise ValueError(f'Expected nonempty string {key}: {context}')

def valid_date(value, context):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        raise ValueError(f'Expected ISO date: {context}')
    dt.date.fromisoformat(value)

EVIDENCE_KINDS = {'opinion','self_report','implementation','controlled_study','survey','curation','vendor_report'}

def validate_batch(batch, known_sources, historical=False):
    if batch.get('schema_version') != 1:
        raise ValueError('Unknown research batch schema_version')
    required_text(batch, ('topic','as_of','timezone','scope','publishing_status'), 'research batch')
    valid_date(batch['as_of'], 'batch as_of')
    if batch['publishing_status'] not in {'research_only','reviewed_for_publication','published'}:
        raise ValueError('Invalid publishing_status')
    if not isinstance(batch.get('findings'), list) or not batch['findings']:
        raise ValueError('Research batch requires findings')
    for field in ('counterevidence','access_gaps','next_questions'):
        if not isinstance(batch.get(field),list):
            raise ValueError(f'Expected batch list: {field}')
    ids=set()
    for finding in batch['findings']:
        required_text(finding, ('source_id','original_url','author','date_basis','checked_on','source_kind','evidence_kind','author_claim','editorial_takeaway','change_type'), 'batch finding')
        ident=finding['source_id']
        if ident in ids: raise ValueError(f'Duplicate batch source: {ident}')
        ids.add(ident)
        if finding['source_kind'] not in {'X','Reddit','GitHub','Web'} or finding['evidence_kind'] not in EVIDENCE_KINDS:
            raise ValueError(f'Invalid source/evidence kind: {ident}')
        if finding['change_type'] not in {'addition','correction','changed_view','applicability_change'}:
            raise ValueError(f'Invalid change_type: {ident}')
        valid_date(finding['checked_on'], ident+' checked_on')
        if 'published_on' not in finding: raise ValueError(f'Missing published_on: {ident}')
        if finding['published_on'] is not None:
            valid_date(finding['published_on'],ident+' published_on')
            if finding['published_on']>finding['checked_on']: raise ValueError(f'Publication after check: {ident}')
        if finding['checked_on']>batch['as_of']: raise ValueError(f'Check after batch date: {ident}')
        if urlparse(finding['original_url']).scheme!='https' or not urlparse(finding['original_url']).netloc:
            raise ValueError(f'Expected HTTPS original URL: {ident}')
        for field in ('limitations','related_source_ids'):
            if not isinstance(finding.get(field),list) or not all(isinstance(x,str) and x.strip() for x in finding[field]):
                raise ValueError(f'Invalid {field}: {ident}')
        if not historical and ident in known_sources and source_identity(finding['original_url']) not in source_keys(known_sources[ident]):
            raise ValueError(f'URL conflicts with catalog ID: {ident}')
    for finding in batch['findings']:
        unknown=set(finding['related_source_ids'])-set(known_sources)-ids
        if unknown: raise ValueError(f'Unknown related sources: {sorted(unknown)}')

def validate(sources, methods, recipes, prompts, site):
    required_text(site, ('title','edition','timezone','research_run','summary'), 'site')
    valid_date(site['edition'],'edition')
    run_path=(ROOT/site['research_run']).resolve()
    if not run_path.is_relative_to(ROOT.resolve()) or not run_path.is_file():
        raise ValueError('Invalid or missing research_run')
    ids = set()
    urls = set()
    identities = {}
    if not isinstance(sources,list) or not sources: raise ValueError('Expected nonempty source list')
    for source in sources:
        for key in ('id', 'kind', 'author', 'date', 'date_basis', 'url', 'title', 'category', 'checked', 'evidence', 'evidence_kind'):
            if key not in source:
                raise ValueError(f'Missing {key}: {source.get("id")}')
        required_text(source, ('id','kind','author','date_basis','url','title','category','checked','evidence','evidence_kind'), source['id'])
        if source['kind'] not in {'X','Reddit','GitHub','Web'} or source['evidence_kind'] not in EVIDENCE_KINDS:
            raise ValueError(f'Invalid source/evidence kind: {source["id"]}')
        valid_date(source['checked'], source['id']+' checked')
        aliases=source.get('aliases',[])
        if not isinstance(aliases,list) or not all(isinstance(url,str) and urlparse(url).scheme=='https' and urlparse(url).netloc for url in aliases):
            raise ValueError(f'Invalid source aliases: {source["id"]}')
        if source['date'] is not None: valid_date(source['date'], source['id']+' date')
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*',source['id']): raise ValueError(f'Invalid source ID: {source["id"]}')
        if source['checked']>site['edition']: raise ValueError(f'Check after edition: {source["id"]}')
        if source['id'] in ids or source['url'] in urls:
            raise ValueError(f'Duplicate source ID or URL: {source["id"]}')
        ids.add(source['id'])
        urls.add(source['url'])
        for identity in source_keys(source):
            if identity in identities and identities[identity] != source['id']:
                raise ValueError(f'Duplicate canonical source: {source["id"]} and {identities[identity]}')
            identities[identity] = source['id']
        for key in ('date', 'revised', 'checked'):
            if source.get(key):
                valid_date(source[key],source['id']+' '+key)
        for key in ('url', 'snapshot_url'):
            if source.get(key) and (urlparse(source[key]).scheme != 'https' or not urlparse(source[key]).netloc):
                raise ValueError(f'Expected HTTPS {key}: {source["id"]}')
        if source.get('date') and source['date'] > source['checked']:
            raise ValueError(f'Publication after check: {source["id"]}')
        if source.get('revised') and source['revised']>source['checked']: raise ValueError(f'Revision after check: {source["id"]}')
    for name, records in [('methods',methods),('recipes',recipes),('prompts',prompts)]:
        if not isinstance(records,list) or not records: raise ValueError(f'Expected nonempty list: {name}')
        record_ids = [record['id'] for record in records]
        if len(set(record_ids)) != len(record_ids):
            raise ValueError(f'Duplicate IDs in {name}')
        for record in records:
            required_text(record, ('id','title'), name)
            if name=='methods':
                required_text(record, ('action','limit'), name)
                if record.get('kind')!='editorial_recommendation' or not isinstance(record.get('sources'),list) or not record['sources']:
                    raise ValueError(f'Invalid method contract: {record["id"]}')
            elif name=='prompts':
                required_text(record, ('text',), name)
                if record.get('kind')!='editorial_template': raise ValueError(f'Invalid prompt kind: {record["id"]}')
            else:
                required_text(record, ('label','context','verify','trim','artifact'), name)
            for source_id in record.get('sources', []):
                if source_id not in ids:
                    raise ValueError(f'Unknown source {source_id} in {name}')

def load_english(sources, canonical):
    overlays=read_json('data/en/sources.json')
    translated={row['id']:row for row in overlays}
    if len(translated)!=len(overlays) or set(translated)!={s['id'] for s in sources}:
        raise ValueError('English source IDs must match the canonical catalog exactly')
    allowed={'id','title','evidence','date_basis','review_scope','takeaway','author'}
    result=[]
    for source in sources:
        overlay=translated[source['id']]
        if set(overlay)-allowed: raise ValueError(f'Unexpected translation metadata: {source["id"]}')
        required_text(overlay,('title','evidence','date_basis','review_scope'),source['id']+' English')
        reject_untranslated_copy(source,overlay,('title','evidence','date_basis','review_scope','takeaway'))
        if 'takeaway' in source: required_text(overlay,('takeaway',),source['id']+' English')
        result.append({**source,**overlay})
    data={}
    for name,records in canonical.items():
        rows=read_json(f'data/en/{name}.json')
        if [r['id'] for r in rows]!=[r['id'] for r in records]: raise ValueError(f'English {name} IDs/order mismatch')
        for base,row in zip(records,rows):
            reject_untranslated_copy(base,row,('title','action','limit','context','verify','trim','artifact','text'))
            for field in ('kind','sources'):
                if row.get(field)!=base.get(field): raise ValueError(f'English {name} {field} mismatch: {row["id"]}')
        data[name]=rows
    return result,data

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--check',action='store_true',help='Fail if generated outputs are stale')
    args=parser.parse_args()
    site=read_json('data/site.json')
    sources=read_json('data/sources.json')
    canonical={name:read_json('data/'+name+'.json') for name in ('methods','recipes','prompts')}
    check_baseline(ROOT)
    validate(sources,canonical['methods'],canonical['recipes'],canonical['prompts'],site)
    known={s['id']:s for s in sources}
    batches=[]
    for path in sorted((ROOT/'research/batches').glob('*.json')):
        batch=json.loads(path.read_text(encoding='utf-8'))
        if batch.get('publishing_status') not in {'reviewed_for_publication','published'}:
            raise ValueError(f'Unreviewed public batch: {path.name}')
        validate_batch(batch,known,historical=True)
        batches.append({'path':path.relative_to(ROOT).as_posix(),'data':batch})
    ko_ui=read_json('data/ui.json')
    en_ui=read_json('data/en/ui.json')
    if set(ko_ui)!=set(en_ui) or set(ko_ui['categories'])!=set(en_ui['categories']):
        raise ValueError('English UI keys must match Korean UI keys')
    english_sources,english_data=load_english(sources,canonical)
    outputs={}
    for language,language_sources,data,ui in [('ko',sources,canonical,ko_ui),('en',english_sources,english_data,en_ui)]:
        localized=[{**s,'category':ui['categories'][s['category']]} for s in language_sources]
        validate(localized,data['methods'],data['recipes'],data['prompts'],site)
        outputs.update(render_language(ROOT,site,localized,data['methods'],data['recipes'],data['prompts'],ui,batches,language))
    stale=[]
    for relative,content in outputs.items():
        target=ROOT/relative
        if args.check:
            if not target.exists() or target.read_text(encoding='utf-8')!=content: stale.append(relative)
        else:
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text(content,encoding='utf-8',newline='\n')
    if stale:
        print('Stale generated outputs: '+', '.join(stale),file=sys.stderr)
        return 1
    print(f'{"Checked" if args.check else "Built"}: ko + en, {len(sources)} sources, {len(canonical["methods"])} methods, {len(canonical["prompts"])} prompts')
    return 0

if __name__=='__main__':
    try:
        sys.exit(main())
    except (ValueError,KeyError,TypeError) as error:
        print(f'Build validation failed: {error}',file=sys.stderr)
        sys.exit(1)
