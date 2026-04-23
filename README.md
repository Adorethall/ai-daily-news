# AI每日资讯日报

自动收集国内外AI领域资讯，整理成结构化日报推送到飞书群。

## 功能特点

- ✅ 多源信息聚合（RSS、arXiv、搜索引擎）
- ✅ AI智能去重过滤
- ✅ 重点资讯优先排序
- ✅ 自动分类整理
- ✅ Markdown格式输出
- ✅ 飞书群推送支持

## 资讯来源

- **国内科技媒体**: 36氪、机器之心、智东西、量子位
- **学术前沿**: arXiv 最新AI论文 (cs.CV, cs.LG, cs.CL, cs.AI)
- **大厂动态**: 自动搜索 Anthropic、OpenAI、Google、Meta、Microsoft、字节跳动、阿里、智谱等公司近期新闻

## 安装

```bash
cd /path/to/ai-daily-news
uv sync
```

## 配置

设置环境变量：

```bash
# 可选：飞书Webhook（不设置则使用OpenClaw原生推送）
export FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/xxx"

# 必填：默认推送群chat_id
export DEFAULT_CHAT_ID="oc_xxx"

# 可选：SearXNG搜索引擎地址
export SEARCHENGINE_URL="http://localhost:8080"
```

## 使用方法

### 生成今日AI日报（不推送）
```bash
uv run python ai_daily.py generate --date today
```

### 生成并推送到默认群
```bash
uv run python ai_daily.py generate --date today --push
```

### 推送到指定群
```bash
uv run python ai_daily.py push --chat-id oc_xxx --file output/daily-2026-04-23.md
```

### 仅抓取arXiv论文
```bash
uv run python ai_daily.py fetch arxiv --limit 10
```

### 搜索特定公司新闻
```bash
uv run python ai_daily.py search --company Anthropic --days 7
```

## 定时推送

使用cron定时执行，每天上午10点推送：

```crontab
0 10 * * * cd /root/.openclaw/workspace/skills/ai-daily-news && uv run python ai_daily.py generate --date today --push >> logs/cron.log 2>&1
```

创建日志目录：
```bash
mkdir -p logs
```

## 输出格式

日报采用Markdown格式，包含以下板块：

- 🤖 标题和日期
- 重点关注（随机选一个大厂动态作为今日焦点）
- 🔔 今日要闻 - 重要新闻
- 🏢 科技巨头动态 - 按公司分组
- 🔬 研究前沿 - arXiv论文
- 🛠 产品与工具 - 新产品发布
- 📊 行业观察 - 行业动态

## 日报示例

```
# 🤖 AI日报 - 2026-04-23

**重点关注：Anthropic**

---

## 🔔 今日要闻

### 1. Anthropic发布Claude 3.5 Opus，支持2M上下文
- 来源: TechCrunch
- 摘要: Anthropic今天发布了最新的Claude 3.5 Opus模型，将上下文窗口提升到了200万tokens...
- 链接: https://...

...
```

## 扩展开发

### 添加新的RSS源

修改 `ai_daily.py` 中的 `Config.sources.domestic_media`:

```python
"domestic_media": [
    {"name": "36氪", "url": "https://36kr.com/feed"},
    {"name": "你的新源", "url": "https://example.com/feed"},
]
```

### 添加更多重点关注公司

修改 `Config.focus_companies`:

```python
self.focus_companies = [
    "Anthropic", "OpenAI", "Google", "Meta", 
    "Microsoft", "ByteDance", "Alibaba", "Zhipu",
    "你的新公司",
]
```

## 许可证

MIT
