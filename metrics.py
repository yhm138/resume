"""Collect public metrics into metrics.json.

Each source is a (primary, fallback) pair. A fallback only exists where a genuinely
equivalent second path exists — inventing one would silently change the number.

  github           API only
  greasyfork       API only
  pypi             pepy.tech  →  pypistats overall
  stackexchange    accounts page (rendered) only
  rosetta          contributions HTML  →  MediaWiki usercontribs API
  chrome           chrome-stats page (usually blocked by Cloudflare → treated as manual)

State carried between runs:
  fail_streak   per-source consecutive failures (drives the alerting workflow)
  sources       which path produced the current value (primary / fallback / manual)

Run:  python metrics.py [--out metrics.json]
"""
import argparse, datetime, json, os, re, sys, urllib.request

from playwright.sync_api import sync_playwright

UA = "resume-metrics/1.0 (+https://github.com/yhm138/resume)"
BROWSER_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

GH_USER = "yhm138"
GF_UID = "1177387"
PYPI_PKG = "bisc-algorithm"
ROSETTA_USER = "Aspen138"
ROSETTA_PAGE = "https://rosettacode.org/wiki/Special:Contributions/%s?limit=5000" % ROSETTA_USER
ROSETTA_API = ("https://rosettacode.org/w/api.php?action=query&list=usercontribs"
               "&ucuser=%s&uclimit=500&ucprop=title|flags&format=json" % ROSETTA_USER)
SE_ACCOUNTS = "https://stackexchange.com/users/21083779/138-aspen?tab=accounts"
CHROME_URL = "https://chrome-stats.com/a/Q2hyb21lV2ViU3RvcmVEZXY"

STREAK_ALERT = 3          # mirrors the workflow threshold


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def get_text(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read().decode("utf-8", "replace")


# ---------------------------------------------------------------- github
def github():
    u = get_json("https://api.github.com/users/%s" % GH_USER)
    return {"github_repos": u.get("public_repos")}


# ---------------------------------------------------------------- greasyfork
def greasyfork():
    u = get_json("https://api.greasyfork.org/users/%s.json" % GF_UID)
    scripts = u.get("scripts") or []
    installs = sum(int(s.get("total_installs") or 0) for s in scripts)
    return {"greasyfork_scripts": len(scripts), "greasyfork_installs": installs}


# ---------------------------------------------------------------- pypi
def pypi_pepy():
    d = get_json("https://pepy.tech/api/v2/projects/%s" % PYPI_PKG)
    return {"pypi_total": int(d["total_downloads"])}


def pypi_pypistats():
    """Fallback. pypistats keeps only a recent window, so the number comes out lower —
    which is exactly why the producing path is recorded in `sources`."""
    d = get_json("https://pypistats.org/api/packages/%s/overall" % PYPI_PKG)
    total = sum(int(r["downloads"]) for r in d.get("data", []))
    if not total:
        raise ValueError("pypistats returned no rows")
    return {"pypi_total": total}


# ---------------------------------------------------------------- stack exchange
SE_JS = """() => [...document.querySelectorAll('.account-stat')]
    .map(e => { const m = (e.innerText || '').match(/([\\d,]+)\\s*reputation/);
                return m ? +m[1].replace(/,/g, '') : null; })
    .filter(x => x !== null)"""


def stackexchange():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(user_agent=BROWSER_UA)
        page.goto(SE_ACCOUNTS, wait_until="networkidle", timeout=90000)
        reps = page.evaluate(SE_JS)
        browser.close()
    if not reps:
        raise ValueError("no reputation rows found")
    return {"stackexchange_rep": sum(reps), "stackexchange_sites": len(reps)}


# ---------------------------------------------------------------- rosetta
def rosetta_html():
    html = get_text(ROSETTA_PAGE)
    if "Just a moment" in html[:2000]:
        raise RuntimeError("blocked by Cloudflare challenge")
    titles = set()
    for m in re.finditer(r"<a[^>]*>", html):
        tag = m.group(0)
        if "mw-contributions-title" not in tag:
            continue
        tm = re.search(r'title="([^"]+)"', tag)
        if not tm:
            continue
        title = tm.group(1)
        if title.startswith("User:") or title.startswith("File:"):
            continue
        titles.add(title)
    if not titles:
        raise ValueError("no contribution titles found")
    return {"rosetta_tasks": len(titles), "rosetta_new": html.count("newpage")}


def rosetta_api():
    """Fallback for when the contributions markup changes: ask the API for the same rows.

    ucprop=title|flags carries the `new` flag, so page creations are still measurable.
    One call caps at 500 rows, which is a lower bound for very active editors.
    """
    d = get_json(ROSETTA_API)
    items = (d.get("query") or {}).get("usercontribs") or []
    if not items:
        raise ValueError("usercontribs empty")
    titles = {i["title"] for i in items
              if not i["title"].startswith("User:") and not i["title"].startswith("File:")}
    new = sum(1 for i in items if "new" in (i.get("flags") or []))
    return {"rosetta_tasks": len(titles), "rosetta_new": new}


# ---------------------------------------------------------------- chrome
CHROME_JS = """() => {
    const t = document.body.innerText;
    const m = t.match(/Users?\\s*[:：]\\s*([\\d,]{2,})/i);
    return m ? +m[1].replace(/,/g, '') : null;
}"""


def chrome():
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--disable-blink-features=AutomationControlled"])
        ctx = browser.new_context(user_agent=BROWSER_UA, locale="en-US",
                                  viewport={"width": 1366, "height": 900})
        page = ctx.new_page()
        page.goto(CHROME_URL, wait_until="domcontentloaded", timeout=90000)
        page.wait_for_timeout(5000)
        body = page.inner_text("body")
        if "Just a moment" in page.title() or "security verification" in body:
            browser.close()
            raise RuntimeError("blocked by Cloudflare challenge")
        val = page.evaluate(CHROME_JS)
        browser.close()
    if val is None:
        raise ValueError("user count not found")
    return {"chrome_users": val}


# ---------------------------------------------------------------- driver
SOURCES = [
    ("github", github, None),
    ("greasyfork", greasyfork, None),
    ("pypi", pypi_pepy, pypi_pypistats),
    ("stackexchange", stackexchange, None),
    ("rosetta", rosetta_html, rosetta_api),
    ("chrome", chrome, None),
]

MANUAL = {"chrome"}          # known-blocked; never raises an alert


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="metrics.json")
    args = ap.parse_args()

    data = {}
    if os.path.exists(args.out):
        try:
            with open(args.out, encoding="utf-8") as fh:
                data = {k: v for k, v in json.load(fh).items() if k != "generated_at"}
        except Exception as exc:
            print("could not read previous metrics: %s" % exc, file=sys.stderr)

    streak = dict(data.get("fail_streak") or {})
    sources = dict(data.get("sources") or {})
    data["generated_at"] = (datetime.datetime.now(datetime.timezone.utc)
                            .replace(microsecond=0).isoformat().replace("+00:00", "Z"))

    for name, primary, fallback in SOURCES:
        try:
            data.update(primary())
            sources[name] = "primary"
            streak.pop(name, None)
            print("ok   %-14s primary" % name)
            continue
        except Exception as exc:
            print("warn %-14s primary failed: %s" % (name, exc), file=sys.stderr)

        if fallback is not None:
            try:
                data.update(fallback())
                sources[name] = "fallback"
                streak.pop(name, None)
                print("ok   %-14s fallback" % name)
                continue
            except Exception as exc:
                print("warn %-14s fallback failed: %s" % (name, exc), file=sys.stderr)

        if name in MANUAL:
            sources[name] = "manual"
            print("skip %-14s manual source, keeping previous value" % name, file=sys.stderr)
        else:
            streak[name] = min(int(streak.get(name, 0)) + 1, STREAK_ALERT + 2)
            print("fail %-14s keeping previous value (streak %d)"
                  % (name, streak[name]), file=sys.stderr)

    data["sources"] = sources
    data["fail_streak"] = streak
    data["stale"] = sorted(streak)

    for legacy in ("stackexchange_by_site", "pypi_last_month", "rosetta_edits"):
        data.pop(legacy, None)

    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")

    over = [k for k, v in streak.items() if v >= STREAK_ALERT]
    print("wrote", args.out)
    print("sources:", sources)
    print("alert threshold reached:", over if over else "none")


if __name__ == "__main__":
    main()
