# Parts Catalog — Anti-Patterns

## 2026-04-07 — BrickLink API requires seller registration
**Context:** Attempted to get API credentials for price guide data
**What happened:** Registration page (/v2/api/register_consumer.page) shows "Seller Only Area"
**Root cause:** BrickLink restricts API access to registered sellers
**Lesson:** Don't plan pipelines around BrickLink API without verifying seller status first. Use Rebrickable API as the free alternative.

## 2026-04-07 — Cowork sandbox blocks CDN downloads
**Context:** Attempted to download Rebrickable CSV dumps inside Cowork session
**What happened:** curl/urllib to cdn.rebrickable.com returns exit code 56 (connection reset)
**Root cause:** Cowork sandbox egress proxy blocks non-allowlisted domains
**Lesson:** Scripts that download data must be designed to run locally on user's machine, not in the sandbox. Write the script in Cowork, run it outside.
