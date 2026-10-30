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
CF_HANDLE = "yhm7000_"
NC_UID = "473856205"
CSDN_USER = "weixin_45183579"
JUEJIN_UID = "935003303452199"
GITEE_USER = "yhm138"
MASTODON_ACCT = "aspen138"
BSKY_HANDLE = "aspen138.bsky.social"


def fetch(url, headers=None, timeout=45):
    h = {"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def post_json(url, payload, headers=None, timeout=45):
    h = {"User-Agent": UA, "Accept": "application/json", "Content-Type": "application/json"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=h, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


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


def codeforces():
    """Public API, no key. /user.status is ~150 KB, which is why the page does not
    fetch it itself; the solved count is the number of distinct accepted problems."""
    info = json.loads(fetch("https://codeforces.com/api/user.info?handles=" + CF_HANDLE))["result"][0]
    time.sleep(1)
    subs = json.loads(fetch("https://codeforces.com/api/user.status?handle=%s&from=1&count=10000"
                            % CF_HANDLE))["result"]
    solved = set()
    for s in subs:
        if s.get("verdict") != "OK":
            continue
        p = s.get("problem", {})
        solved.add("%s:%s" % (p.get("contestId") or p.get("problemsetName"), p.get("index")))
    return {"rating": info.get("rating"),
            "max_rating": info.get("maxRating"),
            "rank": info.get("rank"),
            "max_rank": info.get("maxRank"),
            "solved": len(solved),
            "submissions": len(subs)}


def nowcoder():
    """Contest profile + practice page are server-rendered; no CORS, so only this script
    can read them. Values sit in <div class="state-num">N</div><span>LABEL</span>."""
    profile = fetch("https://ac.nowcoder.com/acm/contest/profile/" + NC_UID,
                    {"Accept": "text/html,application/xhtml+xml"})
    practice = fetch("https://ac.nowcoder.com/acm/contest/profile/" + NC_UID + "/practice-coding",
                     {"Accept": "text/html,application/xhtml+xml"})

    def stat(html, label):
        m = re.search(r'class="state-num[^"]*">([^<]+)</div>\s*<span>' + re.escape(label) + r'</span>',
                      html)
        return m.group(1).strip() if m else None

    def as_int(v):
        try:
            return int(v)
        except (TypeError, ValueError):
            return v

    return {"rating": as_int(stat(profile, "Rating")),
            "rating_rank": stat(profile, "Rating\u6392\u540d"),
            "rating_contests": as_int(stat(profile, "次Rating赛")),
            "contests": as_int(stat(profile, "次比赛")),
            "attempted": as_int(stat(practice, "题已挑战")),
            "passed": as_int(stat(practice, "题已通过")),
            "submissions": as_int(stat(practice, "次提交"))}


def csdn():
    """Profile page is server-rendered (no CORS). Numbers sit in
    <div class="user-profile-statistics-num">N</div><div ...-name">LABEL</div>."""
    body = fetch("https://blog.csdn.net/%s?type=blog" % CSDN_USER,
                 {"Accept": "text/html,application/xhtml+xml",
                  "Accept-Language": "zh-CN,zh;q=0.9"})
    if "安全验证" in body or "Security Verification" in body:
        raise RuntimeError("CSDN served a captcha page")
    pairs = {name: num for num, name in re.findall(
        r'user-profile-statistics-num"[^>]*>([^<]+)</div>\s*'
        r'<div class="user-profile-statistics-name"[^>]*>([^<]+)</div>', body)}
    text = re.sub(r"<[^>]+>", " ", body)

    def grab(pattern):
        m = re.search(pattern, text)
        return int(m.group(1).replace(",", "")) if m else None

    def as_int(v):
        try:
            return int(v.replace(",", ""))
        except (AttributeError, ValueError):
            return None

    return {"posts": as_int(pairs.get("原创")),
            "visits": as_int(pairs.get("总访问量")),
            "fans": as_int(pairs.get("粉丝")),
            "likes": grab(r"获得\s*([\d,]+)\s*次点赞"),
            "comments": grab(r"内容获得\s*([\d,]+)\s*次评论"),
            "favorites": grab(r"获得\s*([\d,]+)\s*次收藏"),
            "rank": grab(r"博客总排名\s*([\d,]+)\s*名")}


def juejin():
    """Public JSON APIs, no CORS. Articles are paginated; count them and sum views."""
    hdr = {"Accept": "application/json", "Referer": "https://juejin.cn/user/%s" % JUEJIN_UID}
    info = json.loads(fetch("https://api.juejin.cn/user_api/v1/user/get?user_id=%s" % JUEJIN_UID, hdr))["data"]
    posts = views = diggs = 0
    cursor = "0"
    for _ in range(20):
        page = post_json("https://api.juejin.cn/content_api/v1/article/query_list",
                         {"user_id": JUEJIN_UID, "cursor": cursor, "sort_type": 2, "limit": 20}, hdr)
        batch = page.get("data") or []
        if not batch:
            break
        for item in batch:
            a = item.get("article_info") or {}
            posts += 1
            views += a.get("view_count") or 0
            diggs += a.get("digg_count") or 0
        cursor = str(page.get("cursor") or "")
        if not cursor or len(batch) < 20:
            break
    return {"posts": posts, "views": views, "diggs": diggs,
            "followers": info.get("follower_count"), "power": info.get("power")}


def gitee():
    """Gitee's API has no CORS; commit counts come from the repo commits endpoint."""
    hdr = {"Accept": "application/json"}
    user = json.loads(fetch("https://gitee.com/api/v5/users/%s" % GITEE_USER, hdr))
    repos = json.loads(fetch("https://gitee.com/api/v5/users/%s/repos?per_page=100" % GITEE_USER, hdr))
    commits = 0
    for repo in repos:
        try:
            cs = json.loads(fetch("https://gitee.com/api/v5/repos/%s/commits?per_page=100" % repo["full_name"], hdr))
            commits += len(cs)
        except Exception:
            pass
    return {"repos": len(repos),
            "stars": sum(r.get("stargazers_count") or 0 for r in repos),
            "forks": sum(r.get("forks_count") or 0 for r in repos),
            "commits": commits,
            "followers": user.get("followers")}


def mastodon():
    acct = json.loads(fetch("https://mastodon.social/api/v1/accounts/lookup?acct=%s" % MASTODON_ACCT,
                            {"Accept": "application/json"}))
    return {"statuses": acct.get("statuses_count"),
            "followers": acct.get("followers_count"),
            "following": acct.get("following_count")}


def bluesky():
    p = json.loads(fetch("https://public.api.bsky.app/xrpc/app.bsky.actor.getProfile?actor=%s" % BSKY_HANDLE,
                         {"Accept": "application/json"}))
    return {"posts": p.get("postsCount"), "followers": p.get("followersCount"),
            "following": p.get("followsCount")}


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
    result = {"oeis": {}, "observable": {}, "code360": {}, "hackerrank": {},
              "codeforces": {}, "nowcoder": {}, "csdn": {}, "juejin": {},
              "gitee": {}, "mastodon": {}, "bluesky": {}}
    stale = []
    for key, fn in (("oeis", oeis), ("observable", observable), ("code360", code360),
                    ("hackerrank", hackerrank), ("codeforces", codeforces),
                    ("nowcoder", nowcoder), ("csdn", csdn), ("juejin", juejin),
                    ("gitee", gitee), ("mastodon", mastodon), ("bluesky", bluesky)):
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
               "code360": result["code360"], "hackerrank": result["hackerrank"],
               "codeforces": result["codeforces"], "nowcoder": result["nowcoder"],
               "csdn": result["csdn"], "juejin": result["juejin"], "gitee": result["gitee"],
               "mastodon": result["mastodon"], "bluesky": result["bluesky"]}
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(ordered, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, OUT)
    changed = [k for k in ("oeis", "observable", "code360", "hackerrank",
                          "codeforces", "nowcoder", "csdn", "juejin", "gitee",
                          "mastodon", "bluesky") if prev.get(k) != result[k]]
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
