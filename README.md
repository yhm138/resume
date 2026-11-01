# resume

线上简历：**https://yhm138.github.io/resume/**

单文件页面（`index.html`，样式内联，无构建）+ 一个 Cloudflare Worker + 两个本机计划任务。每个数字的取数通道不同，取不到就退回旧值，不会空白。

## 指标来源

> 下表按**更新频率**排序：每次访问 → 10 分钟 → 每周一 → 不更新。括号里的数字是写表时的快照，线上以页面显示为准。

| 指标 | 载体 | 更新频率 |
| --- | --- | --- |
| GitHub 仓库数（50） | 浏览器直连 GitHub API | 每次访问 |
| GreasyFork 安装量（11.5k / 81 脚本） | 浏览器直连 GreasyFork API | 每次访问 |
| GreasyFork 好评（39） | 浏览器直连 GreasyFork API | 每次访问 |
| Stack Exchange 分站声誉 | 浏览器直连 SE API | 每次访问 |
| Stack Exchange 徽章（347，117 站合计） | 浏览器直连 SE API（分页） | 每次访问 |
| 访客城市 / 国家 | 浏览器直连 ipinfo.io（降级 api.country.is） | 每次访问 |
| 整站 PV / UV | vercount.one 脚本（busuanzi 兼容） | 每次访问 |
| Codeberg 仓库数（5） | 浏览器直连 Codeberg API（Gitea/Forgejo） | 每次访问 |
| 天池（3 场比赛） | 浏览器直连 Tianchi API（带 CORS） | 每次访问 |
| Stack Exchange 全站声誉（24.7k / 118 站） | Cloudflare Worker | 10 分钟 |
| PyPI 累计下载（3,959） | Cloudflare Worker | 10 分钟 |
| RosettaCode（465 任务页 / 43 新建） | Cloudflare Worker | 10 分钟 |
| 博客园总阅读（165,007 / 139 篇） | Cloudflare Worker | 10 分钟 |
| LeetCode 通过题数（1,953） | Cloudflare Worker | 10 分钟 |
| Codewars（38 kata / 5 kyu） | Cloudflare Worker | 10 分钟 |
| leetcode.com 通过题数（14） | Cloudflare Worker | 10 分钟 |
| 博客阅读量（221k = 博客园 + CSDN + 掘金） | Worker + 本机 `profiles.json` | 10 分钟 / 每周一 |
| 知乎回答 / 赞同 / 收藏 / 感谢（165 / 937 / 1,833 / 620） | 本机计划任务 → `web-stats.json` | 每周一（开机则更新） |
| 博客园文章数（139） | 本机计划任务 → `web-stats.json` | 每周一（开机则更新） |
| Chrome 扩展用户（671 / 6 个） | 本机计划任务 → `chrome-users.json` | 每周一（开机则更新） |
| HackerRank 认证（11 张 / 2 枚徽章） | 本机计划任务 → `profiles.json` | 每周一（开机则更新） |
| Codeforces（127 题 / 峰值 1,485） | 本机计划任务 → `profiles.json` | 每周一（开机则更新） |
| 牛客（490 已通过 / 613 已挑战） | 本机计划任务 → `profiles.json` | 每周一（开机则更新） |
| OEIS（3 序列 / 8 修订） | 本机计划任务 → `profiles.json` | 每周一（开机则更新） |
| Observable（1 notebook） | 本机计划任务 → `profiles.json` | 每周一（开机则更新） |
| Code360（1 题通过 / 250 分） | 本机计划任务 → `profiles.json` | 每周一（开机则更新） |
| CSDN（53,019 访问 / 8 篇 / 16 粉） | 本机计划任务 → `profiles.json` | 每周一（开机则更新） |
| 掘金（3,251 阅读 / 8 篇） | 本机计划任务 → `profiles.json` | 每周一（开机则更新） |
| Gitee（1 仓库 / 9 commits） | 本机计划任务 → `profiles.json` | 每周一（开机则更新） |
| Bluesky（0 帖 / 6 粉）、Mastodon（2 帖 / 0 粉） | 本机计划任务 → `profiles.json` | 每周一（开机则更新） |
| 访客分布地图（按国家；页面每次访问给本国 +1） | 本机计划任务 → `visitor-map.json` | 每周一（开机则更新） |
| ScriptCat（6 脚本 / 2,683 安装） | 本机计划任务 → `profiles.json`（后端 JSON API 无 CORS） | 每周一（开机则更新） |
| Advent of Code 2024 全球名次（#14 / 1,699 分） | 静态（历史赛果） | 不更新 |
| AIME / Putnam 解法 wiki（101 页） | 静态（一年加一两页） | 不更新 |

三条口径提醒：

- 知乎四个数别混：`answer_count` 回答（165）、`voteup_count` 赞同（937）、`favorited_count` 收藏（1,833）、`thanked_count` 感谢（620）。
- 博客园「总阅读数」含首页与分类页浏览，不等于逐篇阅读之和（后者约 11 万）；「博客阅读量」是博客园 + CSDN + 掘金三家相加，任一源缺值就不出总数。
- 数据条共 10 格（桌面 5 列 × 2 行，≤780px 2 列），顺序：repos / GF installs / SE reputation / RosettaCode / PyPI / Chrome / blog reads / AoC / LeetCode / SE badges。实心圆点 = 每次访问实时取，空心 = 定时或本机刷新。

**页面最底部**（页脚里）是访客信息：`you · 城市, 国家`（ipinfo.io 按访客 IP 判断）、`views` / `visitors`（vercount 的整站 PV / UV，按域名计，不是本页单独计数），下面一张点阵世界地图：陆地用分隔线色画点，访客国家用 teal 圆点（半径随访问量开方增长），数据来自 `visitor-map.json` 的周快照。这两块都带 `js-only`，打印时不出现。

## 通道细节

- **浏览器直连**：GitHub、GreasyFork、Stack Exchange、天池、Codeberg（Gitea/Forgejo API）都带 CORS，页面每次访问直接取；SE 徽章走 `users/21083779/associated`，117 个分站 > 100 条/页，必须翻页，否则少算（曾少算成 306）。
- **Cloudflare Worker（v3，源码见 `worker.js`）**：`https://autumn-thunder-2ee6.aspen1382020.workers.dev/metrics`，缓存 10 分钟，`Access-Control-Allow-Origin: *`；`GET /` 是状态页（`primary` / `fallback` / `unavailable`，并列出本次缺了哪些字段）；`GET /?nocache=1` 绕过缓存。
  - v3 修的东西：GreasyFork 改用规范地址（旧地址 301 且跳转后丢 CORS）；Bilibili / 抖音 / LeetCode 加浏览器 UA + referer（旧的 `resume-metrics` UA 被拒，这正是那几个字段从返回里消失的原因）；Bilibili 增加 `x/relation/stat` 兜底；Stack Exchange 改为「账号页抓取为主、API `/associated` 兜底」；知乎从 Worker 移除（所有机房 IP 都 403，只能本机跑）。
  - 口径差异：账号页抓到 118 站 / 24,671；SE API `associated` 是 117 站 / 24,570。两个都算对，只是站点集合不同，页面按抓到的那个数显示。
  - RosettaCode 会间歇性被 Cloudflare challenge，两条通道都可能失败，此时页面回落到静态的 465 / 43。
- **本机任务 A**（`\resume chrome users`，每周一 09:30，`C:\Users\Yangh\resume-metrics\run.cmd`）：`update-chrome-users.py` + `update-web-stats.py`，通过 `gh` 直接提交；跑的是拒绝机房 IP 的源（Chrome Web Store、知乎）。
- **本机任务 B**（`\resume profile stats`，每周一 09:40）：仓库根目录 `python update-profiles.py`，数字没变就不写文件也不提交；跑的是无 CORS 的源（OEIS、Observable、Code360、CSDN、掘金、Gitee、牛客、Codeforces、HackerRank、Bluesky、Mastodon、ScriptCat）。
- **访客信息**：城市/国家靠 ipinfo.io（失败退回 api.country.is，只到国家），PV/UV 靠 vercount.one 的脚本（写一个 1 年期 cookie 用来判首次 UV，本地 localStorage 缓存上次值）。这两项都会把访客 IP 发给第三方；页面本身不写 cookie。两者都失败时显示 `—`，不影响其它数字。
- **访客分布地图**：页面每访问一次，按 ipinfo 给的国家调一次 `abacus.jasoncameron.dev/hit/yhm138resume/c-<iso2>`（只对 64 个被追踪的国家/地区，其余忽略）；周任务再把每个国家的计数器读出来写进 `visitor-map.json`。地图本身是页内 SVG：96×48 陆地掩码（base64，768 字节）+ 64 个国家经纬度，全部内联，不加载任何地图库或瓦片。

## 降级链

```
① Cloudflare Worker  /metrics
      ↓ 不可达
② metrics.json        仓库里的快照
      ↓ 读不到
③ index.html 里的静态值
```

`web-stats.json`、`chrome-users.json`、`profiles.json` 是第四种模式：本机发布，页面直接读 raw，不经 Worker。最坏结果是「不新鲜」，不是「打不开」。

## 外链确认弹窗

所有 `http(s)` 链接点击后先弹 `<dialog class="leave">`（纸色、衬线标题、等宽按钮，同一套 CSS 变量），确认后才 `window.open(url, '_blank', 'noopener,noreferrer')`。Esc / 点背景 / `Stay here` 关闭，焦点回原链接；`prefers-reduced-motion` 下无动画；无 JS 时照常跳转。

## 文件

| 文件 | 作用 |
| --- | --- |
| `index.html` | 页面全部内容与样式 |
| `metrics.json` | Worker 不可达时的快照兜底 |
| `metrics.py` | 重新生成 `metrics.json`（Chrome 段需要 Playwright） |
| `chrome-ids.json` | 6 个扩展的商店 ID，Worker 读它 |
| `chrome-users.json` | 扩展用户合计与逐项明细 |
| `web-stats.json` | 知乎四个计数 + 博客园阅读 / 文章数 |
| `profiles.json` | 12 个平台的计数器（见上表「每周一」部分） |
| `visitor-map.json` | 各国家访客数（abacus 计数器聚合，周快照） |
| `update-profiles.py` | 采集 `profiles.json` 并自行 commit + push |
| `worker.js` | Cloudflare Worker 源码（改完手动粘到控制台部署；仓库这份是源，不是部署产物） |

## 维护

- **刷新快照**：`python metrics.py && git add metrics.json && git commit -m "chore: refresh metrics" && git push`
- **改 Worker**：编辑仓库里的 `worker.js` → 复制粘贴到 Cloudflare 控制台 → 部署；然后开 `https://autumn-thunder-2ee6.aspen1382020.workers.dev/` 看每个源是 `primary` / `fallback` / `unavailable`，再开 `?nocache=1` 确认新值。
- **刷新 Chrome / 知乎 / 博客园**：见本机任务 A；**刷新平台计数器**：见本机任务 B（同时重算 `visitor-map.json`：64 个国家各一次 GET，约 30 秒）。
- **新增或下线 Chrome 扩展**：改 `chrome-ids.json` 的 `ids` 数组，Worker 下次请求生效；下线扩展的详情页 404 会被跳过。
- **部署**：改 `index.html` → commit + push 到 `main`，Pages 自动构建。验证必须带 cache buster（`?v=<时间戳>`），否则约 10 分钟边缘缓存会让你看到旧页面；实测 75 秒时可能仍是旧版，轮询到出现预期内容为止。

## 已知死路

| 平台 | 现象 | 结论 |
| --- | --- | --- |
| LinkedIn | 非登录请求返回 HTTP 999，抓取违反条款 | 只放链接 |
| 知乎 | 接口拒绝机房 IP | 本机跑 → `web-stats.json` |
| Chrome Web Store | 拒绝机房 IP（Worker / Actions 皆 403） | 本机跑 → `chrome-users.json` |
| Code360 | Akamai 拒绝机房 IP，r.jina.ai / allorigins 均 403 | 本机跑 |
| OEIS / Observable / Code360 | 都不发 CORS 头 | 本机跑；Observable 对空 UA 或连打返回 429 |
| 牛客 | sparta API 只有昵称，数据在竞赛主页 HTML | 解析 HTML，本机跑 |
| LintCode | 无公开统计接口，SPA | 放弃 |
| 51CTO | 腾讯云 EdgeOne WAF 拦截页 | 放弃 |
| Bilibili 播放量 | 需 wbi 签名，播放总数只在创作中心 | 放弃 |
| 微信公众号 / 视频号 / 即刻 | 无公开接口 | 做不到 |
| 微博 / 小红书 / X / Instagram / Threads | 反爬或需登录态 | 不建议 |
| GitHub Actions 定时 | 该账号 `schedule` 不触发（空仓库验证过，`workflow_dispatch` 正常） | 不放定时 workflow |
| Lark wiki | 目录树 API 返回 `Login Required`，只有带会话的浏览器能读 | 只放链接 + 静态计数 |

## 撤掉的展示

- **Bilibili 35 粉 / 抖音 71 赞**：数据条最弱的两格，换成博客阅读量与 AoC 名次。
- **HackerRank 认证格**：11 张认证 + 2 枚徽章，数字太小，从数据条撤下，改在 Problem solving 正文写「11 verified HackerRank certifications (2 skill badges)」。
- **网易云音乐 / 豆瓣**：和找工作无关且数字太弱，链接都不放；简书、Bluesky、Mastodon 按「以后会发布」保留链接但不展示数字。

## 调研结论：还能接什么

**没有新的值得接的社媒源。** 下表是逐平台实测记录，不要重复调研；拿到新账号链接时才需要重开。

| 平台 | 账号 | 实测 | 结论 |
| --- | --- | --- | --- |
| GitLab | `yhm138`（id 9277119） | 0 公开项目、无 follower、API 无 CORS | 没内容 |
| V2EX | `yhm138` | 404 | 无账号 |
| ModelScope | `author=yhm138` | 404 | 无模型 |
| Hugging Face | `yhm138` | 无模型 / 数据集 | 没内容 |
| npm | `yhm138` / `~aspen138` | 0 个包 | 先放链接（等发布） |
| crates.io | `yhm138`（id 201685） | 0 crate、0 下载 | 先放链接（等发布） |
| Docker Hub | `aspen138` | 0 仓库 | 先放链接（等发布） |
| SourceForge | `aspen138` | Cloudflare 验证页 | 先放链接 |
| Kaggle | `aspen138` | reCAPTCHA | 先放链接 |
| JetBrains Marketplace | `/author/me` | 匿名访客只见登录页，公开 URL 要等插件上线 | 先放链接 |
| Google Play | 开发者 ID 7351019373232905041 | 公开页 `store/apps/dev?id=...` 因无已上架应用暂 404；后台地址只跳登录 | 已放公开页（暂 404） |
| AtCoder | `yhm138` | 账号存在，无 rating / 比赛记录 | 不值得放 |
| 网易云音乐 | `id=1544379686` | API 可取 2,873 首 / level 7 / 7 歌单 / 0 粉 | 页面未放 |
| 豆瓣 | `220820619` | 匿名看不到关注数，广播需登录 | 页面未放 |
| 简书 | `796435070e0c` | 2 篇 / 1 粉 / 38 字 | 只放链接 |
| 天池 | `userId=1095279495628` | `home/science/races` 返回 3 场比赛；`getByUserId` 显示 Junior Developer 勋章；带 CORS | 显示「3 competitions」 |
| Wolfram Community | `aspen1382020` | Discourse API：0 主题 / 0 回复 / 2 徽章 | 只放链接 |
| MaplePrimes | `Aspen138` | 0 声誉 / 0 徽章 | 只放链接 |
| Reddit | `Aspen138` | 匿名访问返回「This account has been banned」，取不到 karma / 帖子数 | 已放链接（用户要求），恢复后补数字 |
| Wolfram Function Repository | `PublisherID=OnehundredthirtyeightAspen` | 浏览器渲染后可见 **1 个已发布函数**：`MostFrequentKStringDistance`（v1.0.0，2026-01-16）；页面是 SPA，纯 HTTP 只有空壳，资源 API 未带凭据返回 401 | 已放链接 + 计数（静态） |
| Quora | `138-Aspen` | 纯 HTTP 403；浏览器能打开：0 回答 / 0 问题 / 0 帖 / 0 粉，2021-01 加入 | 只放链接（等发布） |
| YouTube | `@yhm138`、`@aspen1382020` 均 404 | — | 有频道再给链接 |

已有平台还有些「小数字」没展示（CSDN 粉丝 16 / 获赞 17 / 收藏 167 / 排名 42,007，掘金关注 2 / 掘力值 97，Gitee followers 0）。它们都在 `profiles.json` 里——量级低于 100 的指标只会稀释已有的强数字，别为了凑数放上去。

## 依赖

`metrics.py` 的 Chrome 段需要 `playwright` + Chromium；`update-profiles.py` 只用标准库，但要能 `git push`（依赖本机 git 凭据）；`update-chrome-users.py` / `update-web-stats.py` 只用标准库 + `gh` CLI。

## 样式与响应式

纸色 `#f7f5f1`、墨色 `#16181a`、强调色 `#123f4d`、分隔线 `#d9d4c9`；标题衬线（Charter / Palatino），正文无衬线，数字等宽。正文关键数字用 `.stat`（衬线 + 1.34em + 琥珀高亮），次要数字用 `.hl`。

三档断点，逐档量过 `documentElement.scrollWidth` 与元素右边界，320 / 360 / 375 / 390 / 414 / 430 / 768 / 1280 无横向溢出：

| 宽度 | 布局 |
| --- | --- |
| > 780px | 左侧章节序号栏 + 右侧正文，数据条 5 列 |
| 421–780px | 序号栏收起，数据条 2 列 |
| ≤ 420px | 小屏字号档，数据条 2 列 |

另有 `text-wrap: balance`、`env(safe-area-inset-bottom)`、`-webkit-tap-highlight-color: transparent`。
