# stock-skills

资讯与投研相关的 Claude Code 技能集。

| 技能 | 说明 | 依赖 |
|---|---|---|
| [`ai-news-brief`](skills/ai-news-brief/SKILL.md) | 科技资讯简报：汇总中国与全球的 AI 技术新闻、**泛科技融资动态**、社媒热议，输出带来源链接的中文简报（日报/周报/专题） | 无（纯 WebSearch/WebFetch） |

融资板块覆盖 AI、半导体、机器人、生物医药、新能源、商业航天、金融科技等全领域，
每笔重点交易结构化输出六个字段：**名称 / 融资事件 / 融资方 / 估值 / 公司简介 / 创始人背景**。

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
├── SKILL.md                      工作流 + 红线                    ≈2.1k tok
├── reference/
│   ├── runbook.md                运行手册：域名、检索词、六字段、  ≈3.7k tok
│   │                             输出骨架、投递 —— 常规执行只读这份
│   └── notes.md                  设计理由、环境校准、踩坑复盘 ——   ≈3.4k tok
│                                 跑简报时不读，只在重新校准时读
└── scripts/
    └── push-to-ima.py            投递到腾讯 IMA 知识库（零依赖，标准库）
```

**运行时只载入 SKILL.md + runbook.md（约 5.8k token）。** 早期版本把四个参考文件
都标成「必读」，每次载入 18.4k token，其中大部分是设计理由而非执行所需——
渐进式披露失效是这类技能最大的隐性成本。改工作流时先问：这段文字是执行时必须的，
还是解释为什么的？后者进 `notes.md`。

### 投递到腾讯 IMA 知识库

```bash
export IMA_CLIENT_ID=...   # https://ima.qq.com/agent-interface 申请
export IMA_API_KEY=...

python skills/ai-news-brief/scripts/push-to-ima.py --probe          # 先探测
python skills/ai-news-brief/scripts/push-to-ima.py 周报.md --folder 知识总结
```

走 `notes/import_doc` 建笔记 → `wiki/add_knowledge`（`media_type=11`）挂进知识库文件夹的
纯 JSON 路径，绕开 `create_media` + COS 二进制上传（需要 COS 签名和临时密钥，依赖更重）。
凭据只从环境变量读，不接受命令行传参。目标文件夹需事先在 IMA 里建好。

> ⚠️ **该脚本未经真实 API 验证**。编写环境的网络策略屏蔽了 `ima.qq.com`，无法联调；
> API 契约来自官方 `ima-skills` 接入包的公开文档。已验证的部分：语法、CLI、凭据缺失保护、
> 错误路径、`--dry-run` 的请求体构造。未验证的部分：响应信封结构、列表接口的字段名、
> 以及 `add_knowledge` 挂载笔记时 `media_id` 取 `doc_id` 这一推断。
> **首次使用务必先 `--probe`**，它会打印接口实际返回的字段名，对不上就照着改。

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
