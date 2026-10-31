# resume

线上简历：**https://yhm138.github.io/resume/**

单文件页面（`index.html`，样式内联，无构建）+ 一个 Cloudflare Worker + 两个本机计划任务。页面上的数字按取数通道分级，取不到就退回旧值，不会空白。

## 页面结构

- **masthead**：姓名、摘要、联系方式（邮箱用 `aspen1382020 at gmail dot com` 反爬写法；LinkedIn 只有链接）
- **数据条**：10 格，桌面 5 列 × 2 行，≤780px 2 列；实心圆点 = 每次访问实时取，空心 = 定时缓存 / 本机发布
- **章节 01–05**：Experience / Education / Awards / Skills / Open Source & Writing
- **所有外链**：点击先弹确认窗（见下文）

### 数据条 10 格

| 格子 | 值（快照） | 通道 |
| --- | --- | --- |
| Public repos | 50 | 浏览器直连 GitHub API |
| GF installs | 11.5k | 浏览器直连 GreasyFork API |
| SE reputation | 24.7k | Worker（全站合计） |
| RosettaCode | 465 | Worker |
| PyPI downloads | 3,951 | Worker |
| Chrome users | 671 | 本机 → `chrome-users.json` |
| Blog reads · 3 sites | 221k | Worker（博客园）+ 本机 `profiles.json`（CSDN / 掘金） |
| AoC 2024 · global | #14 | 静态（历史赛果） |
| LeetCode solved | 1,953 | Worker（国内站） |
| SE badges | 347 | 浏览器直连 SE API（分页合计） |

## 数据通道

### 1. 浏览器直连（接口带 CORS）

| 指标 | 接口 |
| --- | --- |
| GitHub 仓库数 | `api.github.com/users/yhm138` |
| GreasyFork 安装 / 脚本数 / 好评 | `api.greasyfork.org/en/users/1177387-138-aspen.json` |
| SE 分站声誉 | `api.stackexchange.com/2.3/users/<id>?site=...` |
| SE 徽章合计 | `api.stackexchange.com/2.3/users/21083779/associated?pagesize=100&page=N`（117 站 > 100 条/页，必须翻页，否则少算成 306） |

### 2. Cloudflare Worker（10 分钟缓存）

`https://autumn-thunder-2ee6.aspen1382020.workers.dev/metrics`，`Access-Control-Allow-Origin: *`。`GET /` 是状态页，逐项显示 `primary` / `fallback` / `unavailable`。代码不在本仓库，改它要在控制台粘贴部署。

覆盖：Stack Exchange 全站、PyPI、RosettaCode、博客园阅读、Bilibili、抖音、LeetCode 国内 / 国际、HackerRank、Codewars。

> Worker 里的 Bilibili、抖音、HackerRank 三项**页面已不用**：前两项数字太小（35 粉 / 71 赞）已从数据条撤掉，HackerRank 改由正文展示认证数（见「撤掉的展示」）。

### 3. 本机计划任务 → `profiles.json`（每周一 09:40）

`update-profiles.py` 采集，数字没变就不写文件、不提交。当前：HackerRank 认证、Codeforces（127 题 / 峰值 1,485）、牛客（490 / 613）、OEIS（3 序列 / 8 修订）、Observable（1 notebook）、Code360（1 题）、CSDN（53,019 访问 / 8 篇）、掘金（3,251 阅读 / 8 篇）、Gitee（1 仓库 / 9 commits）、Bluesky、Mastodon。

### 4. 本机计划任务 → `web-stats.json` / `chrome-users.json`（每周一 09:30）

知乎（165 回答 / 937 赞同 / 1,833 收藏 / 620 感谢）、博客园阅读数与文章数（139）、Chrome 扩展用户（671 / 6 个）。

### 5. 静态数字

Advent of Code 2024（#14 / 1,699 分）、AIME + Putnam 解法 wiki（101 页 = 33 个 AIME 年份 + 68 篇 Putnam）、ScriptCat（6 脚本 / 2,676 安装）、天池（3 场比赛）。这几项一年也动不了一次，不值得接自动化。

### 6. 只放链接（不展示数字）

Bluesky、Mastodon、Jianshu、crates.io、npm、Docker Hub、SourceForge、Kaggle、JetBrains Marketplace、Google Play、天池（天池另有 3 场比赛的计数）。

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

所有 `http(s)` 链接点击后先弹 `<dialog class="leave">`（纸色、衬线标题、等宽按钮，同一套 CSS 变量），确认后才 `window.open(url, '_blank', 'noopener,noreferrer')`。Esc / 点背景 / `Stay here` 关闭，焦点回到原链接；`prefers-reduced-motion` 下无动画；无 JS 时链接照常跳转。

## 文件

| 文件 | 作用 |
| --- | --- |
| `index.html` | 页面全部内容与样式 |
| `metrics.json` | Worker 不可达时的快照兜底 |
| `metrics.py` | 重新生成 `metrics.json`（Chrome 段需要 Playwright） |
| `chrome-ids.json` | 6 个扩展的商店 ID，Worker 读它 |
| `chrome-users.json` | 扩展用户合计与逐项明细 |
| `web-stats.json` | 知乎四个计数 + 博客园阅读 / 文章数 |
| `profiles.json` | 11 个平台的计数器（见「数据通道 3」） |
| `update-profiles.py` | 采集 `profiles.json` 并自行 commit + push |

## 维护

**刷新快照**：`python metrics.py && git add metrics.json && git commit -m "chore: refresh metrics" && git push`

**刷新 Chrome 用户数 / 知乎与博客园**：`update-chrome-users.py`、`update-web-stats.py`（在 `C:\Users\Yangh\resume-metrics\`，需要 `gh` 已登录；通过 GitHub API 直接提交，不需要 clone）。计划任务 `\resume chrome users`，每周一 09:30。

**刷新平台计数器**：仓库根目录 `python update-profiles.py`。计划任务 `\resume profile stats`，每周一 09:40，日志 `%LOCALAPPDATA%\resume-profile-task.log`。

**部署**：改 `index.html` → commit + push 到 `main`，GitHub Pages 自动构建。验证必须带 cache buster（`?v=<时间戳>`），否则 ~10 分钟边缘缓存会让你看到旧页面并误判；实测 75 秒时可能仍是旧版，轮询到出现预期内容为止。

**新增/下线 Chrome 扩展**：改 `chrome-ids.json` 的 `ids` 数组即可，Worker 下次请求生效。

## 已知死路

| 平台 | 现象 | 结论 |
| --- | --- | --- |
| LinkedIn | 非登录请求返回 HTTP 999，抓取违反条款 | 只放链接 |
| 知乎 | 接口拒绝机房 IP | 只能本机跑 → `web-stats.json` |
| Chrome Web Store | 拒绝机房 IP（Worker / Actions 都 403） | 只能本机跑 → `chrome-users.json` |
| Code360 | Akamai 拒绝机房 IP，r.jina.ai / allorigins 均 403 | 只能本机跑 |
| OEIS / Observable / Code360 | 都不发 CORS 头 | 本机跑；Observable 对空 UA 或连续请求返回 429，带浏览器 UA 且别连打 |
| 牛客 | sparta API 只有昵称，数据在竞赛主页 HTML 里 | 解析 HTML；无 CORS → 本机跑 |
| LintCode | 无公开统计接口，SPA | 放弃 |
| 51CTO | 腾讯云 EdgeOne WAF 拦截页 | 放弃 |
| Bilibili 播放量 | 需 wbi 签名，播放总数只在创作中心 | 放弃 |
| 微信公众号 / 视频号 / 即刻 | 无公开接口 | 做不到 |
| 微博 / 小红书 / X / Instagram / Threads | 反爬或需登录态 | 不建议 |
| GitHub Actions 定时 | 该账号的 `schedule` 不触发（空仓库验证过，`workflow_dispatch` 正常） | 本仓库不放定时 workflow |
| Lark wiki | 目录树 API 返回 `Login Required`，只有带会话的浏览器能读 | 只放链接 + 静态计数 |

## 撤掉的展示

- **Bilibili 35 粉 / 抖音 71 赞**：数据条里最弱的两格，换成博客阅读量与 AoC 名次。
- **HackerRank 认证格**：11 张认证 + 2 枚徽章，数字太小，从数据条撤下，改在 Problem solving 正文里写「11 verified HackerRank certifications (2 skill badges)」。
- **网易云音乐 / 豆瓣 / 简书**：和找工作无关且数字太弱，一度撤掉；简书后来作为「以后会发布」的链接放回，网易云与豆瓣仍不展示。

## 调研结论：还能接什么

结论：**没有新的值得接的社媒源。** 下表是逐平台实测记录，不要重复调研；只有拿到新账号链接时才需要重开。

| 平台 | 账号 | 实测 | 结论 |
| --- | --- | --- | --- |
| GitLab | `yhm138`（id 9277119） | 0 公开项目、无 follower、API 无 CORS | 没内容 |
| V2EX | `yhm138` | 404 | 无账号 |
| ModelScope | `author=yhm138` | 404 | 无模型 |
| Hugging Face | `yhm138` | 无模型 / 数据集 | 没内容 |
| npm | `yhm138` / `~aspen138` | 0 个包 | 先放链接（等发布） |
| crates.io | `yhm138`（id 201685） | 0 crate、0 下载 | 先放链接（等发布） |
| Docker Hub | `aspen138` | 0 仓库 | 先放链接（等发布） |
| SourceForge | `aspen138` | Cloudflare 验证页 | 先放链接，取不到数据 |
| Kaggle | `aspen138` | reCAPTCHA | 先放链接，取不到数据 |
| JetBrains Marketplace | `/author/me` | 匿名访客只见登录页，公开 URL 要等插件上线 | 先放链接，上线后换 `/author/<vendor>` |
| Google Play | 开发者 ID 7351019373232905041 | 后台地址对匿名访客重定向到 Google 登录；公开页 `store/apps/dev?id=...` 目前 404 | 先放链接，上线第一个应用后换成公开页 |
| AtCoder | `yhm138` | 账号存在，无 rating / 比赛记录 | 不值得放 |
| 网易云音乐 | `id=1544379686` | API 可取 2,873 首 / level 7 / 7 歌单 / 0 粉 | 只放链接（页面未放） |
| 豆瓣 | `220820619` | 匿名看不到关注数，广播需登录 | 只放链接（页面未放） |
| 简书 | `796435070e0c` | 2 篇 / 1 粉 / 38 字 | 先放链接（等发布） |
| 天池 | `userId=1095279495628` | `home/science/races` 返回 3 场比赛，`getByUserId` 显示 Junior Developer 勋章；带 CORS | 页面显示「3 competitions」 |
| YouTube | `@yhm138`、`@aspen1382020` 均 404 | — | 有频道再给链接 |

另外：已有平台上还有些「小数字」没展示（CSDN 粉丝 16 / 获赞 17 / 收藏 167 / 排名 42,007，掘金关注 2 / 掘力值 97，Gitee followers 0）。它们都在 `profiles.json` 里——量级低于 100 的指标只会稀释已有的强数字，别为了凑数放上去。

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
