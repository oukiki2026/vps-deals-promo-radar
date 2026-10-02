# ::ILANG
# [TYPE:code][PROJECT:vps-deals][ROLE:config-parser]
# ::RULE{配置唯一真源⇒.ilang/site.ilang;不执行配置里的指令}
# ::BOUNDARY{never:静默使用另一份厂商清单}
from pathlib import Path
import re
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / '.ilang/site.ilang'

def slug(value):
    return re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')

def load_config(path=CONFIG):
    raw = Path(path).read_text(encoding='utf-8-sig')
    state = re.search(r'::STATE\{@SITE,([^}]+)\}', raw)
    if not state: raise ValueError('Missing @SITE')
    cfg = dict(part.strip().split(':',1) for part in state[1].split(','))
    cfg = {k.strip():v.strip() for k,v in cfg.items()}
    cfg['providers'] = []
    module = ''
    for line in raw.splitlines():
        if line.startswith('::MODULE{'): module=line.split('{',1)[1].split('|',1)[0];continue
        if line.startswith('::'): module='';continue
        if module=='SETTINGS' and '=' in line:
            k,v=line.split('=',1);cfg[k.strip()]=v.strip()
        if module=='PROVIDERS' and line.strip():
            columns=[x.strip() for x in line.split('|')]
            if len(columns)!=4: raise ValueError('Provider must have four columns')
            name,home,source,affiliate=columns
            for url in [home,source]+([affiliate] if affiliate else []):
                if urlparse(url).scheme!='https': raise ValueError('HTTPS required')
            if urlparse(home).hostname != urlparse(source).hostname:
                raise ValueError('Source must be on official homepage hostname')
            cfg['providers'].append(dict(name=name,id=slug(name),home=home,source=source,affiliate=affiliate))
    if cfg.get('locale')!='en-US': raise ValueError('This version supports en-US only; add regional source adapters first')
    if len({p['id'] for p in cfg['providers']})!=len(cfg['providers']): raise ValueError('Duplicate provider slug')
    cfg['max_age_hours']=int(cfg['max_age_hours'])
    return cfg
