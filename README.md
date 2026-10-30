# resume

线上简历：**https://yhm138.github.io/resume/**

一个静态页面 + 一个 Cloudflare Worker，没有构建步骤。页面只有一个 `index.html`，样式内联。

底部的数据条不是写死的，但也不是全部实时——每项指标的新鲜度取决于它能从哪儿取到。

## 指标来源

| 指标 | 载体 | 更新频率 |
| --- | --- | --- |
| GitHub 仓库数 | 浏览器直连 GitHub API | 每次访问 |
| GreasyFork 安装量 | 浏览器直连 GreasyFork API | 每次访问 |
| Stack Exchange 分站声誉 | 浏览器直连 SE API | 每次访问 |
| Stack Exchange 徽章（1 金 / 29 银 / 317 铜，117 站合计） | 浏览器直连 SE API（分页） | 每次访问 |
| GreasyFork 好评（39） | 浏览器直连 GreasyFork API | 每次访问 |
| Stack Exchange 全站声誉（24.7k / 118 站） | Cloudflare Worker | 10 分钟 |
| PyPI 累计下载（3,951） | Cloudflare Worker | 10 分钟 |
| RosettaCode（465 任务页 / 43 新建） | Cloudflare Worker | 10 分钟 |
| 博客园总阅读（164,729 / 139 篇） | Cloudflare Worker | 10 分钟 |
| LeetCode 通过题数（1,953，站点排名 1,612） | Cloudflare Worker | 10 分钟 |
| Codewars（38 kata / 5 kyu） | Cloudflare Worker | 10 分钟 |
| leetcode.com 通过题数（14） | Cloudflare Worker | 10 分钟 |
| 博客阅读量（221,229 = 博客园 + CSDN + 掘金） | Worker + 本机 `profiles.json` | 10 分钟 / 每周一 |
| 知乎赞同 / 收藏（937 / 1,833） | 本机计划任务 → `web-stats.json` | 每周一（开机则更新） |
| Chrome 扩展用户（671 / 6 个） | 本机计划任务 → `chrome-users.json` | 每周一（开机则更新） |
| HackerRank 认证（11 张 / 2 枚徽章） | 本机计划任务 → `profiles.json` | 每周一（开机则更新） |
| Codeforces（127 题 / 峰值 1,485） | 本机计划任务 → `profiles.json` | 每周一（开机则更新） |
| 牛客（490 已通过 / 613 已挑战，Rating 1,036） | 本机计划任务 → `profiles.json` | 每周一（开机则更新） |
| OEIS（3 个序列 / 8 次修订） | 本机计划任务 → `profiles.json` | 每周一（开机则更新） |
| Observable（1 个 notebook） | 本机计划任务 → `profiles.json` | 每周一（开机则更新） |
| Code360（1 题通过 / 250 分） | 本机计划任务 → `profiles.json` | 每周一（开机则更新） |
| 博客园文章数（139） | 本机计划任务 → `web-stats.json` | 每周一（开机则更新） |
| CSDN（53,019 访问 / 8 篇 / 16 粉） | 本机计划任务 → `profiles.json` | 每周一（开机则更新） |
| 掘金（3,251 阅读 / 8 篇） | 本机计划任务 → `profiles.json` | 每周一（开机则更新） |
| Gitee（1 仓库 / 9 commits） | 本机计划任务 → `profiles.json` | 每周一（开机则更新） |
| Bluesky（0 帖 / 6 粉）、Mastodon（2 帖 / 0 粉） | 本机计划任务 → `profiles.json` | 每周一（开机则更新） |
| Advent of Code 2024 全球名次（#14 / 1,699 分） | 静态（历史赛果） | 不更新 |

页面上用两种圆点区分：实心 = 每次访问实时取；空心 = 定时缓存或本地刷新。数据条共 10 格，桌面 5 列、移动 2 列。

> 表格里括号中的数字是写这行时的快照（例如博客园与 PyPI 的那两个数一直在涨）；线上按各自通道刷新，以页面显示为准。

> 知乎的三个数字容易混：`voteup_count` 是赞同（937），`favorited_count` 是收藏（1,833），`thanked_count` 是感谢（620）。简历正文里说的“620 次喜欢”指的是感谢数。

> 抖音的 `follower_count` 对未登录访客返回 `null`，所以当年那格放的是**获赞数**（`total_favorited`）。这格已被换掉：B 站 35 粉、抖音 71 赞是数据条里最弱的两项，现在的位置给了博客阅读量与 AoC 名次。

## 三层降级

```
① Cloudflare Worker  /metrics
      ↓ 不可达
② metrics.json        仓库里的快照
      ↓ 读不到
③ index.html 里的静态值
```

任何一层挂掉，页面显示的是旧数字，不会空白，也不会跳变。这是刻意设计的：外部依赖失败时，最坏结果是“不新鲜”，不是“打不开”。

`web-stats.json`、`chrome-users.json` 和 `profiles.json` 走的是第四种模式——它们是本机发布的文件，页面直接读，不经 Worker。

## 文件

| 文件 | 作用 |
| --- | --- |
| `index.html` | 页面全部内容与样式 |
| `metrics.json` | 指标快照，Worker 不可达时的兜底 |
| `metrics.py` | 本地抓取脚本，用来重新生成 `metrics.json` |
| `chrome-ids.json` | 6 个扩展到 Chrome Web Store ID，Worker 读取它 |
| `chrome-users.json` | 扩展用户数合计与逐项明细，由本机计划任务发布 |
| `web-stats.json` | 知乎赞同/收藏与博客园总阅读，由本机计划任务发布 |
| `profiles.json` | OEIS / Observable / Code360 / HackerRank / Codeforces / 牛客 / CSDN / 掘金 / Gitee / Bluesky / Mastodon 计数器，由本机计划任务发布 |
| `update-profiles.py` | 采集上面三个平台并自行 commit + push 的脚本 |

## Cloudflare Worker

- 地址：`https://autumn-thunder-2ee6.aspen1382020.workers.dev`
- `GET /metrics` → JSON，带 `Access-Control-Allow-Origin: *`
- `GET /` → 状态页，逐项显示数值与来源通道（`primary` / `fallback` / `unavailable`）
- 缓存 10 分钟；代码不在本仓库，在 Cloudflare 控制台维护

Worker 负责“浏览器取不到”的那几项：这些站点要么不发 CORS 头，要么需要服务端请求。目前它跑 11 个源：GreasyFork、PyPI、Stack Exchange、RosettaCode、博客园、Bilibili、抖音、LeetCode（国内站）、LeetCode（国际站）、HackerRank、Codewars。

## 哪些没法自动，为什么

**知乎的公开接口拒绝机房 IP。** `https://www.zhihu.com/api/v4/members/...` 在住宅网络下直接返回精确数字，从 Cloudflare 出口取则被挡。所以知乎两个数改由本机每周跑脚本发布成 `web-stats.json`。

**抖音的网页端是 JS 反爬，但旧版分享接口还活着。** `douyin.com/user/...`、`iesdouyin.com/share/user/...`、`m.douyin.com/...` 三个地址返回的都是同一份 72 KB 的 `_$jsvmprt` 混淆脚本，正文为空；而 `https://www.iesdouyin.com/web/api/v2/user/info/?sec_uid=...` 仍返回 JSON。

**LeetCode 的做题数只能走 GraphQL。** 个人主页是 Next.js 渲染的，但 `https://leetcode.cn/graphql/` 允许匿名 POST 查询 `userProfileUserQuestionProgress`，一次拿到三档难度的通过题数与站点排名。

**Codewars 有完全公开的 JSON API。** `https://www.codewars.com/api/v1/users/aspen138` 直接返回 honor、kata 完成数与段位。

**HackerRank 的旧 REST 接口数的是领域，不是徽章。** `https://www.hackerrank.com/rest/hackers/aspen1382020/badges` 返回 5 条（Problem Solving / Java / Python / SQL / Ruby，即账号有活动的领域），不是个人页「Badges」栏里的徽章（2 枚）。页面上那一格现在显示**认证数**：11 张（SQL Basic/Intermediate/Advanced、Python、Java、Go、JavaScript、Rest API、Problem Solving，另有一张 Software Engineer Intern 的 role 认证）。徽章与认证都可以直接从个人页 HTML 数 `class="hacker-badge"` 与 `certificate-link`——该页是服务器直出，不需要浏览器。Worker 里那一项仍在跑，但页面已不采用。

**leetcode.com 与 leetcode.cn 是两个独立的账号体系。** 国际站走 `leetcode.com/graphql` 的 `submitStatsGlobal`，国内站走 `leetcode.cn/graphql` 的 `userProfileUserQuestionProgress`，数字不通用（国内 1,953，国际 14）。

**LintCode 没有公开的用户统计接口。** 个人页是 SPA，`https://apiv1.lintcode.com/new/api/accounts/profile/` 只返回当前会话的账号；带用户 ID 的变体全部 404。

**51CTO 被 WAF 挡住。** `https://blog.51cto.com/u_15247503` 无论直连还是真实浏览器都返回腾讯云 EdgeOne 的拦截页（“请求已被站点安全策略拦截”），拿不到任何数据。

**LinkedIn 完全取不到。** 任何非登录请求都返回 HTTP 999（LinkedIn 的反爬状态码），且抓取违反其条款。页面上只保留链接。

**牛客的数据在竞赛主页的 HTML 里，不在 sparta API 里。** `https://gw-c.nowcoder.com/api/sparta/user/profile/<id>` 只有昵称、学历、身份标签；竞赛主页 `https://ac.nowcoder.com/acm/contest/profile/<id>` 是服务器直出，能看到 Rating（1036）、Rating 排名（9999+）、Rating 赛场次（10）与总场次（28），`.../practice-coding` 页还有「613 题已挑战 / 490 题已通过 / 1452 次提交」。这两个页面不需要登录，也不发 CORS 头；页面上的 490 / 613 由本机每周一任务发布。

**Codeforces 的公开 API 带 `Access-Control-Allow-Origin: *`。** `user.info`、`user.rating`、`user.status` 浏览器可直连；个人页数据：rating 1396、峰值 1485（specialist）、2 场 rated。页面上只展示「127 题 + 峰值 1,485」，走本机每周一任务发布——`/user.status` 一次约 150 KB，不值得每次访问都拉。

**Bilibili 的播放量需要 wbi 签名。** `x/relation/stat`（粉丝/关注）和 `x/web-interface/card`（粉丝/投稿/获赞）都免签名，但播放总数只在创作中心可见，`x/space/wbi/arc/search` 返回 412。

**Chrome Web Store 拒绝机房 IP。** Cloudflare Worker 和 GitHub Actions 的出口 IP 都被 Google 挡（403 或返回没有用户数的落地页），`r.jina.ai` 代理能取到页面但拿不到统计。只有住宅网络能直连，所以改成本机每周跑一次脚本，把结果提交成 `chrome-users.json`。

**博客园没有“总阅读数”的正文字段，只有一个 AJAX 片段。** `https://www.cnblogs.com/yhm138/ajax/blog-stats` 返回 242 字节的 HTML 片段，里面有 `title="总阅读数: 164729"`。注意这个数和“逐篇文章阅读数之和”不是一个口径（后者约 11 万），因为它包含首页与分类页的浏览。

**GitHub Actions 的 `schedule` 在这个账号上不触发。** 用一个独立的、只有 5 分钟 cron 的空仓库验证过：连续多次触发点均为 0 次运行，且 `workflow_dispatch` 正常，平台状态当时无故障。因此本仓库不含任何定时 workflow。

**OEIS、Observable、Code360 三家都不发 CORS 头。** 页面无法直连读取，只能由本机脚本取。OEIS 翻 `/history?user=` 的分页数修订行；Observable 读 `https://api.observablehq.com/user/@aspen1382020/documents`（要求带 `Referer`）；Code360 读 `/code360/api/v3/public_section/profile/user_details?uuid=...&request_differentiator=...&app_context=publicsection&naukri_request=true`，少了后几个参数会被 Akamai 拦。

**Code360 还拒绝机房 IP。** 用 `r.jina.ai` 和 `api.allorigins.win` 各试一次，返回的都是 403 Access Denied，所以 Cloudflare Worker 也取不到它，这条只能靠住宅网络。同一份 API 带上 `Referer` / `Origin` 从本机直连返回 200。

**Observable 会对空 UA 或连续请求返回 429。** 抓取时带浏览器 UA，且每周只取一次；调试时不要连续打同一个 profile 页。

**Lark wiki（AIME / Putnam 解法）对外可读，但目录接口要登录。** 直接请求 `https://adzu3lvjw4g.sg.larksuite.com/space/api/wiki/v2/tree/get_info/?...wiki_token=...` 返回 `{"code":5,"msg":"Login Required"}`，只有带网页会话的浏览器才拿得到完整目录树。所以页面上只放链接和静态计数（33 个 AIME 年份 / 68 篇 Putnam，共 101 页）：这批数字一年才动一次，没必要上自动化。

## 响应式

三档断点，逐档验证过无横向溢出（量 `documentElement.scrollWidth` 并扫描元素右边界）：

| 宽度 | 布局 |
| --- | --- |
| > 780px | 左侧章节序号栏 + 右侧正文，数据条 5 列 |
| 421–780px | 章节序号栏收起，数据条 2 列 |
| ≤ 420px | 小屏字号档（姓名 34px、摘要 14.8px、正文 13.6px），数据条 2 列 |

另外：`text-wrap: balance` 用在姓名与章节标题上；`env(safe-area-inset-bottom)` 避免 iPhone 底部横杠压住页脚；`-webkit-tap-highlight-color: transparent` 关掉移动端点击灰块。

## 怎么维护

**新增或下线扩展**：改 `chrome-ids.json` 里的 `ids` 数组即可，Worker 下次请求就会用新列表。下线的扩展详情页返回 404，会被自动跳过。

**刷新快照**：

```bash
python metrics.py && git add metrics.json && git commit -m "chore: refresh metrics" && git push
```

**刷新 Chrome 用户数**：运行 `update-chrome-users.py`（需要本机已登录 `gh`）。它会抓六个商店页、算出合计，通过 GitHub API 直接提交 `chrome-users.json`，不需要本地 clone。

**刷新知乎与博客园**：运行 `update-web-stats.py`。两者都是单次 HTTP 请求，几秒完成，同样通过 `gh` 直接提交。

计划任务已注册为每周一 09:30，一次跑两个脚本：

```
TaskName : \resume chrome users
命令     : C:\Users\Yangh\resume-metrics\run.cmd
脚本     : update-chrome-users.py, update-web-stats.py
日志     : C:\Users\Yangh\resume-metrics\run.log
```

**刷新平台计数器（OEIS / Observable / Code360 / HackerRank / Codeforces / 牛客 / CSDN / 掘金 / Gitee / Bluesky / Mastodon）**：在仓库根目录运行 `python update-profiles.py`。数字没变就不写文件，也不提交；有变化才 `git commit` + `push`。计划任务每周一 09:40 跑一次（错开 09:30 的 Chrome/知乎任务）：

```
TaskName : \resume profile stats
命令     : cmd /c cd /d D:\yhm138Project\resume-site && python update-profiles.py
日志     : %LOCALAPPDATA%\resume-profile-task.log
```

## 依赖

`metrics.py` 中 Chrome 那一段需要 `playwright` + Chromium；其余数据源只用标准库。`update-profiles.py` 也只用标准库，但它要能 `git push`（依赖本机已登录的 git 凭据）。`update-chrome-users.py` 与 `update-web-stats.py` 只依赖标准库和 `gh` CLI。
