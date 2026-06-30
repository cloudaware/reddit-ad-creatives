#!/usr/bin/env python3
"""
Reddit Ads API — OAuth token helper.

Prerequisite: register an app at https://www.reddit.com/prefs/apps (type "web app")
and have campaign-management allow-listing approved.

Set these env vars first (keep secrets OUT of source control / chat):
    export REDDIT_CLIENT_ID=...
    export REDDIT_CLIENT_SECRET=...
    export REDDIT_REDIRECT_URI=http://localhost:8080      # must match the app's redirect

USAGE
  Step 1 — print the authorize URL, open it in a browser, approve, then copy the
           `code` value from the redirected URL:
        python3 reddit_oauth_helper.py auth-url

  Step 2 — exchange that code for tokens (prints access_token + refresh_token):
        export REDDIT_AUTH_CODE=<code-from-redirect>
        python3 reddit_oauth_helper.py exchange

  Step 3 — later, mint a fresh access token from the saved refresh token:
        export REDDIT_REFRESH_TOKEN=<refresh-token>
        python3 reddit_oauth_helper.py refresh

  Verify access (read-only) once you have an access token:
        export REDDIT_ACCESS_TOKEN=<access-token>
        python3 reddit_oauth_helper.py whoami
"""
import os, sys, json, base64, stat, urllib.parse, urllib.request

AUTH_BASE  = "https://www.reddit.com/api/v1/authorize"
TOKEN_URL  = "https://www.reddit.com/api/v1/access_token"
ADS_API    = "https://ads-api.reddit.com/api/v3"
SCOPES     = "adsread,adsedit"   # Reddit Ads API scopes are comma-separated; adsread=read, adsedit=write
UA         = "cloudaware-ads-deployer/0.1 by u/your_reddit_user"   # set a real UA
TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reddit_tokens.json")

def _save_tokens(tok):
    """Write tokens to a 0600 local file instead of printing them to stdout/chat."""
    with open(TOKEN_FILE, "w") as fh:
        json.dump(tok, fh, indent=2)
    os.chmod(TOKEN_FILE, stat.S_IRUSR | stat.S_IWUSR)
    keys = ", ".join(k for k in tok if k != "access_token" and k != "refresh_token")
    print(f"Saved tokens to {TOKEN_FILE} (chmod 600). "
          f"Contains: {'access_token ' if 'access_token' in tok else ''}"
          f"{'refresh_token ' if 'refresh_token' in tok else ''}"
          f"(values NOT printed). Other fields: {keys}")

def env(k, required=True):
    v = os.environ.get(k)
    if required and not v:
        sys.exit(f"Missing env var: {k}")
    return v

def _post(url, data, basic=None):
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("User-Agent", UA)
    if basic:
        tok = base64.b64encode(f"{basic[0]}:{basic[1]}".encode()).decode()
        req.add_header("Authorization", f"Basic {tok}")
    with urllib.request.urlopen(req) as r:
        return json.load(r)

def _get(url, bearer):
    req = urllib.request.Request(url, method="GET")
    req.add_header("User-Agent", UA)
    req.add_header("Authorization", f"Bearer {bearer}")
    with urllib.request.urlopen(req) as r:
        return json.load(r)

def auth_url():
    cid = env("REDDIT_CLIENT_ID"); redirect = env("REDDIT_REDIRECT_URI")
    q = {
        "client_id": cid, "response_type": "code", "state": "cloudaware",
        "redirect_uri": redirect, "duration": "permanent", "scope": SCOPES,
    }
    print(AUTH_BASE + "?" + urllib.parse.urlencode(q, safe=","))
    print("\nOpen the URL, approve, then copy the `code=` value from the redirect.")

def exchange():
    cid = env("REDDIT_CLIENT_ID"); sec = env("REDDIT_CLIENT_SECRET")
    redirect = env("REDDIT_REDIRECT_URI"); code = env("REDDIT_AUTH_CODE")
    out = _post(TOKEN_URL, {"grant_type": "authorization_code", "code": code,
                            "redirect_uri": redirect}, basic=(cid, sec))
    if "access_token" not in out:
        sys.exit("Token exchange failed: " + json.dumps(out))
    _save_tokens(out)

def refresh():
    cid = env("REDDIT_CLIENT_ID"); sec = env("REDDIT_CLIENT_SECRET")
    rt = os.environ.get("REDDIT_REFRESH_TOKEN")
    if not rt and os.path.exists(TOKEN_FILE):
        rt = json.load(open(TOKEN_FILE)).get("refresh_token")
    if not rt:
        sys.exit("No refresh token (set REDDIT_REFRESH_TOKEN or run exchange first).")
    out = _post(TOKEN_URL, {"grant_type": "refresh_token", "refresh_token": rt},
                basic=(cid, sec))
    if "access_token" not in out:
        sys.exit("Refresh failed: " + json.dumps(out))
    if "refresh_token" not in out:   # reddit may omit it on refresh; keep the old one
        out["refresh_token"] = rt
    _save_tokens(out)

def _access_token():
    at = os.environ.get("REDDIT_ACCESS_TOKEN")
    if not at and os.path.exists(TOKEN_FILE):
        at = json.load(open(TOKEN_FILE)).get("access_token")
    if not at:
        sys.exit("No access token (run exchange/refresh first).")
    return at

def whoami():
    at = _access_token()
    # read-only probe: if this returns your ad accounts, campaign-management access works
    try:
        out = _get(f"{ADS_API}/me/ad_accounts", at)
        print(json.dumps(out, indent=2))
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode()[:500]}")
        print("\n403/404 here usually means the app is not allow-listed for campaign management yet.")

CMDS = {"auth-url": auth_url, "exchange": exchange, "refresh": refresh, "whoami": whoami}
if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in CMDS:
        sys.exit(__doc__)
    CMDS[sys.argv[1]]()
