# ::ILANG
# [TYPE:code][PROJECT:vps-deals][ROLE:static-builder]
# ::RULE{从site.ilang读品牌厂商域名;从数据读事实;过期与陈旧记录下架}
# ::BOUNDARY{never:编价格有效期 把schema当排名保证 输出凭据}
from config import ROOT,load_config
from datetime import datetime,timezone,timedelta
from pathlib import Path
from html import escape
from string import Template
from xml.sax.saxutils import escape as xml_escape
import json,shutil,re,hashlib

def active_offers(cfg,data,now=None):
    now=now or datetime.now(timezone.utc);providers={p['id'] for p in cfg['providers']};out=[]
    for o in data['offers']:
        if o['provider_id'] not in providers:continue
        stamp=datetime.fromisoformat(o['fetched_at'].replace('Z','+00:00'))
        if stamp.tzinfo is None or now-stamp>timedelta(hours=cfg['max_age_hours']) or stamp>now+timedelta(minutes=5):continue
        if o.get('valid_until') and datetime.fromisoformat(o['valid_until'].replace('Z','+00:00')).date()<now.date():continue
        out.append(o)
    return out

def build(config_path=None,output=None):
    cfg=load_config(config_path) if config_path else load_config();base=cfg['base_url'].rstrip('/')
    if not re.fullmatch(r'https://[A-Za-z0-9.-]+',base):raise ValueError('base_url must be an HTTPS origin')
    data=json.loads((ROOT/'data/offers.json').read_text(encoding='utf-8'))
    offers=active_offers(cfg,data);out=Path(output) if output else ROOT/'site'
    # Delete only our generated output inside this repo or an explicit test temp directory.
    if out.resolve()==ROOT.resolve() or out.resolve()==ROOT.parent.resolve():raise ValueError('Refuse deleting source directory')
    if out.exists():shutil.rmtree(out)
    out.mkdir(parents=True);(out/'assets').mkdir();shutil.copy(ROOT/'assets/style.css',out/'assets/style.css');shutil.copy(ROOT/'assets/logo.svg',out/'assets/logo.svg')
    shutil.copy(ROOT/'assets/og.png',out/'assets/og.png')
    style_version=hashlib.sha256((ROOT/'assets/style.css').read_bytes()).hexdigest()[:12]
    (out/'data').mkdir();public_data=dict(data,offers=offers,providers=[p for p in data['providers'] if p['provider_id'] in {x['id'] for x in cfg['providers']}]);(out/'data/offers.json').write_text(json.dumps(public_data,indent=2),encoding='utf-8')
    providers={p['id']:p for p in cfg['providers']};statuses={p['provider_id']:p for p in data['providers']}
    month=datetime.fromisoformat(data['fetched_at']).strftime('%B %Y');paths=[]
    def url(path):return base+path
    def render(template,**kw):return Template((ROOT/'templates'/template).read_text(encoding='utf-8')).substitute(**kw)
    def card(o):
        return f'<article class="card"><div class="eyebrow">{escape(providers[o["provider_id"]]["name"])} · {escape(o["kind"])}</div><h3><a href="/deals/{o["id"]}/">{escape(o["model"])}</a></h3><p class="price">${escape(o["price"])}<small> USD / {escape(o["period"])}</small></p><p>{escape(o.get("specs",""))}</p><p class="terms">{escape(o["terms"])}</p><a class="arrow" href="/deals/{o["id"]}/">Review source &amp; terms ↗</a></article>'
    def itemlist(items):return {'@context':'https://schema.org','@type':'ItemList','itemListElement':[{'@type':'ListItem','position':i+1,'url':url('/deals/'+o['id']+'/'),'name':o['title']} for i,o in enumerate(items)]}
    def page(path,title,description,content,schemas=None,lastmod=None):
        bread={'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':cfg['brand'],'item':url('/')}]}
        if path!='/':bread['itemListElement'].append({'@type':'ListItem','position':2,'name':title,'item':url(path)})
        schema=json.dumps((schemas or [])+[bread],ensure_ascii=False).replace('<','\\u003c')
        support_links='<a href="/privacy/">Privacy policy</a>'
        if cfg.get('operator_name'):support_links+='<a href="/about/">About</a>'
        if cfg.get('contact_email'):support_links+='<a href="/contact/">Contact</a>'
        html=render('base.html',brand=escape(cfg['brand']),tagline=escape(cfg['tagline']),title=escape(title),description=escape(description),canonical=escape(url(path)),base_url=escape(base),content=content,schema=schema,repo=escape(cfg['repository']),updated=escape(data['fetched_at']),support_links=support_links,style_version=style_version)
        target=out/path.lstrip('/')/'index.html' if path!='/' else out/'index.html';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(html,encoding='utf-8');paths.append((path,lastmod or data['fetched_at']))
    nav=''.join(f'<a class="provider-pill" href="/providers/{p["id"]}/">{escape(p["name"])}</a>' for p in cfg['providers'])
    page('/',f'{cfg["brand"]} — VPS introductory offers · {month}',cfg['tagline'],render('index.html',month=month,count=len(offers),cards=''.join(card(o) for o in offers) or '<p>No currently verified offers. Check the official sources below.</p>',providers=nav),[itemlist(offers)])
    for p in cfg['providers']:
        items=[o for o in offers if o['provider_id']==p['id']];st=statuses.get(p['id'],{});check=st.get('checked_at','Not checked yet')
        content=render('provider.html',name=escape(p['name']),source=escape(p['source']),status=escape(st.get('status','not-checked')),checked=escape(check),cards=''.join(card(o) for o in items) or '<div class="notice">No verified current price available. This is not a claim that the provider has no offers. Check the official source.</div>')
        schemas=[]
        # Separate Services prevent unrelated server plans being merged into one Product.
        for o in items:
            schemas.append({'@context':'https://schema.org','@type':'Service','name':o['title'],'provider':{'@type':'Organization','name':p['name']},'offers':offer_schema(o)})
        page('/providers/'+p['id']+'/',f'{p["name"]} VPS offers & source status · {month}',f'Official-source {p["name"]} plans, current verification status and billing terms.',content,schemas)
    for o in offers:
        p=providers[o['provider_id']];target=p['affiliate'] or o['offer_url'];affiliate=bool(p['affiliate'])
        content=render('deal.html',title=escape(o['title']),price=escape(o['price']),currency=escape(o['currency']),period=escape(o['period']),specs=escape(o.get('specs','')),terms=escape(o['terms']),source=escape(o['source_url']),fetched=escape(o['fetched_at']),evidence=escape(o['evidence']),hash=escape(o['source_sha256']),target=escape(target),rel='sponsored noopener' if affiliate else 'noopener',disclosure='Affiliate link: we may earn a commission if you buy.' if affiliate else 'Direct official link. No affiliate commission is configured.')
        schema=offer_schema(o);schema.update({'@context':'https://schema.org','name':o['title'],'seller':{'@type':'Organization','name':p['name']}})
        page('/deals/'+o['id']+'/',f'{o["title"]} — {o["currency"]} {o["price"]}/{o["period"]} · {month}',f'{o["title"]}: {o["currency"]} {o["price"]}/{o["period"]}. {o["terms"]}',content,[schema],o['fetched_at'])
    rows=''.join(f'<tr><td><a href="/deals/{o["id"]}/">{escape(o["title"])}</a></td><td>USD {escape(o["price"])}/{escape(o["period"])}</td><td>{escape(o.get("specs",""))}</td><td>{escape(o["terms"])}</td></tr>' for o in offers)
    page('/compare/',f'Compare verified VPS introductory offers · {month}','Compare only verified prices, hardware and introductory billing conditions.',render('compare.html',rows=rows),[itemlist(offers)])
    page('/methodology/',f'How {cfg["brand"]} verifies offers','Official sources, conservative extraction, billing conditions and affiliate disclosure.',render('methodology.html',freshness=cfg['max_age_hours']))
    policy_date=cfg.get('privacy_updated','2026-10-02')
    privacy_contact='<a href="/contact/">Contact the site operator</a>' if cfg.get('contact_email') else f'<a href="{escape(cfg["repository"])}/issues">Public repository issue tracker</a> (do not post private information)'
    page('/privacy/',f'Privacy policy | {cfg["brand"]}','How this static site handles hosting requests, external links and future third-party advertising.',render('privacy.html',brand=escape(cfg['brand']),domain=escape(cfg['domain']),policy_date=escape(policy_date),privacy_contact=privacy_contact),lastmod=policy_date)
    if cfg.get('operator_name'):
        page('/about/',f'About {cfg["brand"]}','Who maintains this official-source VPS offer monitor and how it works.',render('about.html',brand=escape(cfg['brand']),operator=escape(cfg['operator_name']),repo=escape(cfg['repository'])))
    if cfg.get('contact_email'):
        email=cfg['contact_email']
        if not re.fullmatch(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",email):raise ValueError('contact_email must be a plain email address')
        page('/contact/',f'Contact | {cfg["brand"]}','Report an incorrect offer, ask about privacy or contact the site operator.',render('contact.html',email=escape(email),repo=escape(cfg['repository'])))
    sitemap='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{xml_escape(url(path))}</loc><lastmod>{xml_escape(stamp)}</lastmod></url>' for path,stamp in paths)+'</urlset>'
    (out/'sitemap.xml').write_text(sitemap,encoding='utf-8');(out/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+url('/sitemap.xml')+'\n',encoding='utf-8')
    (out/'_headers').write_text('/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n  Content-Security-Policy: default-src \'self\'; style-src \'self\'; img-src \'self\'; script-src \'none\'; frame-ancestors \'none\'\n',encoding='utf-8')
    # Static 404 prevents Pages SPA fallback from returning the homepage for removed offers.
    (out/'404.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><link rel="stylesheet" href="/assets/style.css"><title>Page unavailable</title><main><section class="page-hero"><h1>Page unavailable</h1><p>This offer may have expired or failed verification, or the address may be incorrect.</p><a class="button" href="/">View current offers</a></section></main></html>'.replace('href="/assets/style.css"',f'href="/assets/style.css?v={style_version}"'),encoding='utf-8')
    if not config_path and not output:
        (ROOT/'data/build-report.json').write_text(json.dumps(dict(base_url=base,deal_pages=len(offers),total_pages=len(paths),fetched_at=data['fetched_at']),indent=2)+'\n',encoding='utf-8')
        readme=ROOT/'README.md';body=readme.read_text(encoding='utf-8')
        main_line='Main site: deployment pending; no verified public URL yet.' if base=='https://example.invalid' else f'Main site: [{base}]({base})'
        body=re.sub(r'Main site:.*',main_line,body)
        readme.write_text(body,encoding='utf-8')
        workflow=ROOT/'.github/workflows/update.yml';original=workflow.read_text(encoding='utf-8')
        body=re.sub(r"- cron: '[^']+'", "- cron: '"+cfg['cron']+"'",original)
        # Leave identical workflow bytes intact: CRLF normalization alone must not
        # make an Actions data update attempt a workflow-permission change.
        if body!=original:workflow.write_text(body,encoding='utf-8')
    print(f'Built {len(paths)} pages, including {len(offers)} deal pages; canonical base {base}')
    return out

def offer_schema(o):
    s={'@type':'Offer','price':o['price'],'priceCurrency':o['currency'],'url':o['offer_url'],'description':o['terms'],'availability':'https://schema.org/OnlineOnly'}
    if o.get('valid_until'):s['priceValidUntil']=o['valid_until']
    return s

if __name__=='__main__':build()
