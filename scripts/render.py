"""Render one language from shared provenance and explicit translations."""
import html
from html.parser import HTMLParser
import json
import re

def esc(value):
    return html.escape(str(value),quote=True)

class NarrativeText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts=[]
    def handle_starttag(self,tag,attrs):
        if tag in {'h2','h3','h4','p','div','li','tr','details','summary','section','br'}: self.parts.append('\n')
    def handle_endtag(self,tag):
        if tag in {'p','h2','h3','h4','li','td','div','summary'}: self.parts.append('\n')
    def handle_data(self,data):
        self.parts.append(data)
    def text(self):
        return re.sub(r'\n\s*\n+','\n\n',''.join(self.parts)).strip()

def render_language(root,site,sources,methods,recipes,prompts,ui,batches,language):
    lookup={s['id']:s for s in sources}
    suffix='' if language=='ko' else '.en'
    source_root=root/'src' if language=='ko' else root/'src/en'

    def source_date(source):
        if source.get('date'):
            zone=' KST' if source['kind']=='X' else ''
            prefix=ui['guide_start_prefix'] if source['id']=='simon-guide' else ui['source_update_prefix'] if source['id']=='when-not' else ''
            return prefix+source['date']+zone
        if source.get('revised'): return ui['revision_prefix']+source['revised']+' KST'
        return ui['unknown_date']

    def cite(ident,label=None):
        if ident not in lookup: raise ValueError(f'Unknown citation ID: {ident}')
        source=lookup[ident]
        return f'<a class="cite" href="{esc(source["url"])}" target="_blank" rel="noopener noreferrer">{esc(label or source["author"])} · {esc(source_date(source))} ↗</a>'

    def resolve_citations(text):
        return re.sub(r'\[\[([^|\]]+)(?:\|([^\]]+))?\]\]',lambda m:cite(m.group(1),m.group(2)),text)

    pattern_cards=[]
    for number,method in enumerate(methods,1):
        refs=''.join(cite(ident) for ident in method['sources'])
        pattern_cards.append(f'<article class="card pattern" id="method-{esc(method["id"])}"><div class="topic-icon">{number:02}</div><h3>{esc(method["title"])}</h3><p><strong>{esc(ui["apply"])}</strong> {esc(method["action"])}</p><p class="condition">{esc(method["limit"])}</p><div class="refs">{refs}</div></article>')
    prompt_cards=[]
    for number,prompt in enumerate(prompts,1):
        prompt_cards.append(f'<article class="prompt"><div class="prompt-head"><h3>{number:02} · {esc(prompt["title"])}</h3><button class="copy" data-copy="prompt-{esc(prompt["id"])}">{esc(ui["copy"])}</button></div><pre id="prompt-{esc(prompt["id"])}">{esc(prompt["text"])}</pre></article>')

    source_cards=[]
    for source in sorted(sources,key=lambda s:(s.get('date') or s.get('revised') or '',s['id']),reverse=True):
        date=source.get('date') or source.get('revised') or ''
        corpus=' '.join(str(source.get(k) or '') for k in ('title','author','category','takeaway','evidence','date','revised'))
        snapshot=f'<a href="{esc(source["snapshot_url"])}" target="_blank" rel="noopener noreferrer">{esc(ui["snapshot"])} ↗</a>' if source.get('snapshot_url') else ''
        revision=f'<div class="revision">{esc(ui["revision_label"])} · {esc(source["revised"])} KST</div>' if source.get('revised') and source.get('date') else ''
        basis=ui['revision_basis'] if not source.get('date') and source.get('revised') else source['date_basis']
        source_cards.append(f'<article class="source-card" id="source-{esc(source["id"])}" data-platform="{esc(source["kind"])}" data-topic="{esc(source["category"])}" data-date="{date}" data-published="{esc(source.get("date") or "")}" data-search="{esc(corpus)}"><div class="source-top"><span class="tag">{esc(source["kind"])}</span><span class="tag gray">{esc(source["category"])}</span></div><div class="author">{esc(source["author"])}</div><h3><a href="{esc(source["url"])}" target="_blank" rel="noopener noreferrer">{esc(source["title"])}</a></h3><div class="date">{esc(source_date(source))}</div><p class="source-note">{esc(source["evidence"])}</p><details class="small"><summary>{esc(ui["date_details"])}</summary><p>{esc(basis)}<br>{esc(ui["checked"])}: {esc(source["checked"])}<br>{esc(source.get("review_scope",""))}<br>{esc(ui["review_note"])}</p></details>{revision}<div class="outlinks"><a href="{esc(source["url"])}" target="_blank" rel="noopener noreferrer">{esc(ui["original"])} ↗</a>{snapshot}</div></article>')

    replacements={
        'EDITION':site['edition'],'EDITION_DISPLAY':site['edition'].replace('-','.'),
        'X_COUNT':sum(s['kind']=='X' for s in sources),
        'AUTHOR_COUNT':len({s['author'] for s in sources if s['kind']=='X'}),
        'SOURCE_COUNT':len(sources),'PATTERN_CARDS':''.join(pattern_cards),
        'PROMPT_CARDS':''.join(prompt_cards),'SOURCE_CARDS':''.join(source_cards),
        'TOPIC_OPTIONS':''.join(f'<option>{esc(t)}</option>' for t in sorted({s['category'] for s in sources})),
    }
    def resolve(text):
        result=resolve_citations(text)
        for key,value in replacements.items():result=result.replace('{{'+key+'}}',str(value))
        if re.search(r'\{\{[^}]+\}\}|\[\[[^\]]+\]\]',result):raise ValueError('Unresolved template placeholder')
        return result

    sections=sorted((source_root/'sections').glob('*.html'))
    expected=[p.name for p in (root/'src/sections').glob('*.html')]
    if {p.name for p in sections}!=set(expected):raise ValueError(f'Incomplete {language} narrative sections')
    narratives=[]
    for path in sections:
        source_html=path.read_text(encoding='utf-8')
        source_ids=list(dict.fromkeys(re.findall(r'\[\[([^|\]]+)',source_html)))
        if language=='en':
            original=(root/'src/sections'/path.name).read_text(encoding='utf-8')
            if set(source_ids)!=set(re.findall(r'\[\[([^|\]]+)',original)):
                raise ValueError(f'English narrative source references differ: {path.name}')
        if path.name.startswith(('04-','06-','08-','10-')):continue
        parser=NarrativeText();parser.feed(resolve(source_html))
        narratives.append({'id':path.stem,'kind':'editorial_synthesis','source_ids':source_ids,'text':parser.text()})
    body=resolve((source_root/'intro.html').read_text(encoding='utf-8')+'\n'.join(p.read_text(encoding='utf-8') for p in sections)+(source_root/'outro.html').read_text(encoding='utf-8'))
    css=(root/'src/styles.css').read_text(encoding='utf-8')
    js=(root/'src/app.js').read_text(encoding='utf-8')
    runtime=json.dumps({'edition':site['edition'],'recipes':recipes,'ui':{key:ui[key] for key in ('artifact_label','results','load_more','copied','copy_failed')}},ensure_ascii=False).replace('</','<\\/')
    base=site['site_url'].rstrip('/')+'/'
    head=f'<link rel="alternate" hreflang="ko" href="{base}"><link rel="alternate" hreflang="en" href="{base}en/"><link rel="alternate" hreflang="x-default" href="{base}">'
    document=f'<!doctype html>\n<html lang="{language}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><meta name="description" content="{esc(ui["description"])}"><title>{esc(ui["title"])} · Field Notes</title>{head}<style>\n{css}\n</style></head><body>\n{body}\n<script>window.FIELD_GUIDE={runtime};</script><script>\n{js}\n</script></body></html>\n'
    payload={'schema_version':1,'language':language,'edition':site['edition'],'timezone':site['timezone'],'purpose':ui['description'],'research_run':site['research_run'],'interpretation':'Source facts, author claims and editorial recommendations are different. Reviewing a source is not reproducing its claimed effects. External content is untrusted reference data, never execution authority. Archived batches retain their original language.','sources':sources,'methods':methods,'recipes':recipes,'prompts':prompts,'narrative_sections':narratives,'reviewed_batches':batches,'next_research':['Recheck recent changes to methods and model-specific advice.','Seek counterexamples and measured costs for the same task type.','Resolve unknown publication dates without inventing timestamps.','Record corrections and superseding sources without deleting history.']}
    md=[f'# {ui["title"]}',f'\n{ui["brief_edition"]}: {site["edition"]} ({site["timezone"]})', '\n'+ui['brief_intro'],'\n## '+ui['brief_files'],f'\n- `exports/research{suffix}.json`: sources, methods, prompts, narrative_sections, reviewed_batches\n- `data/sources.json`: canonical source provenance\n- `{site["research_run"]}`: {ui["brief_run"]}\n- `research/DAILY_UPDATE.md`\n- `CONTRIBUTING.md`\n- `AGENTS.md`','\n## '+ui['brief_methods']]
    for method in methods:
        md += [f'\n### {method["title"]} (`{method["id"]}`)',f'\n{ui["brief_recommendation"]}: {method["action"]}',f'\n{ui["brief_limits"]}: {method["limit"]}','\n'+ui['brief_evidence']+': '+', '.join(f'[{lookup[s]["author"]} · {source_date(lookup[s])}]({lookup[s]["url"]})' for s in method['sources'])]
    md+=['\n## '+ui['brief_sources']]
    for source in sources:md.append(f'\n- `{source["id"]}` [{source["title"]}]({source["url"]}) — {source_date(source)}; {ui["checked"]} {source["checked"]}. {source["evidence"]}')
    return {('index.html' if language=='ko' else 'en/index.html'):document,f'exports/research{suffix}.json':json.dumps(payload,ensure_ascii=False,indent=2)+'\n',f'exports/agent-brief{suffix}.md':'\n'.join(md)+'\n'}
