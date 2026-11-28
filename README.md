# resume

线上简历：**https://yhm138.github.io/resume/**

单文件页面（`index.html`，样式内联，无构建）+ 一个 Cloudflare Worker + 两个本机计划任务。每个数字的取数通道不同，取不到就退回旧值，不会空白。

## 数据链路

```
① 浏览器直连（每次访问，页面自己 fetch）
   GitHub · GreasyFork · Stack Exchange 分站/徽章 · Codeberg · 天池 · npm downloads
   ipinfo.io（+ BigDataCloud 精修）· vercount.one（PV/UV 脚本）
② Cloudflare Worker /metrics（缓存 10 分钟）
   PyPI · SE 全站 · RosettaCode · 博客园阅读 · LeetCode · Codewars · leetcode.com · 抖音
       ↓ Worker 不可达
③ metrics.json（仓库里的快照）→ 再退到 index.html 里的静态值
④ 本机两个计划任务（每天 09:30 / 09:40，直写 main，页面直接读 raw）
   09:30  \resume chrome users  → chrome-users.json（Chrome Web Store）
                                  + web-stats.json（知乎 / 博客园）
   09:40  \resume profile stats → profiles.json（12 个无 CORS 的源）
                                  + visitor-map.json + web-stats.json（冗余再跑一次）
```

- 写文件的通道只有两种：Worker（10 分钟）和本机脚本（每天）。页面读 `raw.githubusercontent.com`，不经过 Worker。
- 每个数字都有静态兜底：接口失败就保留上一次的值或 HTML 里的静态值，不会出现空白或 NaN。
- Worker 的 `sources` 字段标 `primary` / `fallback` / `unavailable`；**口径不同的兜底值页面不采用**——RosettaCode 的 API 兜底只有 204 条贡献行，和账号页的 465 个任务页不是同一个数，所以只在 `sources.rosetta == "primary"` 时才覆盖。
- 静态、不更新：AoC 2024 全球 #14（1,699 分）、AIME/Putnam wiki 101 页。

## 指标来源

> 下表按**更新频率**排序：每次访问 → 10 分钟 → 每天 → 不更新。括号里的数字是写表时的快照，线上以页面显示为准。

| 指标 | 载体 | 更新频率 |
| --- | --- | --- |
| GitHub 仓库数（54） | 浏览器直连 GitHub API | 每次访问 |
| GreasyFork 安装量（11.8k / 82 脚本） | 浏览器直连 GreasyFork API | 每次访问 |
| GreasyFork 好评（42） | 浏览器直连 GreasyFork API | 每次访问 |
| Stack Exchange 分站声誉 | 浏览器直连 SE API | 每次访问 |
| Stack Exchange 徽章（347，associated 分页汇总） | 浏览器直连 SE API（分页） | 每次访问 |
| 访客城市 / 国家（`≈` = IP 估算，`locate me` = 设备定位） | 浏览器直连 ipinfo.io（降级 api.country.is）；精修走 Geolocation + BigDataCloud 反查 | 每次访问 / 按需 |
| 整站 PV / UV | vercount.one 脚本（busuanzi 兼容） | 每次访问 |
| Codeberg 仓库数（5） | 浏览器直连 Codeberg API（Gitea/Forgejo） | 每次访问 |
| 天池（3 场比赛） | 浏览器直连 Tianchi API（带 CORS） | 每次访问 |
| dsh-image-rescue npm 累计下载（动态，静态兜底 713） | 浏览器直连 npm downloads API（发布日 2026-11-12 至今逐日求和） | 每次访问 |
| dsh-btw npm 累计下载（动态，静态兜底 2,129） | 浏览器直连 npm downloads API（发布日 2026-11-17 至今逐日求和） | 每次访问 |
| dsh-codex-session-pin npm 累计下载（动态，静态兜底 782） | 浏览器直连 npm downloads API（发布日 2026-11-21 至今逐日求和） | 每次访问 |
| Stack Exchange 全站声誉（24.7k / 118 站） | Cloudflare Worker | 10 分钟 |
| PyPI 累计下载（4,036） | Cloudflare Worker | 10 分钟 |
| RosettaCode（465 任务页 / 43 新建；仅主通道成功时采用） | Cloudflare Worker | 10 分钟 |
| 博客园总阅读（166,129 / 139 篇） | Cloudflare Worker | 10 分钟 |
| LeetCode 通过题数（1,953） | Cloudflare Worker | 10 分钟 |
| Codewars（38 kata / 5 kyu） | Cloudflare Worker | 10 分钟 |
| leetcode.com 通过题数（14） | Cloudflare Worker | 10 分钟 |
| 博客阅读量（222k = 博客园 + CSDN + 掘金） | Worker + 本机 `profiles.json` | 10 分钟 / 每天 |
| 知乎回答 / 赞同 / 收藏 / 感谢（164 / 947 / 1,850 / 619） | 本机计划任务 A 与 B 都会跑 `update-web-stats.py` → `web-stats.json` | 每天（开机则更新；值不变不提交） |
| 博客园文章数（139） | 本机计划任务 A 与 B 都会跑 `update-web-stats.py` → `web-stats.json` | 每天（开机则更新；值不变不提交） |
| Chrome 扩展用户（663 / 6 个） | 本机计划任务 A → `chrome-users.json` | 每天（开机则更新；内容不变不提交） |
| HackerRank 认证（11 张 / 2 枚徽章） | 本机计划任务 → `profiles.json` | 每天（开机则更新） |
| Codeforces（127 题 / 峰值 1,485） | 本机计划任务 → `profiles.json` | 每天（开机则更新） |
| 牛客（490 已通过 / 613 已挑战） | 本机计划任务 → `profiles.json` | 每天（开机则更新） |
| OEIS（3 序列 / 8 修订） | 本机计划任务 → `profiles.json` | 每天（开机则更新） |
| Observable（1 notebook） | 本机计划任务 → `profiles.json` | 每天（开机则更新） |
| Code360（1 题通过 / 250 分） | 本机计划任务 → `profiles.json` | 每天（开机则更新） |
| CSDN（53,040 访问 / 8 篇 / 16 粉） | 本机计划任务 B → `profiles.json` | 每天（开机则更新） |
| 掘金（3,298 阅读 / 8 篇） | 本机计划任务 B → `profiles.json` | 每天（开机则更新） |
| Gitee（1 仓库 / 9 commits） | 本机计划任务 → `profiles.json` | 每天（开机则更新） |
| Bluesky（0 帖 / 6 粉）、Mastodon（2 帖 / 0 粉） | 本机计划任务 → `profiles.json` | 每天（开机则更新） |
| 访客分布地图（按国家；页面每次访问给本国 +1） | 本机计划任务 B → `visitor-map.json` | 每天（开机则更新；计数不变不提交） |
| ScriptCat（6 脚本 / 2,780 安装） | 本机计划任务 B → `profiles.json`（后端 JSON API 无 CORS） | 每天（开机则更新） |
| Advent of Code 2024 全球名次（#14 / 1,699 分） | 静态（历史赛果） | 不更新 |
| AIME / Putnam 解法 wiki（101 页） | 静态（一年加一两页） | 不更新 |

三条口径提醒：

- 知乎四个数别混：`answer_count` 回答（164）、`voteup_count` 赞同（947）、`favorited_count` 收藏（1,850）、`thanked_count` 感谢（619）。
- 博客园「总阅读数」含首页与分类页浏览，不等于逐篇阅读之和（后者约 11 万）；「博客阅读量」是博客园 + CSDN + 掘金三家相加，任一源缺值就不出总数。
- 数据条共 10 格（桌面 5 列 × 2 行，≤780px 2 列），顺序：repos / GF installs / SE reputation / RosettaCode / PyPI / Chrome / blog reads / AoC / LeetCode / SE badges。实心圆点 = 每次访问实时取，空心 = 定时或本机刷新。

**页面最底部**（页脚里）是访客信息：`you · 城市, 国家`（ipinfo.io 按访客 IP 判断，带 `≈` 表示是估算值；点 `locate me` 用设备定位精修）、`views` / `visitors`（vercount 的整站 PV / UV，按域名计，不是本页单独计数），下面一张点阵世界地图：陆地用分隔线色画点，访客国家用 teal 圆点（半径随访问量开方增长），数据来自 `visitor-map.json` 的每日快照。这两块都带 `js-only`，打印时不出现。

## 通道细节

- **浏览器直连**：GitHub、GreasyFork、Stack Exchange、天池、Codeberg（Gitea/Forgejo API）、npm downloads API（`api.npmjs.org`）都带 CORS，页面每次访问直接取；SE 徽章走 `users/21083779/associated`，117 个分站 > 100 条/页，必须翻页，否则少算（曾少算成 306）。
- **Cloudflare Worker（v3，当前线上就是 v3，源码见 `worker.js`）**：`https://autumn-thunder-2ee6.aspen1382020.workers.dev/metrics`，缓存 10 分钟，`Access-Control-Allow-Origin: *`；`GET /` 是状态页（`primary` / `fallback` / `unavailable`，并列出本次缺了哪些字段）；`GET /?nocache=1` 绕过缓存。
  - v3 修的东西：GreasyFork 改用规范地址（旧地址 301 且跳转后丢 CORS）；Bilibili / 抖音 / LeetCode 加浏览器 UA + referer（旧的 `resume-metrics` UA 被拒，这正是那几个字段从返回里消失的原因）；Bilibili 增加 `x/relation/stat` 兜底；Stack Exchange 改为「账号页抓取为主、API `/associated` 兜底」；知乎从 Worker 移除（所有机房 IP 都 403，只能本机跑）。
  - 口径差异：账号页抓到 118 站 / 24,701；SE API `associated` 是 117 站 / 24,600。两个都算对，只是站点集合不同，页面按抓到的那个数显示。
  - RosettaCode 会间歇性被 Cloudflare challenge：主通道（账号页）挂掉时 Worker 会退到 MediaWiki `usercontribs` 兜底，但那条只返回 204 条贡献行、口径和 465 个任务页不同，页面只在 `sources.rosetta == "primary"` 时采用，否则保留 465 / 43；两条都失败也一样落到静态值。
- **本机任务 A**（`\resume chrome users`，每天 09:30，`C:\Users\Yangh\resume-metrics\run.cmd`）：`update-chrome-users.py` + `update-web-stats.py`，通过 `gh` 直接提交；跑的是拒绝机房 IP 的源（Chrome Web Store、知乎）。任务 B 也会跑一次 `update-web-stats.py`（见下），两边都跑是刻意的冗余：`web-stats.json` 值没变就不提交，不会有重复提交；`chrome-users.json` 内容没变同样不提交；发布撞车（别人刚写过）会重试一次。
- **本机任务 B**（`\resume profile stats`，每天 09:40）：仓库根目录 `python update-profiles.py`，跑完再用同一个 Python 跑 `C:\Users\Yangh\resume-metrics\update-web-stats.py`（知乎 + 博客园 → `web-stats.json`）；两个脚本的退出码都会写进日志并向上传递，任一失败任务结果就是失败。`update-profiles.py` 每次先 `git fetch` + `git rebase origin/main` 再动手——任务 A 用 gh API 直接写主分支，不同步就 push 会被 `fetch first` 拒掉（2026-11 因此静默失败两周）；push 失败重试 3 次、每次重试前再同步一次；只要本地还有没推的提交，即使本次数字没变也会补推；访客地图每次都重算，但计数没变就不重写（`generated_at` 单独变不值得一次提交）；某个源返回全 null（反爬页、页面改版）按失败处理、保留上一次的值，部分字段为 null 时也只补非空字段；失败会打印 `ERROR:` 并以非零码退出，完整日志在 `%LOCALAPPDATA%\resume-profile-task.log`。跑的是无 CORS 的源（OEIS、Observable、Code360、CSDN、掘金、Gitee、牛客、Codeforces、HackerRank、Bluesky、Mastodon、ScriptCat）。
- **访客信息**：城市/国家靠 ipinfo.io（失败退回 api.country.is，只到国家），PV/UV 靠 vercount.one 的脚本（写一个 1 年期 cookie 用来判首次 UV，本地 localStorage 缓存上次值）。这两项都会把访客 IP 发给第三方；页面本身不写 cookie。两者都失败时显示 `—`，不影响其它数字。

  城市前加 `≈` 是因为 IP 库只能到 ISP 登记的机房城市（合肥的家宽常被判成上海）；点 `locate me` 走浏览器 Geolocation（Wi-Fi/GPS，授权一次、之后每次访问静默复用），坐标只发给 BigDataCloud 的 client 反查接口换地名，精修时不再给该国计数器 +1。拒绝授权或设备定位失败就保留 IP 估算值，不影响其它数字。
- **访客分布地图**：页面每访问一次，按 ipinfo 给的国家调一次 `abacus.jasoncameron.dev/hit/yhm138resume/c-<iso2>`（只对 64 个被追踪的国家/地区，其余忽略）；每天的任务再把每个国家的计数器读出来写进 `visitor-map.json`（计数没变不重写）。地图本身是页内 SVG：96×48 陆地掩码（base64，768 字节）+ 64 个国家经纬度，全部内联，不加载任何地图库或瓦片。

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
| `profiles.json` | 12 个平台的计数器（见上表「每天」部分） |
| `visitor-map.json` | 各国家访客数（abacus 计数器聚合，每日快照；计数不变不重写） |
| `update-profiles.py` | 采集 `profiles.json` + `visitor-map.json`，先 fetch+rebase 再 commit + push（失败重试、非零退出） |
| `worker.js` | Cloudflare Worker 源码（改完手动粘到控制台部署；仓库这份是源，不是部署产物） |

## 项目条目（页面 05 节）

| 项目 | 链接 | 页面上的数字 | 口径 / 备注 |
| --- | --- | --- | --- |
| workbuddy-toolkit | [GitHub](https://github.com/yhm138/workbuddy-toolkit) | 无 | 3 个 WorkBuddy 桌面扩展（会话桥、复制会话 ID、云会话），CI 跑 Windows 与 Linux |
| dsh-image-rescue | [GitHub](https://github.com/yhm138/dsh-image-rescue) · [npm](https://www.npmjs.com/package/dsh-image-rescue) · [市场页](https://awesome-dsh-plugin.com/p/yhm138/dsh-image-rescue/) | npm 累计下载（动态，静态兜底 358） | 页面每次访问从 npm downloads API 现算：发布日 2026-11-12 到今天逐日求和，数字链到 npm-stat 趋势图；npm 统计含自动更新 / 镜像 / 爬虫，**不等于用户数**。0 star / 0 fork / 0 issue 与 60 次 clone（14 天、33 个来源）不展示 |
| dsh-btw | [GitHub](https://github.com/yhm138/dsh-btw) · [npm](https://www.npmjs.com/package/@aspen138/dsh-btw) · [市场页](https://awesome-dsh-plugin.com/p/yhm138/dsh-btw/) | npm 累计下载（动态，静态兜底 2,129） | 页面每次访问从 npm downloads API 现算：发布日 2026-11-17 到今天逐日求和，数字链到 npm-stat 趋势图；npm 统计含自己反复安装 / CI / 镜像，**不等于用户数**。Star 2 / Fork 0 / watcher 0 / issue 0 按「低于 100 不展示」不写进页面 |
| dsh-codex-session-pin | [GitHub](https://github.com/yhm138/dsh-codex-session-pin) · [npm](https://www.npmjs.com/package/dsh-codex-session-pin) · [市场页](https://awesome-dsh-plugin.com/p/yhm138/dsh-codex-session-pin/) | npm 累计下载（动态，静态兜底 782） | 页面每次访问从 npm downloads API 现算：发布日 2026-11-21 到今天逐日求和，数字链到 npm-stat 趋势图；npm 统计含自己反复装卸 / CI / 镜像，**不等于用户数**。Star 0 / Fork 0 / watcher 0 / issue 0 按「低于 100 不展示」不写进页面 |

dsh-image-rescue 的契约事实（2026-11-17 用 npm registry + GitHub API 核过）：版本 `0.1.0`，`engines.dsh = ">=0.2.1-rc.2 <0.3.0-0"`，`dsh.bundle.patch: ./cordis.patch.yml`，发布物 11 个文件 / 85.3 kB（registry `dist.fileCount=11`；tarball 实测 85,294 字节，sha1 与 shasum `f86fcdac49c4dce712ab87717b376917102f4162` 一致）。挂载 `@deepseek-ai/dsh-attachment` 的 `ctx.attachments`：`admitPromptContent(content: AttachmentAdmissionPart[]) → Promise<AdmittedPromptContentPart[]>`、`imageLimits`（maxImageBytes / maxImagesPerMessage / maxMessageImageBytes / maxImagePixels / maxImageDimension / mediaTypes）、`validateImage`、`saveImage`、`saveFile`、`fileHostPath`、`readFileStream`；类型 `AttachmentAdmissionPart` = text | image（mediaType + base64 data）| file，返回 `AdmittedPromptContentPart` = text | image 附件 | file 附件，文件引用 `{attachmentId, name, bytes}`。插件导出 `apply(ctx, config)`、`inject = ['attachments']`、`wrapAttachmentStore(store, config)`；配置项 `enabled`（默认 true）、`note`（默认一句中文，`false` 关闭）。救回 `IMAGE_DIMENSION_TOO_LARGE`、`IMAGE_TOO_MANY_PIXELS`、`IMAGE_TOO_LARGE`、`IMAGES_TOO_LARGE`、`TOO_MANY_IMAGES`，`INVALID_IMAGE` 等输入损坏类不救回。awesome-dsh-plugin 的 jsdelivr（#1）与站点（#3）索引都收录，bruc3van 精选（#2）未收录。

dsh-btw 的仓库重建（2026-11-26 核过）：旧仓库（2026-11-17 创建，历史里带真实 DSH 窗口截图）已删除，同名重建为 https://github.com/yhm138/dsh-btw —— 创建 **2026-11-26T05:36:10Z**、默认分支 `main`、**只有 1 个 root commit**（`86470ef`，message 首行 `dsh-btw 0.3.2`）、24 个文件；6 张图全是构造图（`assets/icon-180.png`、`assets/screenshot.png`、`docs/screenshot-{panel,button,followup,settings}.png`）；全仓扫描测试口令字面量为 0（旧口令已改成占位符）。**仓库年龄归零**：以后若要提新的市场条目会重新触发「满 1 天」门槛，现有市场条目地址不变。页面不写仓库创建时间与 commit 数。

dsh-btw 的发布事实（2026-11-26 用 npm registry + GitHub API 核过）：npm `@aspen138/dsh-btw` 最新 `0.3.2`（2026-11-26T05:29:21Z），共 11 个版本（0.0.0-stage / 0.1.0 / 0.1.1 / 0.1.2 / 0.2.0 / 0.2.1 / 0.2.2 / 0.2.3 / 0.3.0 / 0.3.1 / 0.3.2）；发布物 10 个文件、解包 105,285 字节、无运行期依赖；MIT；topics `dsh-plugin` / `deepseek-harness`；市场分类 `ui`、`compatible: true`；0.3.2 是从清理后的树重新发布的，功能与 0.3.1 相同。0.3.x 的改动：追问改为预算口径（`maxThreadTurns` 默认 20 轮、`maxThreadChars` 默认 24,000 字符，从最新往回取，超长单轮截断而不是整条丢弃）；追问链改为从会话日志重建（`--continue <childId>` 串联），插件重载 / profile 重组 / Host 重启后仍能接上；设置页 HTTP 路由改用 Host 的 `ctx.connection.requestRejection`（实测匿名 401 / 已登录 200）。

dsh-btw 的边界事实（2026-11-23 复核）：仓库与 npm 包里的截图是**构造图**（用插件自己的 CSS 渲染虚构内容），不是真实 DSH 窗口截图；侧问子 agent 受沙箱策略约束（默认 `workspace-write`，只能改当前工作区，写工作区外直接拒绝），页签里能看到工具调用与结果，但 **DSH 对文件写入不走审批**——页面与文档都不要写「审批提示」。另：awesome-dsh-plugin 市场索引仍显示 `0.3.1`（落后 npm 的 `0.3.2`，等夜间构建），条目地址不变；描述里那句访问校验的披露不要照抄，**页面版本以 npm 为准**。

dsh-codex-session-pin 的发布事实（2026-11-26 用 npm registry + GitHub API 核过）：npm `dsh-codex-session-pin` 最新 `1.0.2`（2026-11-21T12:10:48Z），共 4 个版本（0.0.0-stage / 1.0.0 / 1.0.1 / 1.0.2）；发布物 12 个文件、解包 65,105 字节、`dependencies` 与 `peerDependencies` 均为空、`engines.dsh = ">=0.2.1-rc.2 <0.3.0-0"`；MIT；topics `dsh-plugin` / `deepseek-harness` / `session` / `pin` / `sidebar` / `codex-ui`；awesome-dsh-plugin 收录（分类 `session`，PR #17716 于 2026-11-22T16:53:27Z 合并）。

dsh-codex-session-pin 的边界事实：市场描述里带一句「HTTP 路由没有 DSH 访问检查」的披露，**页面不抄、也不写任何访问控制或安全加固**，更不把路由当对外接口介绍；该插件与 dsh-btw 0.3.2（用 `ctx.connection.requestRejection`）不同，路由目前确实还没有访问校验。


npm 周下载快照（写表时的记录；页面现在展示动态累计值，不再展示周窗口）：
- `@aspen138/dsh-btw` 1,217（窗口 11-15~11-21；逐日 0 / 0 / 485 / 210 / 191 / 280 / 51，首发日 11-17）
- `dsh-codex-session-pin` 753（窗口 11-18~11-24；逐日 0 / 0 / 0 / 624 / 29 / 49 / 51，发布日 11-21）

## 维护

- **刷新快照**：`python metrics.py && git add metrics.json && git commit -m "chore: refresh metrics" && git push`
- **改 Worker**：编辑仓库里的 `worker.js` → 复制粘贴到 Cloudflare 控制台 → 部署；然后开 `https://autumn-thunder-2ee6.aspen1382020.workers.dev/` 看每个源是 `primary` / `fallback` / `unavailable`，再开 `?nocache=1` 确认新值。
- **刷新 Chrome / 知乎 / 博客园**（任务 A，每天 09:30，日志 `C:\Users\Yangh\resume-metrics\run.log`）：手动跑 `python C:\Users\Yangh\resume-metrics\update-chrome-users.py` 或 `... \update-web-stats.py`（都幂等：值没变就打印 `unchanged, not publishing` 并以 0 退出）。
- **刷新平台计数器 / 访客地图**（任务 B，每天 09:40，日志 `%LOCALAPPDATA%\resume-profile-task.log`）：仓库根目录 `python update-profiles.py`；单独重算访客地图要跑完整的 64 个国家 GET，约 30 秒。
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
| GitHub Actions 定时 | 该账号 `schedule` 不触发（2026-11-17 复测：`main` 上放 `cron: "*/5 * * * *"` 探针工作流，41 分钟内 0 次 schedule 事件；同一工作流手动 `workflow_dispatch` 17 秒跑完。Actions 服务本身正常，只有定时不触发） | 不放定时 workflow；需要定时就用本机计划任务 |
| Lark wiki | 目录树 API 返回 `Login Required`，只有带会话的浏览器能读 | 只放链接 + 静态计数 |

## 撤掉的展示

- **Bilibili 35 粉 / 抖音 71 赞**：数据条最弱的两格，换成博客阅读量与 AoC 名次。
- **HackerRank 认证格**：11 张认证 + 2 枚徽章，数字太小，从数据条撤下，改在 Problem solving 正文写「11 verified HackerRank certifications (2 skill badges)」。
- **网易云音乐 / 豆瓣**：和找工作无关且数字太弱，链接都不放；简书、Bluesky、Mastodon 按「以后会发布」保留链接但不展示数字。
- **dsh-image-rescue 的 0 star / 0 fork / 0 issue 与 14 天 60 次 clone（33 个独立来源）**：clone 基本是爬虫 / 镜像；页面只写 npm 累计下载（每次访问现算）并注明含 CI 与镜像、不等于用户数，不写 star。
- **dsh-btw 的 star / fork / watcher / issue**：都低于 100（重建后的仓库当前 0 / 0 / 0 / 0），按既有约定不写进页面；条目里只写 npm 累计下载（动态、链到 npm-stat，注明含 CI/镜像、不等于用户数）。
- **dsh-codex-session-pin 的 0 star / 0 fork / 0 watcher / 0 issue**：同样不写进页面；条目里只写 npm 累计下载（动态、链到 npm-stat，注明含 CI/镜像、不等于用户数）。

## 调研结论：还能接什么

**没有新的值得接的社媒源。** 下表是逐平台实测记录，不要重复调研；拿到新账号链接时才需要重开。

| 平台 | 账号 | 实测 | 结论 |
| --- | --- | --- | --- |
| GitLab | `yhm138`（id 9277119） | 0 公开项目、无 follower、API 无 CORS | 没内容 |
| V2EX | `yhm138` | 404 | 无账号 |
| ModelScope | `author=yhm138` | 404 | 无模型 |
| Hugging Face | `yhm138` | 无模型 / 数据集 | 没内容 |
| npm | `aspen138`（`~aspen138`） | 已发布 `dsh-image-rescue` 0.1.0（见「项目条目」）；`yhm138` 账号仍无包 | 已放项目条目 + 链接 |
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

已有平台还有些「小数字」没展示（CSDN 粉丝 16 / 获赞 17 / 收藏 167 / 排名 44,593，掘金关注 2 / 掘力值 97，Gitee followers 0）。它们都在 `profiles.json` 里——量级低于 100 的指标只会稀释已有的强数字，别为了凑数放上去。

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
