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
| PyPI 累计下载（3,950） | Cloudflare Worker | 10 分钟 |
| RosettaCode（465 任务页 / 43 新建） | Cloudflare Worker | 10 分钟 |
| Chrome 扩展用户（671 / 6 个） | 本机计划任务 → `chrome-users.json` | 每周一（开机则更新） |

页面上用两种圆点区分：实心 = 每次访问实时取；空心 = 定时缓存或本地刷新。

## 三层降级

```
① Cloudflare Worker  /metrics
      ↓ 不可达
② metrics.json        仓库里的快照
      ↓ 读不到
③ index.html 里的静态值
```

任何一层挂掉，页面显示的是旧数字，不会空白，也不会跳变。这是刻意设计的：外部依赖失败时，最坏结果是“不新鲜”，不是“打不开”。

## 文件

| 文件 | 作用 |
| --- | --- |
| `index.html` | 页面全部内容与样式 |
| `metrics.json` | 指标快照，Worker 不可达时的兜底 |
| `metrics.py` | 本地抓取脚本，用来重新生成 `metrics.json` |
| `chrome-ids.json` | 6 个扩展到 Chrome Web Store ID，Worker 读取它 |
| `chrome-users.json` | 扩展用户数合计与逐项明细，由本机计划任务发布 |

## Cloudflare Worker

- 地址：`https://autumn-thunder-2ee6.aspen1382020.workers.dev`
- `GET /metrics` → JSON，带 `Access-Control-Allow-Origin: *`
- `GET /` → 状态页，逐项显示数值与来源通道
- 缓存 10 分钟；代码不在本仓库，在 Cloudflare 控制台维护

Worker 负责“浏览器取不到”的那几项：这些站点要么不发 CORS 头，要么需要服务端请求。

## 哪些没法自动，为什么

**知乎的公开接口拒绝机房 IP。** pi/v4/members/... 在住宅网络下返回精确数字，从 Cloudflare 出口取则被挡。所以知乎两个数改由本机每周跑脚本发布成 web-stats.json。

**Chrome Web Store 拒绝机房 IP。** Cloudflare Worker 和 GitHub Actions 的出口 IP 都被 Google 挡（403 或返回没有用户数的落地页），`r.jina.ai` 代理能取到页面但拿不到统计。只有住宅网络能直连，所以改成本机每周跑一次脚本，把结果提交成 `chrome-users.json`。

**GitHub Actions 的 `schedule` 在这个账号上不触发。** 用一个独立的、只有 5 分钟 cron 的空仓库验证过：连续多次触发点均为 0 次运行，且 `workflow_dispatch` 正常。平台状态当时无故障。因此本仓库不含任何定时 workflow。

## 怎么维护

**新增或下线扩展**：改 `chrome-ids.json` 里的 `ids` 数组即可，Worker 下次请求就会用新列表。下线的扩展详情页返回 404，会被自动跳过。

**刷新快照**：

```bash
python metrics.py && git add metrics.json && git commit -m "chore: refresh metrics" && git push
```

**刷新 Chrome 用户数**：运行 `update-chrome-users.py`（需要本机已登录 `gh`）。它会抓六个商店页、算出合计，通过 GitHub API 直接提交 `chrome-users.json`，不需要本地 clone。

计划任务已注册为每周一 09:30：

```
TaskName : \resume chrome users
命令     : C:\Users\Yangh\resume-metrics\run.cmd
日志     : C:\Users\Yangh\resume-metrics\run.log
```

## 依赖

`metrics.py` 中 Chrome 那一段需要 `playwright` + Chromium；其余数据源只用标准库。`update-chrome-users.py` 只依赖标准库和 `gh` CLI。
