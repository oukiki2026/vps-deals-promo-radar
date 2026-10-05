import tempfile, unittest
from pathlib import Path
from build import build
from config import ROOT

class AiContentTests(unittest.TestCase):
    def test_config_disables_pages_navigation_and_sitemap(self):
        raw=(ROOT/'site-config'/'site.conf').read_text(encoding='utf-8')
        with tempfile.TemporaryDirectory() as d:
            config=Path(d)/'site.conf';output=Path(d)/'site'
            config.write_text(raw,encoding='utf-8');build(config,output)
            self.assertTrue((output/'ai-tools/cursor/index.html').exists())
            self.assertIn('/ai-tools/cursor/',(output/'sitemap.xml').read_text())
            config.write_text(raw.replace('ai_tools_enabled = true','ai_tools_enabled = false'),encoding='utf-8');build(config,output)
            self.assertFalse((output/'ai-tools').exists())
            self.assertNotIn('/ai-tools/',(output/'index.html').read_text(encoding='utf-8'))
            self.assertNotIn('/ai-tools/',(output/'sitemap.xml').read_text())
