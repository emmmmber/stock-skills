# 信息源清单

所有域名的可达性都在 2026-08-03 用 WebSearch 实测过。**白名单直接抄进 `allowed_domains`，黑名单一个都不能出现。**

## ⛔ 黑名单（实测被拒，放进去会让整个调用 400 失败）

这些站点在 robots 层面屏蔽了 Anthropic 的 user agent。报错形如
`API Error: 400 The following domains are not accessible to our user agent: [...]`，
**是整个调用失败，不是跳过该域名降级返回**。

```
reuters.com      theverge.com     arstechnica.com    wired.com
reddit.com       ft.com           wsj.com            businessinsider.com
techinasia.com
```

> 遇到新的被拒域名，把它加到这张表里，并从下面的白名单删掉。
> 判断方法：报错信息会明确列出是哪几个域名，照着改即可。

⚠️ 注意 Reddit 和 The Verge 都在黑名单里——这两个是英文 AI 资讯的常见直觉选择，容易踩。
Reddit 上的讨论只能通过**不加 `allowed_domains` 的开放搜索**间接捞到（搜索引擎索引的转载/引用），
不能定向搜。

## ✅ 白名单

### 技术动态

**英文**
```json
["techcrunch.com", "venturebeat.com", "technologyreview.com", "semianalysis.com",
 "arxiv.org", "huggingface.co", "openai.com", "anthropic.com",
 "deepmind.google", "ai.meta.com", "theinformation.com"]
```
- `arxiv.org` / `huggingface.co` — 论文与模型发布，技术板块的硬通货
- `openai.com` / `anthropic.com` / `deepmind.google` / `ai.meta.com` — 官方博客，一手信源，优先级最高
- `semianalysis.com` — 芯片/算力深度分析，做算力话题时加上
- `theinformation.com` — 独家多，但多数内容付费墙，搜索摘要往往只有导语

**中文**
```json
["jiqizhixin.com", "qbitai.com", "36kr.com", "infoq.cn",
 "leiphone.com", "geekpark.net", "ithome.com", "huxiu.com"]
```
- `jiqizhixin.com`（机器之心）/ `qbitai.com`（量子位）— 中文 AI 技术报道质量最高的两家，优先
- `infoq.cn` — 偏工程实现
- `ithome.com` — 快讯多、噪音也多，只当补充

### 融资 / 投资

> 融资板块覆盖**泛科技**（不限 AI），且要求结构化输出六个字段。
> **完整的领域分工、两段式检索工作流、口径规范见 [`funding.md`](funding.md)。**
> 这里只列域名白名单。

**英文 · 综合**
```json
["techcrunch.com", "crunchbase.com", "axios.com", "cnbc.com", "venturebeat.com",
 "theinformation.com", "sifted.eu", "pitchbook.com", "fortune.com", "forbes.com",
 "eu-startups.com", "dealstreetasia.com", "kr-asia.com"]
```

**英文 · 垂直领域**
```json
["fiercebiotech.com", "endpts.com", "statnews.com", "therobotreport.com",
 "spacenews.com", "payloadspace.com", "breakingdefense.com", "semianalysis.com",
 "electrek.co", "insideevs.com", "canarymedia.com", "utilitydive.com",
 "finextra.com", "pymnts.com", "ieeespectrum.org", "cleantechnica.com"]
```

**英文 · 公司档案库**（第二段深挖用）
```json
["tracxn.com", "pitchbook.com", "cbinsights.com", "dealroom.co",
 "linkedin.com", "wellfound.com", "sec.gov"]
```

**中文 · 综合**
```json
["pedaily.cn", "chinaventure.com.cn", "itjuzi.com", "cyzone.cn", "iyiou.com",
 "36kr.com", "stcn.com", "cls.cn", "wallstreetcn.com", "caixin.com",
 "yicai.com", "tmtpost.com", "jiemian.com", "thepaper.cn", "21jingji.com",
 "xueqiu.com", "scmp.com"]
```

**中文 · 垂直领域**
```json
["zhidx.com", "eefocus.com", "vcbeat.net", "d1ev.com", "gasgoo.com", "leiphone.com"]
```

关键入口（实测效率最高的几个）：

- **`chinaventure.com.cn`（投中网）「投融周报」**——泛科技全领域，一篇覆盖一周交易。
  中文侧效率最高的单一入口，搜 `投中网 投融周报 <年月>` 直接命中
- **`pedaily.cn`（投资界）「AI 周报」**——AI 垂直，同上
- **`stcn.com`（证券时报）**——中文源里少数会在标题直接写出估值的（实测「估值超百亿元」）
- **`zhidx.com`（智东西/芯东西/车东西）**——半导体、机器人、智能汽车的融资快讯密度高
- **`vcbeat.net`（动脉网）**——生物医药/医疗器械融资，中文侧几乎是唯一的垂直源
- **`fiercebiotech.com` 的 Fundraising Tracker**——按年维护的滚动页，一页覆盖全年生物医药融资
- **`therobotreport.com`**——月度机器人投资汇总
- **`tracxn.com` / `pitchbook.com`**——搜索摘要里直接带创始人姓名、历轮总额、最新估值，
  是补齐「创始人背景」「估值」字段的捷径
- `itjuzi.com`（IT桔子）— 交易数据库，查具体公司的轮次历史
- `caixin.com`（财新）有付费墙，摘要往往只有导语

### 社媒 / 社区热议

**英文**
```json
["news.ycombinator.com", "x.com", "producthunt.com", "lobste.rs", "linkedin.com"]
```
- HN 能定向搜到，但**搜不到分数和评论数**（那要抓页面，本环境 WebFetch 对 HN 是 403）
- `x.com` 的搜索覆盖很差，命中率低，别指望它能反映真实推特热度

**中文**
```json
["zhihu.com", "v2ex.com", "weibo.com", "bilibili.com", "sspai.com", "xiaohongshu.com"]
```
- `zhihu.com` — 实测中文 AI 舆论最容易捞到的源，长文讨论质量尚可
- `v2ex.com` — 开发者视角，情绪真实
- `weibo.com` — **能搜到但拿不到热搜值**，只能定性描述"有讨论"，不能给排名和阅读量
- `xiaohongshu.com` / `bilibili.com` — 面向大众的 AI 产品讨论，做 to C 话题时加

## WebFetch 可用性

本环境实测：

| 目标 | 状态 |
|---|---|
| `github.com/trending`（含 `?since=` / `/<语言>`） | ✅ 可用，能拿到真实 star 增量 |
| `raw.githubusercontent.com/...` | ✅ 可用，读开源项目 README/SKILL.md 用 |
| `github.com/<owner>/<repo>` | ✅ 可用 |
| 36kr / tmtpost / news.ycombinator / arxiv / anthropic.com / huggingface | ❌ 403 |

**结论：正文信息从 WebSearch 返回的摘要里取，不要指望 WebFetch 补全正文。**
只有 GitHub 系链接值得 WebFetch。

## 开放搜索（不加 allowed_domains）

不是所有检索都要限定域名。以下情况用开放搜索更好：

- 追一件**具体事件**的全貌（限定域名会漏掉最早爆料的那家）
- 想捞到黑名单站点的内容（通过其他站的转载/引用间接获得）
- 中文长尾话题，限定域名后结果太稀疏

代价是会混进 SEO 农场和洗稿站，按 SKILL.md Step 3 的过滤规则清理。
