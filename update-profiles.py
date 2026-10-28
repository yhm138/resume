# -*- coding: utf-8 -*-
"""Collect the three profile counters that have no public CORS, and publish profiles.json.

Why this runs locally instead of in the Cloudflare Worker:
  * OEIS, Observable and Code360 all omit Access-Control-Allow-Origin, so the page
    cannot fetch them in the browser.
  * Code360 additionally sits behind Akamai and answers 403 to datacenter IPs
    (verified against r.jina.ai and api.allorigins.win), so a Worker cannot fetch it.
  * From a residential connection all three respond normally.

Output: profiles.json in the repository. Published with plain git so the page can read
it from raw.githubusercontent.com. Nothing is written when the numbers did not change,
so idle runs do not create commits.
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(REPO, "profiles.json")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

OEIS_USER = "Haomin%20Yang"
C360_UUID = "8d5253e5-771f-4039-9fa0-cd51de2b0639"
OBS_USER = "@aspen1382020"


def fetch(url, headers=None, timeout=45):
    h = {"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def oeis():
    """Distinct sequences touched and revision rows, across all history pages."""
    seqs, revs, start, pages = set(), 0, 0, 0
    while start <= 400:
        body = fetch("https://oeis.org/history?user=%s&start=%d" % (OEIS_USER, start))
        pages += 1
        revs += body.count("class=seqnum")
        seqs.update(re.findall(r'href="(/A\d{6})"', body))
        if "older changes" not in body:
            break
        start += 10
        time.sleep(0.4)          # be polite to OEIS
    if pages == 0:
        raise RuntimeError("no history page parsed")
    return {"sequences": len(seqs), "revisions": revs}


def code360():
    base = "https://www.naukri.com/code360/api/v3/public_section"
    hdr = {"Accept": "application/json",
           "Referer": "https://www.naukri.com/code360/profile/" + C360_UUID,
           "Origin": "https://www.naukri.com"}
    details = json.loads(fetch(
        base + "/profile/user_details?uuid=%s&request_differentiator=%d"
               "&app_context=publicsection&naukri_request=true" % (C360_UUID, int(time.time() * 1000)),
        hdr))["data"]
    streak = json.loads(fetch(
        base + "/streaks/fetch_curr_and_long_streak?uuid=%s&request_differentiator=%d"
               "&app_context=publicsection&naukri_request=true" % (C360_UUID, int(time.time() * 1000)),
        hdr))["data"]
    domains = ("dsa_domain_data", "web_domain_data", "analytics_domain_data")
    problems = sum(details[d]["problem_count_data"]["total_count"] for d in domains)
    return {"problems": problems,
            "points": details.get("user_exp"),
            "longest_streak": streak.get("longest_streak")}


def observable():
    docs = json.loads(fetch("https://api.observablehq.com/user/%s/documents" % OBS_USER,
                            {"Accept": "application/json",
                             "Referer": "https://observablehq.com/@aspen1382020"}))
    notebooks = [d for d in docs if d.get("type") == "notebook_reader"]
    return {"notebooks": len(notebooks), "likes": sum(d.get("likes") or 0 for d in notebooks)}


def hackerrank():
    """Profile page is server-rendered: count badge tiles and certificate links.

    The legacy /rest/hackers/<user>/badges endpoint is not used: it lists the five
    domains the account has touched (Problem Solving, Java, Python, SQL, Ruby),
    which is not what the profile shows under Badges.
    """
    body = fetch("https://www.hackerrank.com/profile/aspen1382020",
                 {"Accept": "text/html,application/xhtml+xml"})
    return {"badges": body.count('class="hacker-badge"'),
            "certificates": body.count("certificate-link")}


def load_previous():
    if not os.path.exists(OUT):
        return {}
    try:
        with open(OUT, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def main():
    prev = load_previous()
    result = {"oeis": {}, "observable": {}, "code360": {}, "hackerrank": {}}
    stale = []
    for key, fn in (("oeis", oeis), ("observable", observable), ("code360", code360),
                    ("hackerrank", hackerrank)):
        try:
            result[key] = fn()
        except Exception as e:
            print("FAIL %s: %s: %s" % (key, type(e).__name__, e))
            result[key] = prev.get(key, {})
            stale.append(key)
        time.sleep(1)
    if not all(result[k] for k in result):
        print("all sources failed, nothing to publish")
        return 2

    result["stale"] = stale
    comparable = {k: v for k, v in prev.items() if k != "generated_at"}
    if comparable == result:
        print("unchanged:", json.dumps(result, ensure_ascii=False))
        return 0

    result = dict(result)
    result["generated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    result["stale"] = stale
    ordered = {"generated_at": result["generated_at"], "stale": stale,
               "oeis": result["oeis"], "observable": result["observable"],
               "code360": result["code360"], "hackerrank": result["hackerrank"]}
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(ordered, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, OUT)
    changed = [k for k in ("oeis", "observable", "code360", "hackerrank")
               if prev.get(k) != result[k]]
    print("wrote profiles.json, changed:", ",".join(changed) or "metadata only")

    def git(*args):
        return subprocess.run(["git", "-C", REPO] + list(args), capture_output=True, text=True,
                              timeout=120)

    if git("status", "--porcelain", "profiles.json").stdout.strip():
        git("add", "profiles.json")
        git("-c", "user.name=yhm138", "-c", "user.email=aspen1382020@gmail.com",
            "commit", "-m", "chore: refresh profile counters")
        push = git("push", "origin", "main")
        if push.returncode != 0:
            print("push failed:", push.stderr.strip()[:400])
            return 1
        print("pushed:", git("log", "-1", "--oneline").stdout.strip())
    else:
        print("nothing to commit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
