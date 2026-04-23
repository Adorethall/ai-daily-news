#!/usr/bin/env python3
"""
AI每日资讯日报
- 从多源收集AI资讯
- AI筛选去重
- 整理成Markdown格式
- 推送到飞书群
"""

import os
import sys
import argparse
import json
import datetime
import re
import requests
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import arxiv
import feedparser
from bs4 import BeautifulSoup

# 配置基础目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@dataclass
class NewsItem:
    """新闻条目"""
    title: str
    source: str
    url: str
    summary: str
    publish_date: str
    category: str
    company: str = ""
    score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "source": self.source,
            "url": self.url,
            "summary": self.summary,
            "publish_date": self.publish_date,
            "category": self.category,
            "company": self.company,
            "score": self.score
        }

class Config:
    """配置管理"""
    def __init__(self):
        self.searxng_url = os.environ.get("SEARCHENGINE_URL", "http://localhost:8080")
        self.default_chat_id = os.environ.get("DEFAULT_CHAT_ID", "")
        self.feishu_webhook = os.environ.get("FEISHU_WEBHOOK_URL", "")
        
        # 重点关注公司
        self.focus_companies = [
            "Anthropic", "OpenAI", "Google", "Meta", 
            "Microsoft", "ByteDance", "Alibaba", "Zhipu"
        ]
        
        # 信息源配置
        self.sources = {
            "domestic_media": [
                {"name": "36氪", "url": "https://36kr.com/feed"},
                {"name": "机器之心", "url": "https://www.jiqizhixin.com/rss"},
                {"name": "智东西", "url": "https://zhidx.com/feed"},
                {"name": "量子位", "url": "https://www.qbitai.com/feed"},
            ],
            "arxiv_categories": ["cs.CV", "cs.LG", "cs.CL", "cs.AI"],
        }
        
        # 日报配置
        self.max_items = 20
        self.daily_focus_count = 1
        self.output_dir = os.path.join(BASE_DIR, "output")
        
        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)

class NewsFetcher:
    """新闻抓取器"""
    def __init__(self, config: Config):
        self.config = config
    
    def search_web(self, query: str, category: str = "news") -> List[Dict[str, Any]]:
        """使用SearXNG搜索"""
        try:
            params = {
                "q": query,
                "format": "json",
                "category": category,
                "language": "all",
            }
            url = f"{self.config.searxng_url}/search"
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json().get("results", [])
        except Exception as e:
            print(f"[WARN] Search failed: {e}")
        return []
    
    def fetch_rss(self, feed_url: str) -> List[Dict[str, Any]]:
        """抓取RSS"""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(feed_url, headers=headers, timeout=10)
            feed = feedparser.parse(response.content)
            items = []
            for entry in feed.entries[:20]:
                items.append({
                    "title": entry.title,
                    "link": entry.link,
                    "summary": entry.get("summary", ""),
                    "published": entry.get("published", ""),
                })
            return items
        except Exception as e:
            print(f"[WARN] RSS fetch failed {feed_url}: {e}")
        return []
    
    def fetch_arxiv(self, limit: int = 10) -> List[NewsItem]:
        """抓取arXiv最新AI论文"""
        items = []
        for category in self.config.sources["arxiv_categories"]:
            try:
                search = arxiv.Search(
                    query=f"cat:{category}",
                    max_results=limit // len(self.config.sources["arxiv_categories"]) + 2,
                    sort_by=arxiv.SortCriterion.SubmittedDate
                )
                for result in search.results():
                    published = result.published.strftime("%Y-%m-%d")
                    summary = result.summary[:200] + "..." if len(result.summary) > 200 else result.summary
                    item = NewsItem(
                        title=result.title,
                        source="arXiv",
                        url=result.entry_id,
                        summary=summary,
                        publish_date=published,
                        category="research",
                        score=0.8
                    )
                    items.append(item)
            except Exception as e:
                print(f"[WARN] arXiv fetch failed {category}: {e}")
        return items
    
    def search_company_news(self, company: str, days: int = 1) -> List[NewsItem]:
        """搜索公司近期新闻"""
        query = f"{company} AI news last {days} days"
        results = self.search_web(query, "news")
        items = []
        for result in results:
            item = NewsItem(
                title=result.get("title", ""),
                source=result.get("engine", "web"),
                url=result.get("url", ""),
                summary=result.get("content", "")[:200],
                publish_date=result.get("publishedDate", ""),
                category="company",
                company=company,
                score=0.7
            )
            items.append(item)
        return items
    
    def fetch_all_domestic_media(self) -> List[NewsItem]:
        """抓取所有国内媒体RSS"""
        items = []
        for source in self.config.sources["domestic_media"]:
            rss_items = self.fetch_rss(source["url"])
            for item in rss_items:
                # 过滤AI相关内容
                title = item["title"].lower()
                summary = item.get("summary", "").lower()
                if any(keyword in title or keyword in summary 
                      for keyword in ["ai", "人工智能", "大模型", "llm", "gpt", "claude"]):
                    items.append(NewsItem(
                        title=item["title"],
                        source=source["name"],
                        url=item["link"],
                        summary=re.sub(r'<[^>]*>', '', item.get("summary", ""))[:200],
                        publish_date=item.get("published", ""),
                        category="media",
                        score=0.6
                    ))
        return items

class AIFilter:
    """AI筛选去重器"""
    def __init__(self):
        # TODO: 集成大模型API进行智能筛选
        pass
    
    def filter_and_deduplicate(self, items: List[NewsItem], max_items: int = 20) -> List[NewsItem]:
        """筛选去重 - 简单版本基于关键词评分去重"""
        # 按分数降序排序
        scored_items = sorted(items, key=lambda x: x.score, reverse=True)
        
        # 简单去重：标题相似度
        unique_items = []
        seen_titles = set()
        
        for item in scored_items:
            # 简化标题去重
            simple_title = ''.join(c.lower() for c in item.title if c.isalnum())
            duplicate = False
            for seen in seen_titles:
                # 简单的包含检查
                if simple_title in seen or seen in simple_title:
                    if len(simple_title) > 0.8 * len(seen) or len(seen) > 0.8 * len(simple_title):
                        duplicate = True
                        break
            if not duplicate:
                seen_titles.add(simple_title)
                unique_items.append(item)
                if len(unique_items) >= max_items:
                    break
        
        return unique_items
    
    def categorize(self, items: List[NewsItem]) -> Dict[str, List[NewsItem]]:
        """分类整理"""
        categories = {
            "breaking": [],    # 今日要闻
            "company": [],     # 科技巨头动态
            "research": [],    # 研究前沿
            "product": [],     # 产品与工具
            "industry": [],    # 行业观察
        }
        
        for item in items:
            if item.category in categories:
                categories[item.category].append(item)
            else:
                # 根据内容自动分类
                title_lower = item.title.lower()
                if any(c.lower() in title_lower for c in ["openai", "anthropic", "google", "meta", "microsoft", "字节", "阿里", "智谱"]):
                    categories["company"].append(item)
                elif "paper" in title_lower or "research" in title_lower or "study" in title_lower:
                    categories["research"].append(item)
                elif "product" in title_lower or "launch" in title_lower or "tool" in title_lower or "app" in title_lower:
                    categories["product"].append(item)
                else:
                    categories["breaking"].append(item)
        
        return categories

class MarkdownGenerator:
    """生成Markdown日报"""
    def __init__(self, date: str = None):
        self.date = date or datetime.date.today().strftime("%Y-%m-%d")
    
    def generate(self, categorized: Dict[str, List[NewsItem]], focus_company: str = None) -> str:
        """生成Markdown格式日报"""
        md = f"# 🤖 AI日报 - {self.date}\n\n"
        
        # 重点关注
        if focus_company:
            md += f"**重点关注：{focus_company}**\n\n"
        md += "---\n\n"
        
        # 今日要闻
        if categorized["breaking"]:
            md += "## 🔔 今日要闻\n\n"
            for i, item in enumerate(categorized["breaking"], 1):
                md += f"### {i}. {item.title}\n"
                md += f"- 来源: {item.source}\n"
                if item.summary:
                    md += f"- 摘要: {item.summary}\n"
                md += f"- 链接: {item.url}\n\n"
            md += "---\n\n"
        
        # 科技巨头动态
        if categorized["company"]:
            md += "## 🏢 科技巨头动态\n\n"
            # 按公司分组
            company_groups: Dict[str, List[NewsItem]] = {}
            for item in categorized["company"]:
                company = item.company or self._extract_company(item.title)
                if company not in company_groups:
                    company_groups[company] = []
                company_groups[company].append(item)
            
            for company, items in company_groups.items():
                md += f"### {company}\n"
                for item in items:
                    md += f"- {item.title} - [{item.source}]({item.url})\n"
                    if item.summary:
                        md += f"  - {item.summary}\n"
                md += "\n"
            md += "---\n\n"
        
        # 研究前沿
        if categorized["research"]:
            md += "## 🔬 研究前沿\n\n"
            for i, item in enumerate(categorized["research"], 1):
                md += f"### {i}. {item.title}\n"
                md += f"- 发表: {item.publish_date}\n"
                if item.summary:
                    md += f"- 摘要: {item.summary}\n"
                md += f"- 链接: {item.url}\n\n"
            md += "---\n\n"
        
        # 产品与工具
        if categorized["product"]:
            md += "## 🛠 产品与工具\n\n"
            for i, item in enumerate(categorized["product"], 1):
                md += f"### {i}. {item.title}\n"
                md += f"- 来源: {item.source}\n"
                if item.summary:
                    md += f"- 简介: {item.summary}\n"
                md += f"- 链接: {item.url}\n\n"
            md += "---\n\n"
        
        # 行业观察
        if categorized["industry"]:
            md += "## 📊 行业观察\n\n"
            for item in categorized["industry"]:
                md += f"- {item.title}: {item.summary}\n\n"
            md += "---\n\n"
        
        md += f"*每天上午10点准时更新，重点追踪AI领域最新动态*\n"
        return md
    
    def _extract_company(self, title: str) -> str:
        """从标题提取公司名称"""
        companies = ["Anthropic", "OpenAI", "Google", "Meta", "Microsoft", "字节", "阿里", "智谱"]
        for company in companies:
            if company.lower() in title.lower():
                return company
        return "其他"
    
    def save(self, content: str) -> str:
        """保存到文件"""
        output_dir = os.path.join(BASE_DIR, "output")
        os.makedirs(output_dir, exist_ok=True)
        filename = f"daily-{self.date}.md"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return filepath

class FeishuPusher:
    """飞书推送器"""
    def __init__(self, config: Config):
        self.config = config
    
    def push_markdown(self, content: str, chat_id: str = None) -> bool:
        """推送Markdown到飞书群
        使用OpenClaw原生消息机制时不需要Webhook
        """
        target_chat = chat_id or self.config.default_chat_id
        if not target_chat:
            print("[ERROR] No chat_id configured")
            return False
        
        # 如果配置了Webhook，使用Webhook推送
        if self.config.feishu_webhook:
            return self._push_via_webhook(content)
        
        # 否则输出文件路径，由OpenClaw调用message工具推送
        print(f"[INFO] Ready to push to chat: {target_chat}")
        print(f"[INFO] Content:\n{content[:500]}...")
        return True
    
    def _push_via_webhook(self, content: str) -> bool:
        """通过Webhook推送"""
        try:
            # 飞书富文本格式
            data = {
                "msg_type": "post",
                "content": {
                    "post": {
                        "zh_cn": {
                            "title": content.split('\n')[0].replace('#', '').strip(),
                            "content": self._convert_to_feishu_content(content)
                        }
                    }
                }
            }
            response = requests.post(self.config.feishu_webhook, json=data, timeout=10)
            result = response.json()
            if result.get("code") == 0:
                print("[INFO] Push succeeded")
                return True
            else:
                print(f"[ERROR] Push failed: {result}")
        except Exception as e:
            print(f"[ERROR] Push exception: {e}")
        return False
    
    def _convert_to_feishu_content(self, md: str) -> List[List[Dict]]:
        """简单转换Markdown到飞书富文本格式"""
        content = []
        lines = md.split('\n')
        for line in lines:
            if not line.strip():
                continue
            if line.startswith('#'):
                # 标题
                text = line.replace('#', '').strip()
                content.append([{"tag": "text", "text": f"{text}\n", "unindent": False}])
            elif line.startswith('-'):
                # 列表项
                text = line[1:].strip() + '\n'
                content.append([{"tag": "text", "text": f"• {text}"}])
            else:
                content.append([{"tag": "text", "text": line + '\n'}])
        return content

class AIDailyNews:
    """主应用"""
    def __init__(self):
        self.config = Config()
        self.fetcher = NewsFetcher(self.config)
        self.filter = AIFilter()
        self.pusher = FeishuPusher(self.config)
    
    def generate_daily(self, date: str = None, push: bool = False, chat_id: str = None) -> Tuple[str, str]:
        """生成每日日报"""
        all_items: List[NewsItem] = []
        
        # 1. 抓取国内媒体
        print("[INFO] Fetching domestic media...")
        media_items = self.fetcher.fetch_all_domestic_media()
        all_items.extend(media_items)
        
        # 2. 抓取arXiv
        print("[INFO] Fetching arXiv papers...")
        arxiv_items = self.fetcher.fetch_arxiv(limit=10)
        all_items.extend(arxiv_items)
        
        # 3. 搜索重点公司新闻
        print("[INFO] Searching company news...")
        for company in self.config.focus_companies:
            company_items = self.fetcher.search_company_news(company, days=2)
            for item in company_items:
                item.company = company
            all_items.extend(company_items)
        
        # 4. AI筛选去重
        print(f"[INFO] Filtering {len(all_items)} items...")
        filtered = self.filter.filter_and_deduplicate(all_items, self.config.max_items)
        
        # 5. 分类
        categorized = self.filter.categorize(filtered)
        
        # 6. 选重点关注
        focus = None
        if categorized["company"]:
            focus = categorized["company"][0].company
        
        # 7. 生成Markdown
        print("[INFO] Generating Markdown...")
        generator = MarkdownGenerator(date)
        content = generator.generate(categorized, focus)
        
        # 8. 保存
        filepath = generator.save(content)
        print(f"[INFO] Saved to {filepath}")
        
        # 9. 推送
        if push:
            print("[INFO] Pushing...")
            self.pusher.push_markdown(content, chat_id)
        
        return content, filepath

def main():
    parser = argparse.ArgumentParser(description="AI Daily News Generator")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # generate 命令
    generate_parser = subparsers.add_parser("generate")
    generate_parser.add_argument("--date", default=None, help="Date (default: today)")
    generate_parser.add_argument("--push", action="store_true", help="Push after generate")
    generate_parser.add_argument("--chat-id", default=None, help="Target chat id")
    
    # fetch 命令
    fetch_parser = subparsers.add_parser("fetch")
    fetch_parser.add_argument("source", choices=["arxiv", "rss"], help="Source to fetch")
    fetch_parser.add_argument("--categories", nargs="+", help="arXiv categories")
    fetch_parser.add_argument("--limit", type=int, default=10, help="Limit")
    
    # search 命令
    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("--company", required=True, help="Company to search")
    search_parser.add_argument("--days", type=int, default=7, help="Days range")
    
    # push 命令
    push_parser = subparsers.add_parser("push")
    push_parser.add_argument("--chat-id", default=None, help="Target chat id")
    push_parser.add_argument("--file", required=True, help="Markdown file to push")
    
    args = parser.parse_args()
    
    app = AIDailyNews()
    
    if args.command == "generate":
        content, filepath = app.generate_daily(args.date, args.push, args.chat_id)
        if not args.push:
            print(content)
        print(f"\n[DONE] File saved: {filepath}")
    
    elif args.command == "fetch":
        if args.source == "arxiv":
            items = app.fetcher.fetch_arxiv(args.limit)
            for item in items:
                print(f"- {item.title} ({item.publish_date})")
                print(f"  {item.url}")
    
    elif args.command == "search":
        items = app.fetcher.search_company_news(args.company, args.days)
        for item in items:
            print(f"- {item.title}")
            print(f"  {item.summary}")
    
    elif args.command == "push":
        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read()
        success = app.pusher.push_markdown(content, args.chat_id)
        if success:
            print("[DONE] Push completed")
        else:
            print("[FAILED] Push failed")
            sys.exit(1)

if __name__ == "__main__":
    main()
