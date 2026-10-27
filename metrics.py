"""Collect public metrics into metrics.json.

Sources, in order of reliability:
  · GitHub REST API            (no auth needed; 60 req/h per IP)
  · GreasyFork user JSON       (CORS-enabled, but a cron is tidier than browser fetches)
  · pypistats.org API          (no CORS header, so it must be fetched server-side)
  · RosettaCode MediaWiki API  (no CORS header, so also server-side)

All four sources are plain HTTPS; no browser needed.
Run:  python metrics.py [--out metrics.json]
"""
import argparse, datetime, json, os, sys, urllib.request

# 用带联系方式的 UA：RosettaCode 会拒绝伪装成浏览器的客户端（403），而且这也是 API 礼仪
UA = "resume-metrics/1.0 (+https://github.com/yhm138/resume)"

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


SE_SITES = {"codegolf": 110802, "stackoverflow": 15497427,
            "mathematica": 79318, "math": 909868}


def stackexchange():
    """Public API, one call per site; the ids were resolved once from the display name."""
    total, parts = 0, {}
    for site, uid in SE_SITES.items():
        d = get_json("https://api.stackexchange.com/2.3/users/%d?site=%s&filter=default"
                     % (uid, site))
        rep = (d.get("items") or [{}])[0].get("reputation")
        if rep is None:
            raise ValueError("no reputation for %s" % site)
        parts[site] = int(rep)
        total += int(rep)
    return {"stackexchange_rep": total, "stackexchange_by_site": parts}


def rosetta():
    """RosettaCode runs MediaWiki at /w/api.php — the edit count is a first-class field.

    The site sits behind bot protection that rejects datacenter IPs outright (HTTP 403
    from GitHub Actions), so a failure here is expected and the previous value wins.
    """
    url = ("https://rosettacode.org/w/api.php?action=query&list=users"
           "&ususers=%s&usprop=editcount&format=json" % ROSETTA_USER)
    d = get_json(url)
    users = (d.get("query") or {}).get("users") or []
    if not users or "editcount" not in users[0]:
        raise ValueError("editcount missing: %r" % d)
    return {"rosetta_edits": int(users[0]["editcount"])}


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
                     ("rosetta", rosetta)):
        try:
            data.update(fn())
            print("ok   %-11s" % name)
        except Exception as exc:                      # keep the previous value
            failed.append(name)
            print("fail %-11s %s" % (name, exc), file=sys.stderr)

    if failed:
        data["stale"] = failed

    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    print("wrote", args.out, data)


if __name__ == "__main__":
    main()
