# vps-deals project instructions

Purpose: publish useful AI guides and monitor public official-source VPS offers and prices. Runtime: Hugo 0.167.0 renders the site (`hugo --minify -d site`); Python standard library remains the data layer (scraper.py, tools/prebuild.py, config.py).

- Single source of truth: `site-config/site.conf`; scraper.py and tools/prebuild.py must both read it (build.py keeps data-layer helpers only).
- Allowed: fix parsers, edit templates, add public official sources, test, deploy.
- Sources: read only public official price pages, feeds or sitemaps; check robots first; never bypass a failure.
- One record = provider + real plan name + currency, deduplicated; must have a current price source and purchase conditions.
- Config change => re-run scrape and build; test that removing a provider removes its pages and navigation.
- Domain switch => write back base_url and domain with the real Pages domain or activated custom domain; verify canonical/sitemap/robots externally after building.
- Affiliation: only use approved, legitimate affiliate links; with no approval keep bare official links and state clearly there is no commission.
- Never: invent offers, prices, commissions or expiry dates; fake traffic; buy followers; bypass anti-bot; brand-keyword bidding; cookie injection; self-referral.
- Never: commit credentials or tokens; publish unverified offers; claim domain age guarantees rankings.
- Verify with: python -m unittest discover -s tests; python scraper.py; python tools/prebuild.py && hugo --minify -d site; python validate.py; then check live content, schema and sitemap.
