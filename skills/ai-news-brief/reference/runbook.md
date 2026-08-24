# 运行手册

**常规执行只需要这一份。** 设计理由、实测记录、踩坑复盘在 `notes.md`，别在跑简报时读它。

## 域名

### ⛔ 黑名单（放进 `allowed_domains` 会让整个调用 400 失败）

```
reuters  theverge  arstechnica  wired  reddit  ft  wsj
businessinsider  techinasia
```

新遇到被拒域名：报错会点名，加到这里并从下面删掉。

### 技术

```json
["techcrunch.com","venturebeat.com","technologyreview.com","semianalysis.com",
 "arxiv.org","huggingface.co","openai.com","anthropic.com","deepmind.google","ai.meta.com"]
```
```json
["jiqizhixin.com","qbitai.com","36kr.com","infoq.cn","leiphone.com","geekpark.net","ithome.com"]
```

官方博客定向（只放 openai/anthropic/deepmind/ai.meta.com）配宽 query 如
`model announcement release {年月}`，命中率最高。

### 融资（泛科技）

综合 · 英
```json
["crunchbase.com","techcrunch.com","axios.com","cnbc.com","fortune.com","forbes.com",
 "sifted.eu","eu-startups.com","dealstreetasia.com","kr-asia.com","theinformation.com"]
```
综合 · 中
```json
["pedaily.cn","chinaventure.com.cn","itjuzi.com","cyzone.cn","iyiou.com","36kr.com",
 "stcn.com","cls.cn","wallstreetcn.com","caixin.com","yicai.com","tmtpost.com",
 "jiemian.com","thepaper.cn","21jingji.com"]
```
垂直 · 英
```json
["fiercebiotech.com","endpts.com","statnews.com","therobotreport.com","spacenews.com",
 "payloadspace.com","breakingdefense.com","electrek.co","insideevs.com","canarymedia.com",
 "utilitydive.com","finextra.com","pymnts.com"]
```
垂直 · 中
```json
["zhidx.com","eefocus.com","vcbeat.net","d1ev.com","gasgoo.com"]
```
档案库（深挖用）
```json
["tracxn.com","pitchbook.com","cbinsights.com","dealroom.co","linkedin.com","sec.gov"]
```

**高效入口**：`投中网 投融周报 {年月}`（泛科技全领域，一篇覆盖一周）、
`投资界 AI 周报 {年月}`、Fierce Biotech Fundraising Tracker（年度滚动页）、
The Robot Report 月度投资汇总。`stcn.com` 标题常直接带估值；
`tracxn.com`/`pitchbook.com` 摘要直接带创始人姓名与估值。

### 社媒

```json
["news.ycombinator.com","x.com","producthunt.com","lobste.rs"]
```
```json
["zhihu.com","v2ex.com","weibo.com","bilibili.com","sspai.com"]
```

拿得到「在吵什么」，拿不到「吵得多凶」——HN 分数、微博热搜值均不可得，只做定性描述。

### WebFetch 可用性

`github.com/trending`、`github.com/<owner>/<repo>`、`raw.githubusercontent.com` ✅
其余（36kr / HN / arxiv / anthropic.com / huggingface / ima.qq.com）❌ 403。

## 检索词

`{窗口}` 填 `今天`/`本周`/`{年月}`，`{年月}` 形如 `2026年8月`。
**中英文命中的是两批不同的新闻，不是互为翻译，只搜一种会丢一半。**

技术
```
AI 大模型 发布 开源 进展 {窗口}          model release announcement {年月}
国产大模型 评测 进展 {年月}               LLM benchmark results announced {窗口}
```

融资 · 扫榜
```
投中网 投融周报 {年月}                    biggest funding rounds this week {年月}
融资 轮 亿元 科技公司 {窗口}              startup raises funding round led by {窗口}
{领域} 融资 估值 {窗口}                   {sector} startup raises Series funding {窗口}
```
领域可选：AI 大模型 / 半导体 芯片 / 机器人 具身智能 / 生物医药 / 新能源 储能 /
商业航天 卫星 / 金融科技 / 企业服务

融资 · 深挖（**不加** `allowed_domains`）
```
<公司名> 融资 估值 创始人 背景
<Company> funding valuation founder background
```

社媒
```
AI 热议 争议 讨论 {窗口}                  AI Hacker News discussion {窗口}
```

⚠️ 搜索引擎对时间理解很弱，query 里放时间词只是往新的方向推，**不保证结果是新的**。每条都要核日期。

## 融资六字段

| 字段 | 填不出时写 |
|---|---|
| 名称 | 必填，填不出不该进正文 |
| 融资事件 | 轮次+金额+币种+日期，必填 |
| 融资方 | 领投/跟投分开；「未披露」 |
| 估值 | 标明投前/投后；「未披露估值」 |
| 公司简介 | 成立时间+主营+可量化进展；「公开信息有限」 |
| 创始人背景 | 姓名+教育+关键履历；「创始人背景未检索到」 |

**缺哪个明写缺哪个**，不留空，不用「据悉规模可观」糊弄。

口径：
- 中文「亿元」默认人民币，「亿美元」才是美元；英文 `billion` = 十亿。**保留原文币种，不换算**
- **累计融资 ≠ 本轮融资**（如「A+ 轮，累计超 9 亿元」——9 亿是累计数）
- 战略投资 / 算力协议 / 合作 ≠ 股权融资轮，口径冲突就并列标注
- 中国硬科技公司的估值常互相矛盾，至少两个独立源交叉印证，印证不上就把分歧摆出来

## 输出骨架

```markdown
# 科技资讯{日|周}报 · YYYY-MM-DD

> 覆盖窗口：YYYY-MM-DD → YYYY-MM-DD ｜ 板块：…

## 📌 本期要点
[3-5 句，给只看 30 秒的人。要能独立成篇，不要写成目录]

## 🔬 技术动态
- 🔴 **[结论式标题，数字进标题]** `YYYY-MM-DD`
	[2-4 句展开]
	来源：[媒体](url) · [媒体](url)

### GitHub Trending
| 项目 | 语言 | 新增 ★ | 说明 |
> 剔除常驻教程仓与非 AI 项目并说明

## 💰 融资 / 投资
[一句话点出本期资金流向特征]

### 本期交易一览   ← 多于 5 笔才放
| 公司 | 领域 | 轮次 | 金额 | 估值 | 领投方 | 日期 |

### 重点交易   ← 🔴 全展开，🟡 挑 2-3 笔，⚪ 只进一览表
- 🔴 **公司** — 轮次 金额，投后估值 X `YYYY-MM-DD`
	**融资方**：… **公司**：… **创始人**：… **来源**：…

## 💬 社媒 / 社区热议
- [定性描述，不给热度数字]

## 🔍 本期检索说明
- 时间窗 / 检索量
- **已剔除**（属实但不在窗口）：条目 + 实际日期
- **未能证实**：单源未交叉印证的
- **能力边界**：拿不到什么
```

分级：🔴 改变格局（前沿模型发布、10 亿美元级融资、重大监管）｜🟡 有实质增量｜⚪ 知道即可。
**一份日报 🔴 通常 0-2 条，标了 5 条说明分级失效。**

条目写法：标题是结论不是话题；数字进标题；日期用 `YYYY-MM-DD`，确认不了写「日期未确认」；
来源 2-3 个封顶；不写「值得持续关注」这类废话结尾。

空板块照实写空，不要用旧闻凑数。

## 投递

**文件**：写到 `/mnt/user-data/outputs/<YYYY-MM-DD> 科技资讯{日|周}报.md`，
再 `SendUserFile`（定时任务用 `status: proactive`、`display: attach`）。

**Notion**：`data_source_id` = `8a300b49-4e38-4fe5-9e0d-1847b317fc79`。
属性：`标题`、`date:日期:start`、`覆盖窗口`（用 `→` 不用 `~`，后者会被转义）、
`板块`（只填有内容的）、`要点数`、`icon` 📡。
正文用 Notion-flavored Markdown：**表格必须是 `<table><tr><td>` XML**，管道表格会散架；
转义 `\ * ~ \` $ [ ] < > { } | ^`；引用块不能跨行（多行用 `<br>`）；
裸域名（如 Smallest.ai）会被识别成错误链接，用反引号包成行内代码。
以上六条够用了，**不要再去读 `notion://docs/enhanced-markdown-spec`**（约 5k token）。

**IMA**：`scripts/push-to-ima.py`，先 `--probe`。注意该脚本未经真实 API 联调。
