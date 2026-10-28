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
| Stack Exchange 全站声誉（24.7k / 118 站） | Cloudflare Worker | 10 分钟 |
| PyPI 累计下载（3,951） | Cloudflare Worker | 10 分钟 |
| RosettaCode（465 任务页 / 43 新建） | Cloudflare Worker | 10 分钟 |
| 博客园总阅读（164,729 / 139 篇） | Cloudflare Worker | 10 分钟 |
| Bilibili 粉丝 / 视频数（35 / 10） | Cloudflare Worker | 10 分钟 |
| 抖音获赞 / 作品数（71 / 2） | Cloudflare Worker | 10 分钟 |
| LeetCode 通过题数（1,953，站点排名 1,612） | Cloudflare Worker | 10 分钟 |
| HackerRank 徽章（5 个 / 65 题） | Cloudflare Worker | 10 分钟 |
| 知乎赞同 / 收藏（937 / 1,833） | 本机计划任务 → `web-stats.json` | 每周一（开机则更新） |
| Chrome 扩展用户（671 / 6 个） | 本机计划任务 → `chrome-users.json` | 每周一（开机则更新） |

页面上用两种圆点区分：实心 = 每次访问实时取；空心 = 定时缓存或本地刷新。数据条共 10 格，桌面 5 列、移动 2 列。

> 知乎的三个数字容易混：`voteup_count` 是赞同（937），`favorited_count` 是收藏（1,833），`thanked_count` 是感谢（620）。简历正文里说的“620 次喜欢”指的是感谢数。

> 抖音的 `follower_count` 对未登录访客返回 `null`，所以那一格放的是**获赞数**（`total_favorited`），不是粉丝数；`mplatform_followers_count` 是唯一对游客可见的粉丝字段（当前值 6）。

## 三层降级

```
① Cloudflare Worker  /metrics
      ↓ 不可达
② metrics.json        仓库里的快照
      ↓ 读不到
③ index.html 里的静态值
```

任何一层挂掉，页面显示的是旧数字，不会空白，也不会跳变。这是刻意设计的：外部依赖失败时，最坏结果是“不新鲜”，不是“打不开”。

`web-stats.json` 和 `chrome-users.json` 走的是第四种模式——它们是本机发布的文件，页面直接读，不经 Worker。

## 文件

| 文件 | 作用 |
| --- | --- |
| `index.html` | 页面全部内容与样式 |
| `metrics.json` | 指标快照，Worker 不可达时的兜底 |
| `metrics.py` | 本地抓取脚本，用来重新生成 `metrics.json` |
| `chrome-ids.json` | 6 个扩展到 Chrome Web Store ID，Worker 读取它 |
| `chrome-users.json` | 扩展用户数合计与逐项明细，由本机计划任务发布 |
| `web-stats.json` | 知乎赞同/收藏与博客园总阅读，由本机计划任务发布 |

## Cloudflare Worker

- 地址：`https://autumn-thunder-2ee6.aspen1382020.workers.dev`
- `GET /metrics` → JSON，带 `Access-Control-Allow-Origin: *`
- `GET /` → 状态页，逐项显示数值与来源通道（`primary` / `fallback` / `unavailable`）
- 缓存 10 分钟；代码不在本仓库，在 Cloudflare 控制台维护

Worker 负责“浏览器取不到”的那几项：这些站点要么不发 CORS 头，要么需要服务端请求。目前它跑九个源：GreasyFork、PyPI、Stack Exchange、RosettaCode、博客园、Bilibili、抖音、LeetCode、HackerRank。

## 哪些没法自动，为什么

**知乎的公开接口拒绝机房 IP。** `https://www.zhihu.com/api/v4/members/...` 在住宅网络下直接返回精确数字，从 Cloudflare 出口取则被挡。所以知乎两个数改由本机每周跑脚本发布成 `web-stats.json`。

**抖音的网页端是 JS 反爬，但旧版分享接口还活着。** `douyin.com/user/...`、`iesdouyin.com/share/user/...`、`m.douyin.com/...` 三个地址返回的都是同一份 72 KB 的 `_$jsvmprt` 混淆脚本，正文为空；而 `https://www.iesdouyin.com/web/api/v2/user/info/?sec_uid=...` 仍返回 JSON。注意它对未登录访客把 `follower_count` 置为 `null`（用浏览器渲染确认过：页面上“关注/粉丝/获赞”三个标签都在，数字是空的）。

**LeetCode 的做题数只能走 GraphQL。** 个人主页是 Next.js 渲染的，但 https://leetcode.cn/graphql/ 允许匿名 POST 查询 userProfileUserQuestionProgress，一次拿到三档难度的通过题数与站点排名——2026-10 实测：简单 701、中等 936、困难 316，合计 1,953，排名 1,612。

**HackerRank 用的是旧版 REST 接口。** 
est/hackers/<user>/badges 与 .../scores 仍返回 JSON，页面本身是 React 渲染的。

**LinkedIn 完全取不到。** 任何非登录请求都返回 HTTP 999（LinkedIn 的反爬状态码），且抓取违反其条款。页面上只保留链接。

**牛客没有公开的统计数据。** gw-c.nowcoder.com/api/sparta/user/profile/<id> 能拿到昵称、学历、身份标签，但刷题数、排名都不对外，所以没有可展示的数字。

**Bilibili 的播放量需要 wbi 签名。** `x/relation/stat`（粉丝/关注）和 `x/space/navnum`（视频/文章数）都免签名，但 `x/space/arc/search` 返回 412，要 wbi 签名才能取播放量，因此只展示粉丝与视频数。

**Chrome Web Store 拒绝机房 IP。** Cloudflare Worker 和 GitHub Actions 的出口 IP 都被 Google 挡（403 或返回没有用户数的落地页），`r.jina.ai` 代理能取到页面但拿不到统计（它只渲染非 JS 版本）。只有住宅网络能直连，所以改成本机每周跑一次脚本，把结果提交成 `chrome-users.json`。

**博客园没有“总阅读数”的正文字段，只有一个 AJAX 片段。** `https://www.cnblogs.com/yhm138/ajax/blog-stats` 返回 242 字节的 HTML 片段，里面有 `title="总阅读数: 164729"` ——悬停博客侧边栏“阅读 - 16万”看到的就是它。注意这个数和“逐篇文章阅读数之和”不是一个口径（后者约 11 万），因为它包含首页与分类页的浏览。

**GitHub Actions 的 `schedule` 在这个账号上不触发。** 用一个独立的、只有 5 分钟 cron 的空仓库验证过：连续多次触发点均为 0 次运行，且 `workflow_dispatch` 正常，平台状态当时无故障。因此本仓库不含任何定时 workflow。

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

## 依赖

`metrics.py` 中 Chrome 那一段需要 `playwright` + Chromium；其余数据源只用标准库。`update-chrome-users.py` 与 `update-web-stats.py` 只依赖标准库和 `gh` CLI。
