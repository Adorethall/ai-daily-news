---
name: ai-daily-news
description: 每日AI资讯推送，自动收集国内外科技媒体、学术前沿、大厂动态，整理成日报推送至飞书群
author: ArkClaw
version: 1.0.0
triggers:
  - "AI日报"
  - "ai日报"
  - "每日AI"
  - "AI资讯"
metadata: {"clawdbot":{"emoji":"📰","requires":{"bins":["python3","uv"]},"config":{"env":{"FEISHU_WEBHOOK_URL":{"description":"飞书群机器人Webhook URL","required":false},"DEFAULT_CHAT_ID":{"description":"默认推送群chat_id","required":false},"SEARCHENGINE_URL":{"description":"搜索引擎服务URL (SearXNG)","default":"http://localhost:8080","required":false}}}}}
---

# AI每日资讯日报 Skill

自动收集国内外AI领域资讯，整理成结构化日报推送到指定飞书群。

## 工作流程

```
配置信息源 → 爬取/搜索资讯 → AI筛选过滤去重 → 格式整理 → 推送至群聊
```

### 1. 信息源配置

支持以下资讯来源：

- **国内科技媒体**: 36氪、智东西、机器之心、量子位、虎嗅、钛媒体
- **海外科技媒体**: TechCrunch、The Verge、Wired、Bloomberg、MIT Technology Review
- **学术前沿**: arXiv 最新AI论文 (cs.CV, cs.LG, cs.CL)
- **大厂动态**: Anthropic、OpenAI、Google、Meta、Microsoft、ByteDance、Alibaba、智谱等

### 2. 安装依赖

```bash
uv sync
```

### 3. 使用方法

#### 生成今日AI日报（不推送）
```bash
uv run {baseDir}/ai_daily.py generate --date today
```

#### 生成并推送到默认群
```bash
uv run {baseDir}/ai_daily.py generate --date today --push
```

#### 推送到指定群
```bash
uv run {baseDir}/ai_daily.py push --chat-id oc_xxx --file output/daily-2026-04-23.md
```

#### 仅更新 arXiv 论文
```bash
uv run {baseDir}/ai_daily.py fetch arxiv --categories cs.CV cs.LG cs.CL --limit 10
```

#### 仅搜索大厂动态
```bash
uv run {baseDir}/ai_daily.py search --company Anthropic --days 7
```

## 配置说明

在环境变量中配置：

| 变量 | 说明 | 必填 |
|------|------|------|
| `FEISHU_WEBHOOK_URL` | 飞书机器人Webhook地址 | 否（使用OpenClaw原生消息推送时不需要） |
| `DEFAULT_CHAT_ID` | 默认推送的飞书群chat_id | 是 |
| `SEARCHENGINE_URL` | SearXNG 搜索引擎地址 | 否（使用默认值） |

## 日报格式

```
# 🤖 AI日报 - YYYY-MM-DD

**重点关注：{今日焦点}**

---

## 🔔 今日要闻

### 1. {标题}
{摘要，100-200字}

---

## 🏢 科技巨头动态

### {公司}
- {动态1}
- {动态2}

---

## 🔬 研究前沿

### {论文标题}
- 作者：{作者}
- 摘要：{简要摘要}
- 链接：{arXiv链接}

---

## 🛠 产品与工具

### {产品}
- {简介}

---

## 📊 行业观察

{简短行业观察总结}

---

*每天上午10点准时更新*
```

## 功能特点

- ✅ 多源信息聚合
- ✅ AI智能去重过滤
- ✅ 重点资讯优先排序
- ✅ 自动格式整理
- ✅ 支持定时推送
- ✅ 可配置重点关注公司
- ✅ arXiv 每日论文追踪

## 定时任务

建议使用 cron 定时执行：

```
# 每天上午10点执行
0 10 * * * cd /path/to/ai-daily-news && uv run ./ai_daily.py generate --date today --push >> logs/cron.log 2>&1
```

## 依赖说明

- Python 3.10+
- requests
- beautifulsoup4
- openai (用于AI筛选去重)
- arxiv (arXiv API)
