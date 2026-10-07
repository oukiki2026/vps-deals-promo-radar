# kikomono-deals

VPS offers and AI tools for developers. Official sources. Clear terms.

Main site: [https://kikomono.com](https://kikomono.com)

Maintained by OuKiki. Public contact: [oukiki2026@gmail.com](mailto:oukiki2026@gmail.com).
Site information: [About](https://kikomono.com/about/) · [Contact](https://kikomono.com/contact/) · [Privacy policy](https://kikomono.com/privacy/).

![Brand mark](assets/logo.svg)

## What this is

English AI workflow guides with a deterministic official-source offer-monitoring pipeline. It reads official public pages, checks robots.txt and publishes only plans with identifiable names, current prices and billing conditions. Providers that cannot be verified remain visible without prices. No estimated search volumes, fake discounts or guaranteed-income claims.

## Run locally

Python 3.12+; standard library only; no paid inference or data API keys.

```sh
python make_assets.py
python scraper.py
python build.py
python validate.py
python -m unittest discover -s tests -v
```

Cloudflare Pages build command: `python build.py`; output: `site/`. Connect the public repository through the Cloudflare GitHub App. No Cloudflare token needs to be stored in GitHub Actions. GitHub supplies the workflow's short-lived `GITHUB_TOKEN` for committing verification records.

## Configuration that changes the site

`site-config/site.conf` is parsed by both scraper and builder. Use `[site]` for identity, `[settings]` for build options and `[providers]` for pipe-separated provider rows. Edit values, then run the pipeline. The regression test removes a provider and checks that its page and navigation disappear. The first version intentionally supports only en-US; add real regional source adapters before extending languages.

The same configuration holds `operator_name`, `contact_email` and `privacy_updated`. About and contact pages are published only when the corresponding real details have been supplied. Approved affiliate placements and analytics are configured. Keep privacy disclosures, consent handling and Content Security Policy aligned with the actual integrations.

The scheduled workflow requests a check every six hours, at minute 17 UTC. Execution may be delayed or fail. Verification timestamps are genuine retrieval times, not claims that the price is still available. Scheduled public workflows can be disabled after inactivity by GitHub. See [GitHub schedule rules](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/disable-and-enable-workflows) and [Actions billing](https://docs.github.com/en/actions/concepts/billing-and-usage). Standard hosted runners are free for public repositories, subject to GitHub terms. Cloudflare Pages has a [Free-plan build limit](https://developers.cloudflare.com/pages/platform/limits/).

## Data and failure policy

One provider + real plan name + currency = one record. Conflicting prices are dropped. No price is derived from an aggregate starting-at number. Source failures remove that provider's offers in the next dataset. The builder removes records over the configured freshness window or a disclosed expiry. Unknown offer end dates are omitted, not invented. Check official checkout before committing to any contract.

The initial IONOS adapter extracts the visible US VPS+ plan cards, including introductory duration and minimum term. Other providers use a conservative Product/Offer structured-data adapter; if the source omits unambiguous plan-level billing information, no price is published. Unsupported parsing is visible rather than hidden.

## Monetization, when approved

Approved software affiliate placements are listed in `MONETIZATION.md`. Hosting provider rows currently use direct official links; the fourth column accepts an approved provider-specific affiliate destination. Links get disclosure and `rel=sponsored` automatically. No invented revenue or commission; no cookie injection, self-referral or brand bidding. A website is not an affiliate approval.

## Move to a custom domain

After registration, activate it in Pages and DNS, set `base_url` and `domain` in `site-config/site.conf`, rebuild and verify every canonical and sitemap URL. Domain age, repository commits and structured data do not guarantee rankings or rich results.

## AI Tools

The `/ai-tools/` collection is manually reviewed editorial content with official product sources and no invented coupons or prices. `site-config/site.conf` controls `ai_tools_enabled` and `ai_content_updated`. `ai_content.py` contains the guides. These dates are independent of automated VPS fetch timestamps. Disable the flag to remove the collection and its navigation/sitemap entries. Product listings use direct official links; designated hub and workflow placements contain labelled affiliate advertisements.
