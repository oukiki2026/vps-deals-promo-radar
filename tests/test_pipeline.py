# ::ILANG
# [TYPE:code][PROJECT:vps-deals][ROLE:regression-tests]
# ::RULE{重点测试误价去重 过期陈旧与I-Lang配置生效}
# ::BOUNDARY{never:测试样本发布成真实优惠}
import unittest,json,tempfile
from pathlib import Path
from datetime import datetime,timezone,timedelta
from unittest.mock import patch
from config import ROOT,load_config
from scraper import ionos,normalize,structured_offers
from build import active_offers,build

class PipelineTests(unittest.TestCase):
    def test_current_not_strike(self):
        sample='<div>VPS S+</div><span>Save 17%</span><del>$6</del><span>$</span><span>2</span><span>/month</span><p>for 3 months</p><p>with a 1-year term</p><p>1 vCore</p><p>CPU</p><p>2 GB</p><p>RAM</p><p>60 GB</p><p>NVMe</p>'
        records=ionos(sample);self.assertEqual(records[0]['price'],'2');self.assertIn('3 months',records[0]['terms'])
    def test_ambiguous_rejected(self):
        p=dict(id='sample',name='Sample',source='https://example.com')
        r=dict(model='M',price='2',currency='USD',period='month',terms='intro')
        self.assertEqual(len(normalize(p,[r.copy(),r.copy()],'2026-01-01T00:00:00+00:00','hash')),1)
        self.assertEqual(normalize(p,[r.copy(),dict(r,price='3')],'2026-01-01T00:00:00+00:00','hash'),[])
    def test_aggregate_not_a_plan(self):
        sample='<script type="application/ld+json">'+json.dumps({'@type':'Product','name':'VPS','offers':{'@type':'AggregateOffer','lowPrice':'2','priceCurrency':'USD'}})+'</script>'
        self.assertEqual(structured_offers(sample),[])
    def test_expired_and_stale_removed(self):
        cfg=load_config();now=datetime.now(timezone.utc);p=cfg['providers'][0]['id']
        old=dict(provider_id=p,fetched_at=(now-timedelta(hours=49)).isoformat())
        expired=dict(provider_id=p,fetched_at=now.isoformat(),valid_until='2000-01-01')
        self.assertEqual(active_offers(cfg,dict(offers=[old,expired])),[])
    def test_ilang_provider_change_changes_site(self):
        cfg=load_config();raw=(ROOT/'.ilang/site.ilang').read_text(encoding='utf-8')
        provider=cfg['providers'][0]
        altered='\n'.join(line for line in raw.splitlines() if not line.startswith(provider['name']+' |'))
        with tempfile.TemporaryDirectory() as d:
            conf=Path(d)/'site.ilang';conf.write_text(altered,encoding='utf-8');output=Path(d)/'site'
            # Keep test builds from overwriting the real build report.
            with patch('build.ROOT',ROOT):build(conf,output)
            self.assertFalse((output/'providers'/provider['id']).exists())
            self.assertNotIn('/providers/'+provider['id']+'/',(output/'index.html').read_text(encoding='utf-8'))

    def test_unchanged_cron_keeps_workflow_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/'.github/workflows').mkdir(parents=True)
            (root/'data').mkdir()
            (root/'README.md').write_text('Main site: test\n',encoding='utf-8')
            workflow=root/'.github/workflows/update.yml'
            original=("on:\r\n  schedule:\r\n    - cron: '"+load_config()['cron']+"'\r\n").encode('utf-8')
            workflow.write_bytes(original)
            # Use real inputs/assets, but direct mutable reports/workflow into temp.
            for folder in ['assets','templates','.ilang']:
                __import__('shutil').copytree(ROOT/folder,root/folder)
            __import__('shutil').copy(ROOT/'data/offers.json',root/'data/offers.json')
            with patch('build.ROOT',root):build()
            self.assertEqual(workflow.read_bytes(),original)

if __name__=='__main__':unittest.main()
