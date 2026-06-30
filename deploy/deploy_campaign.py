#!/usr/bin/env python3
"""
Deploy the CloudAware CMDB "scale" campaign to Reddit Ads — everything PAUSED.

Hierarchy created:
  campaign (CLICKS / Traffic)
   ├─ ad group A  "Single-cloud / AWS at scale"  → AWS light creative
   │    └─ image post → ad
   └─ ad group B  "Multi-cloud at scale"         → multi-cloud light creative
        └─ image post → ad

Usage:
  python3 deploy_campaign.py            # DRY RUN — prints every payload, creates nothing
  python3 deploy_campaign.py --go       # actually create the objects (all PAUSED)

Reads the access token from reddit_tokens.json (never prints it).
"""
import os, sys, json, datetime, urllib.request, urllib.error

DRY = "--go" not in sys.argv
HERE = os.path.dirname(os.path.abspath(__file__))
API = "https://ads-api.reddit.com/api/v3"
UA  = "cloudaware-ads-deployer/0.1 by u/CloudawareLabs"

AD_ACCOUNT_ID = "a2_j9lke3bask24"
FUNDING_ID    = "1849230"
PROFILE_ID    = "t2_2hl740xkqa"
GEO           = ["US"]
DAILY_BUDGET  = 50_000_000          # $50.00/day in micro-USD
BID_VALUE     = 1_000_000           # $1.00 max CPC in micro-USD (CPC ad groups require a bid)
LANDING       = "https://cloudaware.com/cmdb/"
DISPLAY_URL   = "cloudaware.com"
RAW = "https://raw.githubusercontent.com/cloudaware/reddit-ad-creatives/main/images"

START_TIME = (datetime.datetime.now(datetime.timezone.utc)
              + datetime.timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

CAMPAIGN = {
    "name": "CloudAware CMDB — Scale — Traffic — 2026-06",
    "configured_status": "PAUSED",
    "objective": "CLICKS",
    "funding_instrument_id": FUNDING_ID,
}

AD_GROUPS = [
    {
        "key": "aws",
        "name": "Single-cloud / AWS at scale",
        "communities": ["aws", "sysadmin", "devops", "Terraform"],  # targeting uses NAMES, not t5_ ids
        "image": f"{RAW}/scale-aws-light.png",
        "utm": "aws-light",
        "headline": ("Every public IP across 5,000+ AWS accounts — in one question. "
                     "CloudAware's MCP interface turns plain English into answers across your whole AWS estate."),
    },
    {
        "key": "multicloud",
        "name": "Multi-cloud at scale",
        "communities": ["cloudcomputing", "cloudengineering", "googlecloud", "AZURE", "ITManagers"],
        "image": f"{RAW}/scale-multicloud-light.png",
        "utm": "multicloud-light",
        "headline": ("One question across AWS, Azure & GCP. CloudAware unifies every account into one "
                     "inventory you can query in plain English via MCP — answers in seconds."),
    },
]

def token():
    p = os.path.join(HERE, "reddit_tokens.json")
    return json.load(open(p))["access_token"]

def post(path, data, label):
    body = {"data": data}
    if DRY:
        print(f"\n--- [DRY] POST {path}   ({label}) ---")
        print(json.dumps(body, indent=2))
        return {"id": f"<{label}-id>"}
    req = urllib.request.Request(API + path, data=json.dumps(body).encode(), method="POST")
    req.add_header("Authorization", f"Bearer {token()}")
    req.add_header("User-Agent", UA)
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req) as r:
            out = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"\n!! HTTP {e.code} on {label} ({path}):\n{e.read().decode()[:1200]}")
    obj = out.get("data", out)
    print(f"  ✓ {label}: id={obj.get('id')}")
    return obj

def utm(content):
    return (f"{LANDING}?utm_source=reddit&utm_medium=cpc"
            f"&utm_campaign=cmdb-scale-2026-06&utm_content={content}")

def main():
    mode = "DRY RUN (nothing will be created)" if DRY else "LIVE — creating PAUSED objects"
    print(f"=== Reddit Ads deploy — {mode} ===")
    print(f"ad_account={AD_ACCOUNT_ID}  budget=${DAILY_BUDGET/1e6:.0f}/day/adgroup  geo={GEO}  start≈{START_TIME}")

    existing = os.environ.get("REDDIT_CAMPAIGN_ID")
    if existing:
        print(f"  (reusing existing campaign {existing})")
        cid = existing
    else:
        cid = post(f"/ad_accounts/{AD_ACCOUNT_ID}/campaigns", CAMPAIGN, "campaign")["id"]

    summary = []
    for g in AD_GROUPS:
        reuse_ag = os.environ.get("REDDIT_ADGROUP_" + g["key"].upper())
        if reuse_ag:
            print(f"  (reusing existing ad_group {g['key']} = {reuse_ag})")
            ag = {"id": reuse_ag}
        else:
            ag = post(f"/ad_accounts/{AD_ACCOUNT_ID}/ad_groups", {
                "name": g["name"],
                "campaign_id": cid,
                "configured_status": "PAUSED",
                "goal_type": "DAILY_SPEND",
                "goal_value": DAILY_BUDGET,
                "bid_strategy": "MANUAL_BIDDING",
                "bid_type": "CPC",
                "bid_value": BID_VALUE,
                "start_time": START_TIME,
                "targeting": {"geolocations": GEO, "communities": g["communities"]},
            }, f"ad_group[{g['utm']}]")

        dest = utm(g["utm"])
        pp = post(f"/profiles/{PROFILE_ID}/posts", {
            "type": "IMAGE",
            "headline": g["headline"],
            "allow_comments": False,
            "content": [{
                "media_url": g["image"],
                "destination_url": dest,
                "display_url": DISPLAY_URL,
                "call_to_action": "Learn More",
            }],
        }, f"post[{g['utm']}]")

        ad = post(f"/ad_accounts/{AD_ACCOUNT_ID}/ads", {
            "name": f"CMDB scale — {g['utm']}",
            "ad_group_id": ag["id"],
            "configured_status": "PAUSED",
            "profile_id": PROFILE_ID,
            "post_id": pp["id"],
            "click_url": dest,
            "campaign_objective_type": "CLICKS",
        }, f"ad[{g['utm']}]")

        summary.append((g["name"], ag["id"], pp["id"], ad["id"]))

    print("\n=== SUMMARY ===")
    print(f"campaign: {cid}")
    for name, agid, pid, adid in summary:
        print(f"  {name}: ad_group={agid}  post={pid}  ad={adid}")
    if DRY:
        print("\nDRY RUN complete. Re-run with --go to create these (all PAUSED).")
    else:
        print(f"\nLIVE. Review/activate at: https://ads.reddit.com/")

if __name__ == "__main__":
    main()
