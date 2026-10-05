# [TYPE:code][PROJECT:vps-deals][ROLE:public-source-scraper]
# ::RULE{先检查robots;只解析可核验当期价格;失败就不展示}
# ::BOUNDARY{never:反爬绕过 编价格 编有效期 续费价冒充促销价}
from config import ROOT,load_config,slug
from html.parser import HTMLParser
from datetime import datetime,timezone
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from urllib.parse import urlparse,urljoin
from urllib.robotparser import RobotFileParser
from decimal import Decimal,InvalidOperation
import json,re,hashlib,time

AGENT='VPSDealsBot/1.0 (+https://github.com/oukiki2026/vps-deals-promo-radar)'

class VisibleText(HTMLParser):
    def __init__(self): super().__init__();self.skip=0;self.parts=[]
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style','noscript'):self.skip+=1
    def handle_endtag(self,tag):
        if tag in ('script','style','noscript'):self.skip=max(0,self.skip-1)
    def handle_data(self,data):
        if not self.skip and data.strip():self.parts.append(data.strip())

def text_content(raw):
    p=VisibleText();p.feed(raw);return '\n'.join(p.parts)

class SameHostRedirect(__import__('urllib.request',fromlist=['HTTPRedirectHandler']).HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        if urlparse(newurl).hostname != urlparse(req.full_url).hostname:
            raise ValueError('Cross-host redirect refused; configure official source explicitly')
        return super().redirect_request(req,fp,code,msg,headers,newurl)

def fetch(url):
    opener=__import__('urllib.request',fromlist=['build_opener']).build_opener(SameHostRedirect())
    with opener.open(Request(url,headers={'User-Agent':AGENT,'Accept-Language':'en-US,en;q=0.8'}),timeout=30) as response:
        raw=response.read(5_000_001)
        if len(raw)>5_000_000:raise ValueError('Source too large')
        return raw.decode('utf-8','replace')

def check_robots(source):
    origin=urlparse(source);url=f'{origin.scheme}://{origin.netloc}/robots.txt'
    try:raw=fetch(url)
    except HTTPError as e:
        if e.code==404:raw='User-agent: *\nAllow: /'
        else:raise
    rp=RobotFileParser();rp.parse(raw.splitlines())
    if not rp.can_fetch(AGENT,source):raise ValueError('Disallowed by robots.txt')
    delay=rp.crawl_delay(AGENT) or rp.crawl_delay('*') or 1
    if delay>60:raise ValueError('Crawl delay exceeds run budget; source skipped')
    time.sleep(delay)
    return dict(url=url,sha256=hashlib.sha256(raw.encode()).hexdigest(),allowed=True)

def ionos(raw):
    # Parse the visible US plan cards, not crossed-out prices or ambiguous AggregateOffer.
    text=text_content(raw)
    pattern=r'(VPS (?:S|M|L|XL|XXL)\+)\nSave \d+%\n\$[\d.]+\n\$\n(\d+(?:\.\d+)?)\n/month\nfor (\d+) months\nwith a (\d+)-year term\n(\d+) vCores?\nCPU\n(\d+) GB\nRAM\n(\d+) GB\nNVMe'
    records=[]
    for m in re.finditer(pattern,text):
        model,price,promo,term,cpu,ram,storage=m.groups()
        records.append(dict(model=model,price=price,currency='USD',kind='introductory',period='month',
            terms=f'Introductory rate for {promo} months with a {term}-year term. Later charges differ; confirm full contract, renewal and taxes with IONOS.',
            specs=f'{cpu} vCore · {ram} GB RAM · {storage} GB NVMe',
            evidence=f'{model}: USD {price}/month for {promo} months with a {term}-year term; {cpu} vCore, {ram} GB RAM, {storage} GB NVMe.',
            parser='ionos-visible-plan-card-v1'))
    return records

def structured_offers(raw):
    # Strict Product+Offer only. Generic aggregate prices do not identify a real plan.
    records=[]
    def visit(node):
        if isinstance(node,list):
            for item in node:visit(item)
        elif isinstance(node,dict):
            types=node.get('@type',[]);types=types if isinstance(types,list) else [types]
            if 'Product' in types:
                model=node.get('name','');offers=node.get('offers',[]);offers=offers if isinstance(offers,list) else [offers]
                for o in offers:
                    if not isinstance(o,dict) or o.get('@type')!='Offer':continue
                    # Unspecified billing period/current-vs-renewal cannot be reliably priced.
                    if not o.get('priceSpecification',{}).get('unitText'):continue
                    if not isinstance(model,str) or not model.strip() or len(model)>100:continue
                    if 'price' not in o or o.get('priceCurrency')!='USD':continue
                    record=dict(model=model,price=str(o['price']),currency='USD',kind='listed-price',period=o['priceSpecification']['unitText'],terms='Official listed price; confirm all billing terms and taxes on the provider page.',evidence=f'{model}: USD {o["price"]} per {o["priceSpecification"]["unitText"]}.',parser='official-product-offer-jsonld-v1')
                    if o.get('priceValidUntil'):record['valid_until']=o['priceValidUntil']
                    records.append(record)
            for value in node.values():
                if isinstance(value,(dict,list)):visit(value)
    for script in re.findall(r'<script\b[^>]*type=[\"\']application/ld\+json[\"\'][^>]*>(.*?)</script>',raw,re.S|re.I):
        try:visit(json.loads(script))
        except (ValueError,TypeError):continue
    return records

def normalize(provider,records,now,source_hash):
    grouped={}
    for r in records:
        try:price=Decimal(r['price'])
        except (InvalidOperation,KeyError):continue
        if not price.is_finite() or price<=0:continue
        if r.get('valid_until'):
            try:
                if datetime.fromisoformat(r['valid_until'].replace('Z','+00:00')).date()<datetime.now(timezone.utc).date():continue
            except ValueError:continue
        key=(provider['id'],r['model'],r['currency']);r['price']=format(price,'f')
        grouped.setdefault(key,[]).append(r)
    result=[]
    for key,items in grouped.items():
        if len({(r['price'],r['period'],r['terms']) for r in items})!=1:continue
        r=items[0]
        result.append(dict(r,id=slug(provider['name']+' '+r['model']+' '+r['currency']),provider_id=provider['id'],title=provider['name']+' '+r['model'],offer_url=provider['source'],source_url=provider['source'],fetched_at=now,source_sha256=source_hash))
    return result

def main():
    cfg=load_config();now=datetime.now(timezone.utc).isoformat(timespec='seconds');offers=[];statuses=[]
    for p in cfg['providers']:
        status=dict(provider_id=p['id'],name=p['name'],source_url=p['source'],checked_at=now)
        try:
            status['robots']=check_robots(p['source']);raw=fetch(p['source']);sha=hashlib.sha256(raw.encode()).hexdigest()
            records=ionos(raw) if urlparse(p['source']).hostname=='www.ionos.com' and urlparse(p['source']).path=='/servers/vps' else structured_offers(raw)
            parsed=normalize(p,records,now,sha);offers+=parsed
            status.update(status='verified' if parsed else 'no-verifiable-price',offer_count=len(parsed),source_sha256=sha)
        except Exception as e:
            status.update(status='unavailable',offer_count=0,reason=str(e)[:200])
        statuses.append(status)
        print(p['name'],status['status'],status['offer_count'])
    output=dict(schema_version=1,fetched_at=now,locale=cfg['locale'],offers=offers,providers=statuses)
    (ROOT/'data').mkdir(exist_ok=True)
    (ROOT/'data/offers.json').write_text(json.dumps(output,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(f'Published {len(offers)} independently identified plans; unsupported sources remain visible without prices.')

if __name__=='__main__':main()
