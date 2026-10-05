# vps-deals project instructions

Purpose: monitor public official-source VPS offers and prices. Runtime: Python standard library static site.

- Single source of truth: `site-config/site.conf`; both scraper.py and build.py must read it.
- Allowed: fix parsers, edit templates, add public official sources, test, deploy.
- Sources: read only public official price pages, feeds or sitemaps; check robots first; never bypass a failure.
- One record = provider + real plan name + currency, deduplicated; must have a current price source and purchase conditions.
- Config change => re-run scrape and build; test that removing a provider removes its pages and navigation.
- Domain switch => write back base_url and @SITE.domain with the real Pages domain or activated custom domain; verify canonical/sitemap/robots externally after building.
- Affiliation: only use approved, legitimate affiliate links; with no approval keep bare official links and state clearly there is no commission.
- Never: invent offers, prices, commissions or expiry dates; fake traffic; buy followers; bypass anti-bot; brand-keyword bidding; cookie injection; self-referral.
- Never: commit credentials or tokens; publish unverified offers; claim domain age guarantees rankings.
- Verify with: python -m unittest discover -s tests; python scraper.py; python build.py; then check live schema and sitemap.
