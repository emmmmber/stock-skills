# 检索词模板库

按板块组织。`{窗口}` 处填时间提示词，`{年月}` 填形如 `2026年8月`。

**用法**：每个板块挑 1 条中文 + 1 条英文，配 `reference/sources.md` 对应的 `allowed_domains`，
所有 query 放在同一条消息里并行发出。

## 为什么要中英文各搜一遍

实测中英文搜索命中的是**两批完全不同的新闻**，不是同一批的翻译：

- 中文源对国内融资、国产模型发布、政策监管的覆盖远好于英文源
- 英文源对论文、基础设施、硅谷人事变动的覆盖远好于中文源
- 同一件事的中英文报道口径经常不同（尤其融资金额和估值）——这正好用来交叉验证

只搜一种语言会系统性丢掉一半。

## 时间提示词

WebSearch 对时间的理解很弱，但**在 query 里放时间词仍然有效**，能把结果往新的方向推：

| 时间窗 | 中文 | 英文 |
|---|---|---|
| 近 24-48h | `今天` `昨天` `最新` | `today` `this week` `latest` |
| 近 7 天 | `本周` `近期` `{年月}` | `this week` `past week` `{Month Year}` |
| 近 30 天 | `{年月}` `近一个月` | `{Month Year}` `this month` |

⚠️ 放了时间词也**不代表结果就是新的**。必须按 SKILL.md Step 3 逐条核对日期。

## 技术动态

**中文**
```
AI 大模型 发布 开源 {窗口}
国产大模型 进展 评测 {年月}
AI Agent 智能体 技术 突破 {窗口}
多模态 推理模型 发布 {年月}
```

**英文**
```
AI model release open source {窗口}
LLM benchmark results announced {窗口}
AI agent framework launch {年月}
frontier model capabilities paper {窗口}
```

**官方博客定向**（`allowed_domains` 只放 openai/anthropic/deepmind/ai.meta.com）
```
model announcement release
```
这条 query 故意写得很宽——因为限定了官方域名，返回的本来就都是发布公告，
不需要靠关键词筛。这是命中率最高的一条，别省。

## 融资 / 投资

> 融资板块覆盖**泛科技**，且要求六字段结构化输出。
> 完整工作流、领域分工、口径规范见 [`funding.md`](funding.md)——**做融资板块前必读那一份**。
> 这里只给 query 模板。

### 第一段 · 扫榜（捞交易清单）

**中文 · 栏目直搜**（效率最高，优先跑）
```
投中网 投融周报 {年月}
投资界 AI 周报 {年月}
```

**中文 · 综合**
```
融资 轮 亿元 科技公司 {窗口}
硬科技 融资 估值 {年月}
{领域} 融资 领投 {窗口}
```

**中文 · 分领域**（按本期需要挑 1-2 个）
```
AI 大模型 融资 亿元 {窗口}
半导体 芯片 融资 轮 {窗口}
机器人 具身智能 融资 估值 {窗口}
生物医药 创新药 融资 轮 {窗口}
新能源 储能 电池 融资 {窗口}
商业航天 卫星 融资 {窗口}
企业服务 SaaS 融资 {窗口}
```

**英文 · 综合**
```
startup raises funding round led by {窗口}
biggest funding rounds this week {年月}
tech startup valuation Series funding {窗口}
```

**英文 · 分领域**
```
biotech startup raises Series funding {窗口}
semiconductor chip startup funding round {窗口}
robotics investments funding {年月}
space defense startup raises {窗口}
climate energy startup funding round {窗口}
fintech startup raises Series {窗口}
```

### 第二段 · 逐笔深挖（补齐六字段）

**不加 `allowed_domains`**，开放搜索命中率高得多。每笔 🔴 交易做一条：

```
<公司名> 融资 估值 创始人 背景
<公司名> 成立 团队 产品 客户
<Company> funding valuation founder background
<Company> raises Series <X> led by investors
```

实测：一条「星动纪元 人形机器人 融资 估值 创始人 陈建宇 清华」同时拿到了
成立时间、产品迭代次数、交付量、客户结构、历轮投资方、最新估值、
以及创始人的本科/博士/任职履历——六字段一次填满。

**query 里带上已知的人名或机构名会显著提升命中率**（上例里的「陈建宇 清华」）。
第一段扫榜时如果看到创始人姓名，第二段务必带上。

### 单位与口径

- 中文源「亿元」默认人民币，「亿美元」才是美元；英文源 `billion` = 十亿。
  **保留原文币种，不要擅自换算**——汇率会变，换算过的数字日后无法回溯核对
- **累计融资 ≠ 本轮融资**。实测陷阱：「必博半导体完成 A+ 轮，累计融资超 9 亿元」
  ——9 亿是累计数，本轮金额未披露
- 实测摘要里出现过「DeepSeek 融资 500 亿元 / 估值 4000 亿」这类表述，
  数量级需回原文核对——**核对不了就照抄原文表述并标注来源，不要自己算**

## 社媒 / 社区热议

**中文**
```
AI 热议 争议 讨论 {窗口}
大模型 网友 吐槽 体验 {年月}
AI 产品 刷屏 出圈 {窗口}
```

**英文**
```
AI Hacker News discussion controversy {窗口}
AI product launch reaction developers {窗口}
```

**这个板块的正确期望值**：能拿到「大家在吵什么」，拿不到「吵得多凶」。
写的时候用定性表述（"知乎/V2EX 上有较集中的讨论"），
**不要给热搜排名、阅读量、点赞数、HN 分数**——本 skill 拿不到这些。

## GitHub Trending

不走 WebSearch，用 WebFetch：

```
https://github.com/trending?since=daily
https://github.com/trending?since=weekly
https://github.com/trending/python?since=daily
https://github.com/trending/typescript?since=weekly
```

拿到的是真实 star 增量，这是本 skill 少数能给出精确数字的地方。
注意 trending 榜上有大量教程仓库和陈年老项目（`build-your-own-x`、
`AI-For-Beginners` 这类常年在榜），**做 AI 简报时挑当天真正在涨的新项目**，
别把常驻榜单的教程仓当新闻。

## 追踪具体事件

用户问"XX 公司那事怎么回事"时，换成开放搜索（不限定域名），三段式：

```
1. <公司/产品名> <事件关键词>              → 摸清事件轮廓
2. <公司名> 回应 声明 官方                  → 找当事方表态
3. <公司名> <事件> 分析 影响               → 找评论和后续
```
