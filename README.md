# vps-deals

Official-source VPS offers. Clear terms. No invented coupons.

Main site: deployment pending; no verified public URL yet.

![Brand mark](assets/logo.svg)

## What this is

A public, deterministic offer-monitoring pipeline for en-US. It reads official public pages, checks robots.txt and publishes only plans with identifiable names, current prices and billing conditions. Providers that cannot be verified remain visible without prices. No estimated search volumes, fake discounts or guaranteed-income claims.

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

`.ilang/site.ilang` is parsed by both scraper and builder. Edit the provider rows, brand or base_url, then run the pipeline. The regression test removes a provider and checks that its page and navigation disappear. The first version intentionally supports only en-US; add real regional source adapters before extending languages.

The scheduled workflow requests a check every six hours, at minute 17 UTC. Execution may be delayed or fail. Verification timestamps are genuine retrieval times, not claims that the price is still available. Scheduled public workflows can be disabled after inactivity by GitHub. See [GitHub schedule rules](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/disable-and-enable-workflows) and [Actions billing](https://docs.github.com/en/actions/concepts/billing-and-usage). Standard hosted runners are free for public repositories, subject to GitHub terms. Cloudflare Pages has a [Free-plan build limit](https://developers.cloudflare.com/pages/platform/limits/).

## Data and failure policy

One provider + real plan name + currency = one record. Conflicting prices are dropped. No price is derived from an aggregate starting-at number. Source failures remove that provider's offers in the next dataset. The builder removes records over the configured freshness window or a disclosed expiry. Unknown offer end dates are omitted, not invented. Check official checkout before committing to any contract.

The initial IONOS adapter extracts the visible US VPS+ plan cards, including introductory duration and minimum term. Other providers use a conservative Product/Offer structured-data adapter; if the source omits unambiguous plan-level billing information, no price is published. Unsupported parsing is visible rather than hidden.

## Monetization, when approved

No affiliate links or commissions are configured at launch. The fourth provider column accepts an approved provider-specific affiliate destination later. Links get disclosure and `rel=sponsored` automatically. Evaluate managed-hosting recurring offers only through a provider's official program and approved CJ/Impact or successor platform terms. No invented revenue or commission; no cookie injection, self-referral or brand bidding. A website is not an affiliate approval.

X and Facebook are deferred. Reuse the brand mark, tagline and main-site URL if accounts are created later. Do not post an unverified offer or automatically claim a largest discount without a verified comparison basis.

## Move to a custom domain

After registration, activate it in Pages and DNS, set `base_url` and `@SITE.domain` in `.ilang/site.ilang`, rebuild and verify every canonical and sitemap URL. Domain age, repository commits and structured data do not guarantee rankings or rich results.

站点规则用 I-Lang 协议描述，见 `.ilang/site.ilang`；协议说明： https://ilang.ai 。
