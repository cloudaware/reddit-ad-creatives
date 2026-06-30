# reddit-ad-creatives

CloudAware's Reddit advertising creative library — generator scripts, rendered ad images, and deploy tooling for the Reddit Ads API.

This repo is **public on purpose**: the Reddit Ads API has no media-upload endpoint, so ad images must be served from public URLs that Reddit fetches (once) at ad-creation time. The raw image URLs below are referenced as `media_url` in the deploy script.

## Structure

```
images/        Rendered 1500x1020 ad creatives (PNG)
generators/    Pillow scripts that produce the images (reproducible)
deploy/        Reddit Ads API tooling (OAuth helper + campaign deploy script)
```

## Current creatives

CloudAware CMDB / asset-management campaign — "ask once, get answers across every cloud" (MCP / scale positioning).

| File | Theme | Audience |
|------|-------|----------|
| `images/scale-aws-light.png` | Light | Single-cloud at scale (large AWS estates) |
| `images/scale-multicloud-light.png` | Light | Multi-cloud at scale (AWS + Azure + GCP) |
| `images/scale-aws-dark.png` | Dark | A/B variant of the AWS creative |
| `images/scale-multicloud-dark.png` | Dark | A/B variant of the multi-cloud creative |

### Raw URLs (what Reddit fetches)

```
https://raw.githubusercontent.com/cloudaware/reddit-ad-creatives/main/images/scale-aws-light.png
https://raw.githubusercontent.com/cloudaware/reddit-ad-creatives/main/images/scale-multicloud-light.png
https://raw.githubusercontent.com/cloudaware/reddit-ad-creatives/main/images/scale-aws-dark.png
https://raw.githubusercontent.com/cloudaware/reddit-ad-creatives/main/images/scale-multicloud-dark.png
```

## Regenerating images

```bash
python3 -m venv venv && ./venv/bin/pip install Pillow
./venv/bin/python generators/make_light_ads.py
```

Brand tokens (dark `#1D2023`, teal `#04A6A8`, cyan `#24EDFF`, magenta `#FF3C84`) match cloudaware.com.

## Security

Secrets are **never** committed — see `.gitignore`. OAuth client secret and tokens live only in local, git-ignored files (`.reddit_creds`, `reddit_tokens.json`). The deploy tooling reads them at runtime and never prints token values.
