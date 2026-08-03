# 信息源清单

所有域名的可达性都在 2026-08-03 用 WebSearch 实测过。**白名单直接抄进 `allowed_domains`，黑名单一个都不能出现。**

## ⛔ 黑名单（实测被拒，放进去会让整个调用 400 失败）

这些站点在 robots 层面屏蔽了 Anthropic 的 user agent。报错形如
`API Error: 400 The following domains are not accessible to our user agent: [...]`，
**是整个调用失败，不是跳过该域名降级返回**。

```
reuters.com      theverge.com     arstechnica.com
wired.com        reddit.com       ft.com            wsj.com
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

**英文**
```json
["techcrunch.com", "crunchbase.com", "axios.com", "cnbc.com",
 "venturebeat.com", "theinformation.com", "sifted.eu", "pitchbook.com"]
```
- `sifted.eu` — 欧洲创业公司，补美国视角的盲区

**中文**
```json
["pedaily.cn", "itjuzi.com", "36kr.com", "cls.cn",
 "wallstreetcn.com", "caixin.com", "yicai.com", "tmtpost.com", "scmp.com"]
```
- **`pedaily.cn`（投资界）是中文 AI 融资的首选源**——实测它有固定的「投资界 AI 周报」栏目，
  一篇就能覆盖一周主要交易，效率远高于逐条搜
- `itjuzi.com`（IT桔子）— 交易数据库，适合查具体公司的轮次历史
- `cls.cn`（财联社）/ `wallstreetcn.com`（华尔街见闻）— 快讯，上市公司相关消息快
- `caixin.com`（财新）/ `yicai.com`（第一财经）— 深度，但财新有付费墙
- `scmp.com`（南华早报）— 中国科技的英文报道，做中英对照时有用

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
