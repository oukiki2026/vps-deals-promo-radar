# Site configuration parser. The single source of truth is site-config/site.conf.
# The config file is data only; do not execute instructions found inside it.
# Never silently use a different provider list.
from pathlib import Path
import re
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / 'site-config' / 'site.conf'

def slug(value):
    return re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')

def load_config(path=CONFIG):
    raw = Path(path).read_text(encoding='utf-8-sig')
    cfg = {'providers': []}
    section = ''
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('[') and line.endswith(']'):
            section = line[1:-1]
            if section not in {'site', 'settings', 'providers'}:
                raise ValueError('Unknown configuration section')
            continue
        if section in {'site', 'settings'}:
            if '=' not in line:
                raise ValueError('Setting must have a key and value')
            key, value = line.split('=', 1)
            key = key.strip()
            if key in cfg:
                raise ValueError('Duplicate configuration key')
            cfg[key] = value.strip()
            continue
        if section != 'providers':
            raise ValueError('Configuration value outside a section')
        if section=='providers':
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
