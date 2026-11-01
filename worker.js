/**
 * resume-metrics — a single-file Cloudflare Worker.  (v3)
 *
 * GET /metrics  → JSON, CORS-enabled, cached 10 minutes (what the résumé page reads).
 * GET /?nocache=1 → same JSON, cache bypassed (debugging).
 * GET /         → a small status page: every row, its value and its source state.
 *
 * Only sources that are fetchable from a server live here. GitHub / GreasyFork /
 * Stack Exchange per-site / Tianchi / SE badges are fetched by the page itself,
 * because those APIs already send Access-Control-Allow-Origin. Zhihu and the
 * Chrome Web Store reject datacenter IPs, so they are refreshed by the local
 * weekly task (web-stats.json / chrome-users.json), not here.
 *
 * A field is omitted when its source fails — the page then keeps whatever it had.
 *
 * v3 changes vs v2:
 *   - GreasyFork uses the canonical /en/users/<id>-<slug>.json URL (the old one 301s).
 *   - Bilibili / Douyin / LeetCode get a browser UA + referer; the old bot UA was
 *     being rejected, which is why those fields silently disappeared.
 *   - Bilibili falls back to x/relation/stat when the card endpoint fails.
 *   - RosettaCode falls back to the MediaWiki API with a browser UA.
 *   - Stack Exchange: accounts-page scrape first, API /associated as fallback.
 *   - Zhihu removed: it returns 403 for every datacenter IP, so it only ever
 *     produced an "unavailable" row (the page reads web-stats.json instead).
 *   - /?nocache=1 for debugging; status page shows the omitted-field list.
 */

const UA = "resume-metrics/3.0 (+https://github.com/yhm138/resume)";
// Chrome Web Store / Bilibili / Douyin / LeetCode only answer browser UAs.
const BROWSER_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " +
  "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36";
const TTL = 600;                     // seconds

const GF_UID = "1177387";
const PYPI_PKG = "bisc-algorithm";
const ROSETTA_PAGE = "https://rosettacode.org/wiki/Special:Contributions/Aspen138?limit=5000";
const ROSETTA_API = "https://rosettacode.org/w/api.php?action=query&list=usercontribs" +
  "&ucuser=Aspen138&uclimit=500&ucprop=title|flags&format=json";

const CORS = { "access-control-allow-origin": "*" };

function jsonResponse(obj, extraHeaders = {}) {
  return new Response(JSON.stringify(obj, null, 2), {
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": `public, max-age=${TTL}`,
      ...CORS,
      ...extraHeaders,
    },
  });
}

function htmlResponse(obj) {
  const rows = [
    ["GreasyFork installs", obj.greasyfork_installs, "greasyfork"],
    ["GreasyFork scripts", obj.greasyfork_scripts, "greasyfork"],
    ["PyPI downloads", obj.pypi_total, "pypi"],
    ["Stack Exchange reputation", obj.stackexchange_rep, "stackexchange"],
    ["Stack Exchange sites", obj.stackexchange_sites, "stackexchange"],
    ["RosettaCode tasks", obj.rosetta_tasks, "rosetta"],
    ["RosettaCode new pages", obj.rosetta_new, "rosetta"],
    ["Cnblogs total reads", obj.cnblogs_reads, "cnblogs"],
    ["Cnblogs posts", obj.cnblogs_posts, "cnblogs"],
    ["Bilibili followers", obj.bilibili_followers, "bilibili"],
    ["Bilibili videos", obj.bilibili_videos, "bilibili"],
    ["Bilibili likes", obj.bilibili_likes, "bilibili"],
    ["Douyin likes", obj.douyin_likes, "douyin"],
    ["Douyin posts", obj.douyin_posts, "douyin"],
    ["LeetCode solved", obj.leetcode_solved, "leetcode"],
    ["LeetCode rank", obj.leetcode_rank, "leetcode"],
    ["HackerRank badges", obj.hackerrank_badges, "hackerrank"],
    ["Codewars katas", obj.codewars_katas, "codewars"],
    ["Codewars kyu", obj.codewars_kyu, "codewars"],
    ["LeetCode.com solved", obj.leetcode_global_solved, "leetcodeGlobal"],
    ["LeetCode.com rank", obj.leetcode_global_rank, "leetcodeGlobal"],
  ];

  const missing = rows.filter(([, v]) => v === undefined).map(([label]) => label);

  const body = rows.map(([label, value, src]) => {
    const state = obj.sources?.[src] ?? "—";
    const bad = state === "unavailable" || value === undefined;
    const shown = value === undefined ? "—" : Number(value).toLocaleString("en-US");
    return `<tr><td>${label}</td><td class="num">${shown}</td>
      <td class="${bad ? "bad" : "ok"}">${state}</td></tr>`;
  }).join("");

  const html = `<!doctype html><meta charset="utf-8">
<title>resume-metrics</title>
<style>
  body{font:14px/1.6 ui-monospace,SFMono-Regular,Consolas,monospace;max-width:640px;margin:40px auto;padding:0 20px;color:#16181a;background:#f7f5f1}
  h1{font-size:15px;letter-spacing:.12em;text-transform:uppercase;color:#8a8f96;font-weight:600}
  table{border-collapse:collapse;width:100%}
  td{padding:7px 0;border-top:1px solid #d9d4c9}
  .num{text-align:right;font-variant-numeric:tabular-nums}
  .ok{color:#0f8a5f;text-align:right}.bad{color:#b3261e;text-align:right}
  .meta{margin-top:18px;color:#8a8f96;font-size:12px}
  .meta code{color:#123f4d}
  a{color:#123f4d}
</style>
<h1>resume-metrics</h1>
<table>${body}</table>
<p class="meta">
  generated <b>${obj.generated_at ?? "?"}</b> · cached ${TTL}s ·
  <a href="/metrics">/metrics JSON</a> · <a href="/?nocache=1">bypass cache</a><br>
  fetched by the page itself: GitHub · GreasyFork · SE per-site · SE badges · Tianchi<br>
  fetched by the local weekly task: Zhihu · Chrome Web Store · CSDN · 掘金 · Codeforces · 牛客 · OEIS ·
  Observable · Code360 · HackerRank certs · Gitee · Bluesky · Mastodon · ScriptCat · visitor map<br>
  ${missing.length ? `<span class="bad">omitted this run: ${missing.join(", ")}</span>` : "all fields present"}
</p>`;
  return new Response(html, {
    headers: { "content-type": "text/html; charset=utf-8", "cache-control": `public, max-age=${TTL}`, ...CORS },
  });
}

async function fetchText(url, { timeout = 20000, ua = UA, referer, accept = "text/html,application/json", cacheTtl = 0 } = {}) {
  const headers = { "user-agent": ua, accept, "accept-language": "en-US,en;q=0.9" };
  if (referer) headers.referer = referer;
  const init = { headers, signal: AbortSignal.timeout(timeout) };
  if (cacheTtl) init.cf = { cacheTtl, cacheEverything: true };
  const r = await fetch(url, init);
  if (!r.ok) throw new Error(`${url} → ${r.status}`);
  return r.text();
}

async function fetchJson(url, opts = {}) {
  const body = await fetchText(url, { ...opts, accept: "application/json" });
  try {
    return JSON.parse(body);
  } catch (_) {
    throw new Error(`${url} → non-JSON body (${body.slice(0, 60)})`);
  }
}

async function postJson(url, payload, { timeout = 20000, referer } = {}) {
  const origin = new URL(url).origin;
  const r = await fetch(url, {
    method: "POST",
    headers: {
      "user-agent": BROWSER_UA,
      "content-type": "application/json",
      accept: "application/json",
      "accept-language": "en-US,en;q=0.9",
      origin,
      referer: referer || origin + "/",
    },
    body: JSON.stringify(payload),
    signal: AbortSignal.timeout(timeout),
  });
  if (!r.ok) throw new Error(`${url} → ${r.status}`);
  const body = await r.text();
  try {
    return JSON.parse(body);
  } catch (_) {
    throw new Error(`${url} → non-JSON body (${body.slice(0, 60)})`);
  }
}

/* ---------------------------------------------------------------- sources */

// 2015 年以来的老接口，仍然免签名；改用规范地址，避免 301 把 CORS 弄丢。
async function greasyfork() {
  const u = await fetchJson(`https://api.greasyfork.org/en/users/${GF_UID}-138-aspen.json`);
  const scripts = u.scripts || [];
  if (!scripts.length) throw new Error("greasyfork: no scripts");
  return {
    greasyfork_scripts: scripts.length,
    greasyfork_installs: scripts.reduce((s, x) => s + (x.total_installs || 0), 0),
  };
}

async function pypi() {
  const d = await fetchJson(`https://pepy.tech/api/v2/projects/${PYPI_PKG}`);
  if (typeof d.total_downloads !== "number") throw new Error("pypi: no total_downloads");
  return { pypi_total: d.total_downloads };
}

// 主通道：账号页是服务端渲染的，账号行就在 HTML 里（118 站，与页面显示一致）。
// 备用通道：Stack Exchange API 的 associated（分页 100/页，117 站，口径略少一点）。
const SE_ACCOUNTS = "https://stackexchange.com/users/21083779/138-aspen?tab=accounts";

async function stackexchangeHtml() {
  const html = await fetchText(SE_ACCOUNTS, { timeout: 25000, ua: BROWSER_UA, cacheTtl: 600 });
  const reps = [...html.matchAll(
    /<div class="account-stat">\s*<span class="account-number">([\d,]+)<\/span>\s*<span class="cool">reputation<\/span>/g,
  )].map((m) => Number(m[1].replace(/,/g, "")));
  if (!reps.length) throw new Error("no reputation rows");
  return {
    stackexchange_rep: reps.reduce((a, b) => a + b, 0),
    stackexchange_sites: reps.length,
  };
}

// 注意：associated 不接 site 参数，带了会 400。
async function stackexchangeApi() {
  let rep = 0, sites = 0, page = 1, more = true;
  while (more && page <= 3) {
    const d = await fetchJson(
      `https://api.stackexchange.com/2.3/users/21083779/associated?pagesize=100&page=${page}`,
      { cacheTtl: 600 },
    );
    for (const it of d.items || []) {
      rep += Number(it.reputation) || 0;
      sites += 1;
    }
    more = !!d.has_more;
    page += 1;
  }
  if (!sites) throw new Error("se: no associated accounts");
  return { stackexchange_rep: rep, stackexchange_sites: sites };
}

// 贡献页是服务端渲染的；页面改版或被 Cloudflare 拦时退回 MediaWiki API。
async function rosettaHtml() {
  const html = await fetchText(ROSETTA_PAGE, { timeout: 25000, ua: BROWSER_UA, cacheTtl: 600 });
  if (html.slice(0, 2000).includes("Just a moment")) throw new Error("cloudflare challenge");
  const titles = new Set();
  for (const m of html.matchAll(/<a[^>]*>/g)) {
    const tag = m[0];
    if (!tag.includes("mw-contributions-title")) continue;
    const t = /title="([^"]+)"/.exec(tag);
    if (!t) continue;
    const title = t[1];
    if (title.startsWith("User:") || title.startsWith("File:")) continue;
    titles.add(title);
  }
  if (!titles.size) throw new Error("no titles");
  return { rosetta_tasks: titles.size, rosetta_new: (html.match(/newpage/g) || []).length };
}

async function rosettaApi() {
  const d = await fetchJson(ROSETTA_API, { timeout: 20000, ua: BROWSER_UA, cacheTtl: 600 });
  const items = (d.query && d.query.usercontribs) || [];
  if (!items.length) throw new Error("empty usercontribs");
  const titles = new Set(items.map((i) => i.title)
    .filter((t) => !t.startsWith("User:") && !t.startsWith("File:")));
  const fresh = items.filter((i) => (i.flags || []).includes("new")).length;
  return { rosetta_tasks: titles.size, rosetta_new: fresh };
}

// 博客园：侧边栏统计是独立的 AJAX 片段，里面带 title="总阅读数: N"。
const CNBLOGS_STATS = "https://www.cnblogs.com/yhm138/ajax/blog-stats";

async function cnblogs() {
  const html = await fetchText(CNBLOGS_STATS, { timeout: 15000, ua: BROWSER_UA, cacheTtl: 600 });
  const total = html.match(/总阅读数[:：]\s*(\d+)/);
  if (!total) throw new Error("cnblogs: no total-view field");
  const posts = html.match(/随笔\s*-\s*(\d+)/);
  return {
    cnblogs_reads: Number(total[1]),
    cnblogs_posts: posts ? Number(posts[1]) : null,
  };
}

// B 站：x/web-interface/card 一次给出粉丝、投稿数、总获赞，免签名。Bot UA 会被拒，
// 必须带浏览器 UA + space 页 referer。播放总数只在创作中心可见，公开渠道没有。
const BILI_MID = "503777379";
const BILI_REFERER = `https://space.bilibili.com/${BILI_MID}`;

async function bilibili() {
  const d = await fetchJson(
    `https://api.bilibili.com/x/web-interface/card?mid=${BILI_MID}`,
    { ua: BROWSER_UA, referer: BILI_REFERER, cacheTtl: 600 },
  );
  const c = d && d.data && d.data.card;
  if (!c) throw new Error(`bili card code ${d && d.code}`);
  return {
    bilibili_followers: Number(d.data.follower) || 0,
    bilibili_following: Number(d.data.following) || 0,
    bilibili_videos: Number(d.data.archive_count) || 0,
    bilibili_likes: Number(d.data.like_num) || 0,
  };
}

// card 挂了时的兜底：relation/stat 至少能给出粉丝数。
async function bilibiliFollowers() {
  const d = await fetchJson(
    `https://api.bilibili.com/x/relation/stat?vmid=${BILI_MID}`,
    { ua: BROWSER_UA, referer: BILI_REFERER, cacheTtl: 600 },
  );
  if (!d || !d.data || typeof d.data.follower !== "number") throw new Error("bili relation: no follower");
  return { bilibili_followers: d.data.follower };
}

// 抖音：分享页的旧版 v2 接口仍可用；follower_count 对未登录访客是 null。
const DOUYIN_SEC = "MS4wLjABAAAA1_4tBCUwtrW4IBcNkz5ouwndczRoFQfvehgQPH2CroA";
const DOUYIN_UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 " +
  "(KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1";

async function douyin() {
  const d = await fetchJson(
    `https://www.iesdouyin.com/web/api/v2/user/info/?sec_uid=${DOUYIN_SEC}`,
    { ua: DOUYIN_UA, referer: "https://www.douyin.com/", cacheTtl: 600 },
  );
  const ui = d && d.user_info;
  if (!ui) throw new Error("douyin: no user_info");
  return {
    douyin_likes: Number(ui.total_favorited) || 0,
    douyin_posts: Number(ui.aweme_count) || 0,
    douyin_following: Number(ui.following_count) || 0,
    douyin_followers: ui.follower_count ?? ui.mplatform_followers_count ?? null,
  };
}

// LeetCode 中国站的 GraphQL 允许匿名查询指定用户的做题进度（浏览器 UA + referer 必需）。
const LEETCODE_SLUG = "yhm138_";

async function leetcode() {
  const d = await postJson("https://leetcode.cn/graphql/", {
    query: `query p($userSlug: String!) {
      userProfileUserQuestionProgress(userSlug: $userSlug) {
        numAcceptedQuestions { difficulty count }
      }
      userProfilePublicProfile(userSlug: $userSlug) { siteRanking }
    }`,
    variables: { userSlug: LEETCODE_SLUG },
  }, { referer: `https://leetcode.cn/u/${LEETCODE_SLUG}/` });
  const prog = d && d.data && d.data.userProfileUserQuestionProgress;
  if (!prog) throw new Error("leetcode: no progress");
  const byDiff = {};
  for (const row of prog.numAcceptedQuestions) byDiff[row.difficulty] = row.count;
  const total = Object.values(byDiff).reduce((a, b) => a + b, 0);
  return {
    leetcode_solved: total,
    leetcode_easy: byDiff.EASY ?? null,
    leetcode_medium: byDiff.MEDIUM ?? null,
    leetcode_hard: byDiff.HARD ?? null,
    leetcode_rank: d.data.userProfilePublicProfile
      ? d.data.userProfilePublicProfile.siteRanking
      : null,
  };
}

// LeetCode 国际站：同样的 GraphQL，匿名可查。
async function leetcodeGlobal() {
  const d = await postJson("https://leetcode.com/graphql", {
    query: `query u($username: String!) {
      matchedUser(username: $username) {
        profile { ranking }
        submitStatsGlobal { acSubmissionNum { difficulty count } }
      }
    }`,
    variables: { username: "aspen1382020" },
  }, { referer: "https://leetcode.com/aspen1382020/" });
  const m = d && d.data && d.data.matchedUser;
  if (!m) throw new Error("leetcode.com: no matchedUser");
  const all = (m.submitStatsGlobal.acSubmissionNum || []).find((x) => x.difficulty === "All");
  return {
    leetcode_global_solved: all ? all.count : null,
    leetcode_global_rank: m.profile ? m.profile.ranking : null,
  };
}

// HackerRank 的旧 REST 接口仍然开放：徽章与各领域分数。
const HACKERRANK_USER = "aspen1382020";

async function hackerrank() {
  const d = await fetchJson(`https://www.hackerrank.com/rest/hackers/${HACKERRANK_USER}/badges`,
    { ua: BROWSER_UA, cacheTtl: 600 });
  const badges = (d && d.models) || [];
  if (!badges.length) throw new Error("hackerrank: no badges");
  const stars = badges.reduce((a, b) => a + (Number(b.stars) || 0), 0);
  const solved = badges.reduce((a, b) => a + (Number(b.solved) || 0), 0);
  return {
    hackerrank_badges: badges.length,
    hackerrank_stars: stars,
    hackerrank_solved: solved,
  };
}

// Codewars：完全公开的 JSON API。
async function codewars() {
  const d = await fetchJson("https://www.codewars.com/api/v1/users/aspen138", { cacheTtl: 600 });
  const cc = d.codeChallenges || {};
  const rank = (d.ranks || {}).overall || {};
  if (typeof cc.totalCompleted !== "number") throw new Error("codewars: no challenge count");
  return {
    codewars_katas: cc.totalCompleted,
    codewars_honor: d.honor ?? null,
    codewars_kyu: rank.name || null,
  };
}

// Chrome Web Store / 知乎被 Cloudflare 出口拦（403 / 无用户数的降落页），所以不放进这里：
// 它们由本机周任务写 chrome-users.json / web-stats.json。

const SOURCES = [
  ["greasyfork", greasyfork, null],
  ["pypi", pypi, null],
  ["stackexchange", stackexchangeHtml, stackexchangeApi],
  ["rosetta", rosettaHtml, rosettaApi],
  ["cnblogs", cnblogs, null],
  ["bilibili", bilibili, bilibiliFollowers],
  ["douyin", douyin, null],
  ["leetcode", leetcode, null],
  ["hackerrank", hackerrank, null],
  ["codewars", codewars, null],
  ["leetcodeGlobal", leetcodeGlobal, null],
];

export async function collect() {
  const out = { generated_at: new Date().toISOString(), sources: {} };
  const failed = [];
  for (const [name, primary, fallback] of SOURCES) {
    try {
      Object.assign(out, await primary());
      out.sources[name] = "primary";
      continue;
    } catch (_primaryError) { /* fall through to the fallback */ }
    if (fallback) {
      try {
        Object.assign(out, await fallback());
        out.sources[name] = "fallback";
        continue;
      } catch (_fallbackError) { /* fall through */ }
    }
    out.sources[name] = "unavailable";
    failed.push(name);
  }
  if (failed.length) out.stale = failed;
  return out;
}

/* ---------------------------------------------------------------- handler */

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (url.pathname !== "/" && url.pathname !== "/metrics") {
      return new Response("GET / or /metrics\n", { status: 404, headers: CORS });
    }

    const bypass = url.searchParams.has("nocache");
    const cache = caches.default;
    const key = new Request(new URL("/metrics", url.origin).toString());
    let res = bypass ? null : await cache.match(key);
    if (!res) {
      res = jsonResponse(await collect());
      if (!bypass) ctx.waitUntil(cache.put(key, res.clone()));
    }
    if (url.pathname === "/metrics") return res;

    const data = await res.clone().json();
    return htmlResponse(data);
  },
};
