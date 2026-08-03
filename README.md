# stock-skills

资讯与投研相关的 Claude Code 技能集。

| 技能 | 说明 | 依赖 |
|---|---|---|
| [`ai-news-brief`](skills/ai-news-brief/SKILL.md) | AI 资讯简报：汇总中国与全球的 AI 技术新闻、融资动态、社媒热议，输出带来源链接的中文简报（日报/周报/专题） | 无（纯 WebSearch/WebFetch） |

## ai-news-brief

### 为什么不用现成的爬虫型新闻 skill

社区里成熟的方案（如 [cclank/news-aggregator-skill](https://github.com/cclank/news-aggregator-skill)，MIT）用 Python 直连抓取 44+ 个站点，本地机器上能拿到微博热搜值、HN 分数、Product Hunt 票数这类精确热度数据，非常好用。

但在 **Claude Code 云端环境**里跑不通：沙箱的网络策略只放行包管理器和 git 协议，普通 HTTPS 出站一律 403。实测该 skill 的 45 个源全部返回空数组：

```
36kr.com:443              → gateway 403 (policy denial)
weibo.com:443             → gateway 403
news.ycombinator.com:443  → gateway 403
api-one.wallstcn.com:443  → gateway 403
github.com/trending       → 403
export.arxiv.org          → 连接超时
```

本 skill 改走 WebSearch/WebFetch 通道绕开该限制，不需要爬虫脚本、API key 或本地网络直连。
代价是拿不到精确热度数字——**这类数字一律不编，见 SKILL.md 的红线一节。**

两者可以并存互补：本地用爬虫版拿精确数据，云端用这个。

### 结构

```
skills/ai-news-brief/
├── SKILL.md                      四步工作流 + 六条红线
└── reference/
    ├── sources.md                实测校准的域名白名单/黑名单、WebFetch 可用性
    ├── queries.md                中英双语检索词库
    └── report-template.md        简报模板、三档重要性分级、空板块写法
```

### 环境校准结论（2026-08-03 实测）

设计基于以下实测结果，换环境后建议重新校准 `reference/sources.md`：

- **WebFetch 在云端环境基本只对 GitHub 放行**。36kr / HN / arxiv / anthropic.com / huggingface 均 403。
  因此正文信息从 WebSearch 返回的摘要里取，不靠 WebFetch 补全；GitHub Trending 是唯一稳定可用的抓取目标。
- **`allowed_domains` 里混入被屏蔽的域名会让整个调用 400 失败**，不是跳过降级。
  已知黑名单：`reuters` `theverge` `arstechnica` `wired` `reddit` `ft` `wsj`。
  其中 Reddit 和 The Verge 是英文 AI 资讯的直觉选择，最容易踩。
- **中英文搜索命中的是两批不同的新闻**，不是互为翻译。中文源在国内融资、国产模型、政策监管上
  覆盖远好；英文源在论文、基础设施、硅谷人事上远好。只搜一种语言会系统性丢一半。
- **`pedaily.cn`（投资界）有固定的「AI 周报」栏目**，一篇覆盖整周交易，比逐条搜效率高得多。

### 用法

```
帮我出一份 AI 周报
最近 AI 圈的融资动态
今天有什么 AI 新闻
GitHub 上今天什么 AI 项目在涨
```

## 安装

```bash
# 本地测试
claude --plugin-dir /path/to/stock-skills

# 或作为插件安装
/plugin install <此仓库地址>
```

本技能集无脚本依赖，clone 下来即可用。
