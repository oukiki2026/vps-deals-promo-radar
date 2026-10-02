# ::ILANG
# [TYPE:code][PROJECT:vps-deals][ROLE:output-validation]
# ::RULE{核验canonical sitemap schema与真实方案数量}
# ::BOUNDARY{never:用测试通过冒充富媒体展示保证}
from config import ROOT,load_config
from build import active_offers
from html.parser import HTMLParser
from xml.etree import ElementTree as ET
import json,re

def main():
    cfg=load_config();base=cfg['base_url'].rstrip('/');site=ROOT/'site'
    offers=active_offers(cfg,json.loads((ROOT/'data/offers.json').read_text(encoding='utf-8')))
    xml=ET.parse(site/'sitemap.xml');locations=[x.text for x in xml.findall('.//{*}loc')]
    assert len([u for u in locations if '/deals/' in u])==len(offers)
    assert len(list((site/'deals').glob('*/index.html'))) == len(offers) if offers else not (site/'deals').exists()
    for url in locations:
        assert url.startswith(base+'/'),url
        path=url[len(base):];html=(site/path.lstrip('/')/'index.html').read_text(encoding='utf-8') if path!='/' else (site/'index.html').read_text(encoding='utf-8')
        canon=re.findall(r'<link rel="canonical" href="([^"]+)"',html)
        assert canon==[url],(url,canon)
        assert 'example.invalid' not in html if 'example.invalid' not in base else True
        for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>',html,re.S):
            nodes=json.loads(raw)
            for n in nodes:
                if n.get('@type')=='Offer':assert n['priceCurrency']=='USD' and float(n['price'])>0
        for link in re.findall(r'href="(/[^"]*)"',html):
            link=link.split('#')[0].split('?')[0]
            if not link:continue
            target=site/link.lstrip('/')
            assert target.exists() or (target/'index.html').exists(),link
    assert 'Sitemap: '+base+'/sitemap.xml' in (site/'robots.txt').read_text()
    assert (site/'assets/og.png').read_bytes().startswith(b'\x89PNG')
    print(json.dumps(dict(pages=len(locations),deal_pages=len(offers),canonical_base=base,sitemap_matches=True,jsonld_parse=True,internal_links=True),indent=2))

if __name__=='__main__':main()
