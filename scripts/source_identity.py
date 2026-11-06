"""Stable identities for citation deduplication; never rewrites original URLs."""
import re
from urllib.parse import parse_qsl, urlencode, urlsplit

def source_identity(url):
    parsed=urlsplit(url)
    host=(parsed.hostname or '').lower()
    path=parsed.path.rstrip('/')
    if host in {'x.com','www.x.com','twitter.com','www.twitter.com','mobile.twitter.com'}:
        match=re.search(r'/status/(\d+)',path)
        if match:return 'x:'+match.group(1)
    if host=='redd.it':return 'reddit:post:'+path.strip('/').lower()
    if host=='reddit.com' or host.endswith('.reddit.com'):
        query_comment=dict(parse_qsl(parsed.query)).get('comment')
        if query_comment and re.fullmatch(r'[A-Za-z0-9]+',query_comment):return 'reddit:comment:'+query_comment.lower()
        comment=re.search(r'/comments/[^/]+/(?:[^/]+/)?comment/([^/]+)',path)
        if comment:return 'reddit:comment:'+comment.group(1).lower()
        post=re.search(r'/comments/([^/]+)',path)
        if post:
            tail=path[post.end():].strip('/').split('/')
            if len(tail)>=2 and tail[-1] not in {'comment','comments'}:
                return 'reddit:comment:'+tail[-1].lower()
            return 'reddit:post:'+post.group(1).lower()
    if host in {'github.com','www.github.com'}:
        parts=path.strip('/').split('/')
        if len(parts)>=2:
            repo='/'.join(parts[:2]).lower().removesuffix('.git')
            if len(parts)>=4 and parts[2] in {'issues','pull','discussions'} and re.fullmatch(r'(?:issuecomment-|discussioncomment-|discussion_r|pullrequestreview-|r)\d+',parsed.fragment):
                return 'github-comment:'+repo+':'+parsed.fragment
            if len(parts)==2:return 'github:'+repo+':README.md'
            if len(parts)>=5 and parts[2]=='blob':return 'github:'+repo+':'+('/'.join(parts[4:]))
            if len(parts)>=5 and parts[2]=='tree':return 'github:'+repo+':'+('/'.join(parts[4:]))+'/README.md'
    query=urlencode(sorted((k,v) for k,v in parse_qsl(parsed.query,keep_blank_values=True) if not k.lower().startswith('utm_') and k.lower() not in {'fbclid','gclid','mc_cid','mc_eid'}))
    return 'web:'+host+path+('?' +query if query else '')

def source_keys(source):
    urls=[source[field] for field in ('url','snapshot_url') if source.get(field)]
    return {source_identity(url) for url in urls+source.get('aliases',[])}
