# 设计笔记与实测记录

**跑简报时不要读这份。** 只在重新校准环境、域名被拒、结果反常、或想改工作流时读。
运行时需要的一切都在 `runbook.md`。

## token 预算

这个技能的成本结构（一次日报，实测估算）：

| 项 | token |
|---|---|
| 读参考文件 | 2,000（早期版本 18,400） |
| WebSearch 返回（每条约 1.2k） | 8,400（早期 15,600） |
| Routine prompt | 600（早期 1,800） |
| clone / trending / 产出 | 4,500 |
| **合计** | **≈15,500（早期 ≈40,000）** |

早期版本把四个参考文件都标成「必读」，每次载入 18k token，其中绝大部分是设计理由
而非执行所需——**渐进式披露失效是这类技能最大的隐性成本**。
拆成 `runbook.md`（运行时）+ `notes.md`（解释）后降到 2k。

另外两处曾经的浪费：
- 让 agent 每次去读 `notion://docs/enhanced-markdown-spec`（约 5k token），
  而真正要遵守的只有六条规则，直接写进 runbook 即可
- 日报也按周报的量搜 8+5 条 query。日报素材本来就少，5+2 足够，
  多搜的边际收益远低于成本

**改工作流时先问：这段文字是执行时必须的，还是解释为什么的？** 后者进 notes.md。

## 环境校准（2026-08 实测）

Claude Code 云端沙箱的网络策略只放行包管理器和 git，普通 HTTPS 出站一律 403：

```
36kr.com:443 / weibo.com:443 / news.ycombinator.com:443  → gateway 403
github.com/trending → 403（curl）    export.arxiv.org / huggingface.co → 超时
ima.qq.com / liao.ai.qq.com → 000（连接被掐断）
```

所以依赖 `requests`/`playwright` 直连抓取的新闻 skill（如 cclank/news-aggregator-skill，MIT）
在此环境下 45 个源全部返回空数组。本 skill 改走 WebSearch/WebFetch 通道绕开。

**本地机器上没有这个限制**，爬虫版能拿到微博热搜值、HN 分数、Product Hunt 票数这类
本 skill 拿不到的精确数据，两者可以并存互补。

有意思的是 WebFetch 和 curl 的可达性不一致：curl 打 `github.com/trending` 是 403，
但 WebFetch 能拿到完整榜单（含真实 star 增量）。所以 GitHub Trending 走 WebFetch。

## 域名黑名单是怎么来的

`allowed_domains` 里出现任何一个被 Anthropic crawler 屏蔽的域名，
**整个调用直接 400 失败**，不是跳过该域名降级返回。报错会明确点名是哪几个：

```
API Error: 400 The following domains are not accessible to our user agent: [...]
```

批量试探是最高效的摸底方式——一次塞十几个候选域名，报错会把不可用的全列出来。

已知黑名单里 **Reddit 和 The Verge 最容易踩**，这两个是英文 AI 资讯的直觉选择。
Reddit 的讨论只能通过不加 `allowed_domains` 的开放搜索间接捞到（搜索引擎索引的转载）。

## 为什么中英文要各搜一遍

实测两边命中的是**两批完全不同的新闻**，不是同一批的翻译：

- 中文源对国内融资、国产模型发布、政策监管的覆盖远好于英文源
- 英文源对论文、基础设施、硅谷人事变动的覆盖远好于中文源
- 同一件事的中英文口径经常不同（尤其融资金额和估值）——正好用来交叉验证

只搜一种语言会系统性丢掉一半。

## 融资板块：为什么必须两段式

**一段式检索永远填不满六个字段。** 榜单类文章（投中网投融周报、Crunchbase 周榜、
Fierce Biotech tracker）能高效告诉你「本期有哪些交易」，但几乎从不给估值和创始人履历；
而公司深度报道能给创始人背景，但你得先知道该搜哪家。

实测：一条 `星动纪元 人形机器人 融资 估值 创始人 陈建宇 清华` 同时拿到了成立时间、
产品迭代次数、交付量、客户结构、历轮投资方、最新估值、创始人的本科/博士/任职履历
——六字段一次填满。**第一段扫榜时看到创始人姓名，第二段务必带上。**

## 实测踩过的坑

### 榜单文章不一定是本期的 ← 最危险

搜 `biggest funding rounds this week August 2026`，返回的 Crunchbase 周榜实际是
**7 月 21-23 那周**的：Atoms（$1.7B）、Augustus（$180M）、Crystalys（$130M）全在窗口外，
而搜索摘要把它们描述成 "early August"。

对策：榜单只提供候选清单，每笔日期在第二段单独确认。原始报道 URL 里的日期
（`techcrunch.com/2026/07/22/...`）是最可靠判据。确认不了宁可不写。

同类：知乎/微信的聚合文章大量复用旧闻当「本周热点」。实测被它们坑过三次——
SpaceX 收购 Cursor（实为 2026-06-16）、Claude Opus 4.7 发布（实为 2026-04-16）、
加州 AI 训练数据透明度法案（实为 2024 年签署的 AB 2013）。

### 长会话里的日期会漂

本技能曾在一个跨两周的会话里，按上下文早期的日期锚定窗口，
差点做出一份窗口错两周的周报。**每次执行先 `date -u`，不要从上下文推断今天是哪天。**

### 中国硬科技公司估值口径互相矛盾

实测 AI² Robotics（智平方）：一处称「约 7.35 亿美元融资，估值超 500 亿元」，
另一处称「超 10 亿元 B 轮，估值超 100 亿元」——差 5 倍。
原因通常是不同轮次混谈、币种换算错误、或累计与本轮混淆。

### 公司改名重组会制造假新闻

Atoms 并非新公司，是 Travis Kalanick 的 CloudKitchens（City Storage Systems）
2026 年 4 月更名重组而来，已隐身运营近 8 年。报道很容易读成「一家新公司融了 17 亿美元」。
留意「成立时间」与「融资规模」是否匹配。

### Notion 写入的两个坑

- 裸域名（如 `Smallest.ai`）会被自动识别成指向 `http://Smallest.ai` 的错误链接
  → 用反引号包成行内代码
- `~` 会被转义成 `\~` → 表示区间用 `→`

## 定时任务的限制

Routine 触发的会话**拿不到 MCP 连接器工具**（`connectors` 参数对部分组织未开放），
所以定时跑的简报写不进 Notion / Google Drive。可行的自动投递方式是
写文件 + `SendUserFile`，这条路不依赖任何连接器。

要让定时任务也进 Notion，需在 claude.ai 的 Routines 界面手动创建并勾选连接器。

## 源清单的取舍

被删掉没进 runbook 的：播客、长文随笔（Paul Graham、Wait But Why 等）、
国际综合新闻（BBC/Guardian/Al Jazeera/France 24）。理由是它们与「科技资讯简报」
的相关度低，而每多一个域名就多摊薄一次检索的命中密度。
需要时自己加回去，注意先确认不在黑名单里。
