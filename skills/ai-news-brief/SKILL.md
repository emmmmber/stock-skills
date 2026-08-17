---
name: ai-news-brief
description: |
  科技资讯简报技能：汇总中国与全球的 AI 技术新闻、**泛科技融资/投资动态**、社媒与社区热议，
  输出带来源链接、可核对的中文简报（日报/周报/专题）。
  融资板块覆盖 AI、半导体、机器人、生物医药、新能源、商业航天、金融科技等全领域，
  每笔重点交易给出六个字段：名称、融资事件、融资方、估值、公司简介、创始人背景。
  完全基于 WebSearch + WebFetch 实现，不需要爬虫脚本、不需要 API key、不需要本地网络直连，
  因此在 Claude Code 云端/沙箱环境（出站被网络策略拦截）中同样可用。
  当用户要求"AI 日报""AI 周报""今天的 AI 新闻""最近 AI 圈发生了什么""AI 融资动态"
  "大模型融资""AI 资讯""AI 简报""AI 热点""看看 AI 社媒在聊什么""GitHub trending"
  "融资周报""投融资动态""这周谁拿了钱""硬科技融资""半导体/机器人/生物医药融资"
  或要求汇总某段时间的科技技术/融资/舆论动态时，使用此skill。
metadata:
  type: workflow
  source: |
    原创工作流。设计前对本环境做过实测校准（2026-08-03）：
    - WebSearch 对中英文源均可用，返回的摘要正文足以支撑简报写作
    - WebFetch 在本环境仅对 github.com / raw.githubusercontent.com 稳定可用，
      其余站点（36kr / tmtpost / news.ycombinator / arxiv / anthropic.com 等）普遍返回 403
    - allowed_domains 中若含被拒域名，整个调用直接 400 失败（详见 reference/sources.md）
    参考过 cclank/news-aggregator-skill (MIT) 的源分类思路与简报模板结构，
    未复用其任何代码——该项目依赖 Python 直连抓取，在受限网络环境下全部返回空。
---

# ai-news-brief

用 WebSearch 做扇出检索、用模板做结构化归纳，产出**中国 + 全球**的 AI 资讯简报。

和爬虫型新闻 skill 的区别：不抓站、不解析 HTML、不依赖出站网络策略放行，因此在 Claude Code 云端环境里能跑通。代价是拿不到微博热搜值、HN 分数这类精确热度数字——**这类数字一律不要编，见"红线"一节**。

## 模块速览

| 参考文档 | 内容 | 何时读 |
|---|---|---|
| [`reference/sources.md`](reference/sources.md) | 已实测的域名白名单（中/英 × 技术/融资/社媒）、**必须避开的黑名单**、WebFetch 可用性说明 | 每次执行前必读，`allowed_domains` 直接从这里抄 |
| [`reference/queries.md`](reference/queries.md) | 中英双语搜索词模板库，按板块和时间窗组织 | 组织检索时读 |
| [`reference/funding.md`](reference/funding.md) | **融资板块作业手册**：两段式检索、泛科技领域分工、六字段记录规范、金额口径 | **每次做融资板块前必读** |
| [`reference/report-template.md`](reference/report-template.md) | 简报输出模板、条目写法、重要性分级、日期标注规范 | 写报告时读 |
| [`scripts/push-to-ima.py`](scripts/push-to-ima.py) | 把生成好的简报投递到腾讯 IMA 知识库指定文件夹 | 用户要求推送到 IMA 时 |

## 工作流

### Step 0 · 确定范围

从用户话里解析三件事，缺省值如下：

| 参数 | 缺省 | 说明 |
|---|---|---|
| 时间窗 | 近 7 天 | "今天/日报" → 近 24-48 小时；"周报" → 近 7 天；"最近" → 近 7 天 |
| 板块 | 全部 | 技术 / 融资 / 社媒（政策按需） |
| 地域 | 中国 + 全球 | 用户明确说"国内"或"硅谷"时才收窄 |
| 融资范围 | **泛科技** | 半导体、机器人、生物医药、新能源、航天、金融科技等，不限 AI |

**先说一句你要查什么，再开查**，别默默跑一大堆搜索。

### Step 1 · 扇出检索（并行）

从 `reference/queries.md` 取查询词，**把所有独立的 WebSearch 放在同一个消息里并行发出**——这是本 skill 的主要耗时来源，串行会慢 5-10 倍。

一次标准的日报/周报大约 8-11 条 query：

```
技术·中文  技术·英文
融资·扫榜·中文  融资·扫榜·英文  融资·分领域（1-2 条）
社媒·中文  社媒·英文
```

外加 GitHub Trending（见 Step 2）。每条 query 都带上 `allowed_domains`，值从 `reference/sources.md` 抄。

⚠️ **融资板块还有第二段检索**：扫榜拿到交易清单后，要对每笔重点交易做定向深挖，
补齐估值、公司简介、创始人背景。这一段在 Step 1 之后、Step 3 之前做，
日报 3-5 条 query，周报 5-8 条。**详见 [`reference/funding.md`](reference/funding.md)，
不读那份就做不出六字段。**

**两条硬约束：**

1. `allowed_domains` 里出现任何一个黑名单域名，**整个调用直接 400 失败**，不是降级返回。抄的时候逐个核对。
2. WebSearch 对时间的理解很弱。搜"本周融资"照样会返回两年前的文章（实测：搜 2026 年的融资，返回了 Llama 3.1 发布这种老新闻）。**每条素材都要回到标题/摘要里确认时间**，确认不了的按 Step 3 处理。

### Step 2 · GitHub Trending（可选但推荐）

技术板块想要"今天大家在写什么代码"时，用 WebFetch 打：

```
https://github.com/trending?since=daily        # 或 since=weekly
https://github.com/trending/python?since=daily # 按语言收窄
```

这是本环境里**唯一稳定可用的 WebFetch 目标**，能拿到真实的 star 增量。别对其他站点用 WebFetch，基本都是 403。

### Step 3 · 归并与分级

1. **去重**：同一件事被多家报道 → 合成一条，保留 2-3 个最权威来源的链接
2. **过滤**：剔除营销软文、"XX 大会即将召开"这类无信息量条目、纯 SEO 站的洗稿
3. **定日期**：给每条标注日期。搜索结果里确认不到确切日期的，标 `（日期未确认）`，**不要猜、不要写"近日"糊弄过去**
4. **分级**：按 `reference/report-template.md` 的三档（🔴 重大 / 🟡 值得关注 / ⚪ 简讯）打标

### Step 4 · 出报告

套 `reference/report-template.md`。默认输出 Markdown 到对话里；用户要文件就写到 `reports/YYYY-MM-DD-ai-brief.md`。

报告末尾必须有「本期检索说明」，写清楚：查了哪些板块、时间窗、哪些板块素材偏少或没查到。**空板块要明说空，不要用凑数条目填满**。

### Step 5 · 投递（可选）

用户要求存盘或推送到知识库时才做，默认不做。

**存本地**：直接写文件。Windows 用户常用 `D:\AI周报\<年份>\`，先确认目录存在再写。

**推送到腾讯 IMA 知识库**：用 `scripts/push-to-ima.py`。

```bash
# 凭据从环境变量读，不要写进命令行或提交到仓库
export IMA_CLIENT_ID=...   # Windows: set IMA_CLIENT_ID=...
export IMA_API_KEY=...     # 申请地址 https://ima.qq.com/agent-interface

# 首次使用：先探测，确认知识库和目标文件夹能被正确识别
python scripts/push-to-ima.py --probe

# 正式投递
python scripts/push-to-ima.py 2026-08-03-ai-weekly.md --kb 我的知识库 --folder 知识总结
```

走的是 `notes/import_doc` 建笔记 → `wiki/add_knowledge`（`media_type=11`）挂进知识库文件夹
的纯 JSON 路径，零第三方依赖。目标文件夹**必须已经在 IMA 里建好**，脚本不会自动创建。

**首次跑一定先 `--probe`**：IMA OpenAPI 的响应信封和列表字段名官方文档没有完整说明，
脚本对常见结构做了容错，但如果接口结构和预期不符，`--probe` 会把实际返回的字段名打出来，
比直接投递失败好排查。

## 红线

这是资讯类技能最容易翻车的地方，逐条遵守：

- **不编造数字**。融资金额、估值、star 数、热搜排名——搜索结果里没有的就写"未披露"。微博热搜值、HN 分数这类本 skill 拿不到的精确热度，**不要给一个看起来合理的数**。
- **不编造日期**。见 Step 3 第 3 点。
- **不编造链接**。每条的来源链接必须来自 WebSearch 实际返回的 URL，不要根据标题拼 URL。
- **来源冲突就并列**。比如 A 家说融资 20 亿美元、B 家说 25 亿美元，两个都写上并标注来源，不要取平均也不要只挑一个。
- **传闻标为传闻**。中文科技媒体大量使用"据知情人士""接近交易的人士"，转述时保留这个限定词。
- **区分"发布"和"预告"**。"某公司将于下月发布"不是技术新闻，放简讯或直接砍掉。

## 调研说明

本环境（Claude Code 云端沙箱）的网络策略只放行包管理器和 git 协议，普通 HTTPS 出站一律 403。因此所有依赖 `requests`/`playwright` 直连抓取的新闻 skill（如 cclank/news-aggregator-skill）在此环境下 45 个源全部返回空数组。本 skill 改走 WebSearch/WebFetch 通道绕开该限制。

如果你在**本地机器**上使用 Claude Code，网络无限制，那么爬虫型 skill 能拿到本 skill 拿不到的精确热度数据（微博热搜值、HN 分数、Product Hunt 票数），两者可以并存互补。
