"""Collect public metrics into metrics.json.

Sources:
  · GitHub REST API               — plain HTTPS
  · GreasyFork user JSON          — plain HTTPS, CORS-friendly
  · pepy.tech API                 — plain HTTPS, lifetime PyPI downloads
  · stackexchange.com accounts    — rendered page, every network site at once
  · rosettacode.org contributions — rendered page, distinct task pages
  · chrome-stats.com              — rendered page (Cloudflare may block CI)

The last three need a browser, so Playwright is a hard dependency.
Run:  python metrics.py [--out metrics.json]
"""
import argparse, datetime, json, os, re, sys, urllib.request

from playwright.sync_api import sync_playwright

# 普通 API 用带联系方式的 UA（API 礼仪）
UA = "resume-metrics/1.0 (+https://github.com/yhm138/resume)"
# 需要浏览器的站点用真实浏览器 UA，否则直接 403
BROWSER_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

GH_USER = "yhm138"
GF_UID = "1177387"
PYPI_PKG = "bisc-algorithm"
ROSETTA_USER = "Aspen138"


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def github():
    u = get_json("https://api.github.com/users/%s" % GH_USER)
    return {"github_repos": u.get("public_repos")}


def greasyfork():
    u = get_json("https://api.greasyfork.org/users/%s.json" % GF_UID)
    scripts = u.get("scripts") or []
    installs = sum(int(s.get("total_installs") or 0) for s in scripts)
    return {"greasyfork_scripts": len(scripts), "greasyfork_installs": installs}


def pypi():
    """pepy.tech keeps the lifetime count — the same source the PyPI badge links to."""
    d = get_json("https://pepy.tech/api/v2/projects/%s" % PYPI_PKG)
    return {"pypi_total": int(d["total_downloads"])}


SE_ACCOUNTS = "https://stackexchange.com/users/21083779/138-aspen?tab=accounts"
SE_JS = """() => [...document.querySelectorAll('.account-stat')]
    .map(e => { const m = (e.innerText || '').match(/([\\d,]+)\\s*reputation/);
                return m ? +m[1].replace(/,/g, '') : null; })
    .filter(x => x !== null)"""

CHROME_URL = "https://chrome-stats.com/a/Q2hyb21lV2ViU3RvcmVEZXY"
CHROME_JS = """() => {
    const t = document.body.innerText;
    const m = t.match(/([\\d,]{2,})\\s*(?:total\\s+)?users/i) || t.match(/users?\\s*[:：]?\\s*([\\d,]{2,})/i);
    return m ? +m[1].replace(/,/g, '') : null;
}"""


def _browser_page(url, timeout=90000):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--disable-blink-features=AutomationControlled"])
        ctx = browser.new_context(user_agent=BROWSER_UA, locale="en-US",
                                  viewport={"width": 1366, "height": 900})
        page = ctx.new_page()
        page.goto(url, wait_until="networkidle", timeout=timeout)
        out = page.evaluate  # noqa: F841  (kept for readability at call sites)
        return browser, ctx, page


def stackexchange():
    """All 100+ network sites, read off the public accounts page.

    The API's /associated endpoint needs an access token, and per-site ids would mean
    100+ calls, so the rendered page is the cheapest complete source.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(user_agent=BROWSER_UA)
        page.goto(SE_ACCOUNTS, wait_until="networkidle", timeout=90000)
        reps = page.evaluate(SE_JS)
        browser.close()
    if not reps:
        raise ValueError("no reputation rows found")
    return {"stackexchange_rep": sum(reps), "stackexchange_sites": len(reps)}


def chrome_extensions():
    """chrome-stats sits behind Cloudflare Turnstile; expect this to fail in CI."""
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--disable-blink-features=AutomationControlled"])
        ctx = browser.new_context(user_agent=BROWSER_UA, locale="en-US",
                                  viewport={"width": 1366, "height": 900})
        page = ctx.new_page()
        page.goto(CHROME_URL, wait_until="domcontentloaded", timeout=90000)
        page.wait_for_timeout(6000)
        if "Just a moment" in page.title() or "security verification" in page.inner_text("body"):
            browser.close()
            raise RuntimeError("blocked by Cloudflare challenge")
        val = page.evaluate(CHROME_JS)
        browser.close()
    if val is None:
        raise ValueError("user count not found")
    return {"chrome_users": val}


def rosetta():
    """Distinct RosettaCode task pages contributed to.

    Ported from the author's own userscript (greasyfork #487164): raw edit count rewards
    typo fixes, so the meaningful number is how many distinct tasks carry his code.
    User: and File: pages are excluded, as in the original script.

    The contributions page is plain server-rendered HTML, so no browser is needed —
    only the /w/api.php endpoint refuses non-browser clients.
    """
    url = ("https://rosettacode.org/wiki/Special:Contributions/%s?limit=5000"
           % ROSETTA_USER)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as r:
        html = r.read().decode("utf-8", "replace")

    titles = set()
    for m in re.finditer(r'<a[^>]*>', html):
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
    return {"rosetta_tasks": len(titles)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="metrics.json")
    args = ap.parse_args()

    # 以现有文件为底稿：某个源临时失败时保留上一次的值，而不是把它抹成 null。
    data = {}
    if os.path.exists(args.out):
        try:
            with open(args.out, encoding="utf-8") as fh:
                data = {k: v for k, v in json.load(fh).items() if k != "generated_at"}
            print("carried over %s" % sorted(data))
        except Exception as exc:
            print("could not read previous metrics: %s" % exc, file=sys.stderr)

    stamp = (datetime.datetime.now(datetime.timezone.utc)
             .replace(microsecond=0).isoformat().replace("+00:00", "Z"))
    data["generated_at"] = stamp

    failed = []
    for name, fn in (("github", github), ("greasyfork", greasyfork),
                     ("pypi", pypi), ("stackexchange", stackexchange),
                     ("rosetta", rosetta), ("chrome", chrome_extensions)):
        try:
            data.update(fn())
            print("ok   %-11s" % name)
        except Exception as exc:                      # keep the previous value
            failed.append(name)
            print("fail %-11s %s" % (name, exc), file=sys.stderr)

    # 旧字段即使被 carry over 到内存里，也不再写回文件
    for legacy in ("rosetta_edits", "stackexchange_by_site", "pypi_last_month"):
        data.pop(legacy, None)

    if failed:
        data["stale"] = failed

    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    print("wrote", args.out, data)


if __name__ == "__main__":
    main()
