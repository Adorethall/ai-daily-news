# AI 日报 HTML 渲染模板

本文件包含日报卡片的完整 HTML/CSS 模板，供 Claude 渲染时参考。

---

## CSS 样式块

```html
<style>
*{box-sizing:border-box;margin:0;padding:0}
.wrap{padding:1.5rem 0}
.header{border-bottom:0.5px solid var(--color-border-tertiary);padding-bottom:1rem;margin-bottom:1.5rem}
.date-badge{display:inline-block;font-size:12px;color:var(--color-text-info);background:var(--color-background-info);padding:3px 10px;border-radius:99px;margin-bottom:0.5rem}
.headline{font-size:22px;font-weight:500;color:var(--color-text-primary);line-height:1.3}
.sub{font-size:14px;color:var(--color-text-secondary);margin-top:0.4rem}
.section-title{font-size:12px;font-weight:500;color:var(--color-text-secondary);text-transform:uppercase;letter-spacing:0.06em;margin:1.5rem 0 0.75rem}
.card{background:var(--color-background-primary);border:0.5px solid var(--color-border-tertiary);border-radius:var(--border-radius-lg);padding:1rem 1.25rem;margin-bottom:0.75rem}
.card-tag{display:inline-block;font-size:11px;padding:2px 8px;border-radius:99px;margin-bottom:0.5rem;font-weight:500}
.card-title{font-size:15px;font-weight:500;color:var(--color-text-primary);line-height:1.4;margin-bottom:0.35rem}
.card-body{font-size:13px;color:var(--color-text-secondary);line-height:1.6}
.highlight-row{display:flex;gap:10px;margin-bottom:1.5rem}
.stat-box{flex:1;background:var(--color-background-secondary);border-radius:var(--border-radius-md);padding:0.75rem 1rem;text-align:center}
.stat-num{font-size:20px;font-weight:500;color:var(--color-text-primary)}
.stat-label{font-size:11px;color:var(--color-text-secondary);margin-top:2px}
.divider{height:0.5px;background:var(--color-border-tertiary);margin:1.25rem 0}
.footer{font-size:12px;color:var(--color-text-tertiary);text-align:center;padding-top:1rem;border-top:0.5px solid var(--color-border-tertiary);margin-top:1.5rem}

/* Tag 颜色映射 */
/* OpenAI — 蓝色系 */
.tag-openai{background:#E6F1FB;color:#185FA5}
/* DeepSeek / 国内大模型 — 绿色系 */
.tag-deepseek{background:#E1F5EE;color:#0F6E56}
/* Google / Gemini — 黄色系 */
.tag-google{background:#FAEEDA;color:#854F0B}
/* 特斯拉 / 自动驾驶 — 红色系 */
.tag-tesla{background:#FCEBEB;color:#A32D2D}
/* 政策 / 国内官方 — 紫色系 */
.tag-china{background:#EEEDFE;color:#534AB7}
/* 产业 / 资本 / 芯片 — 灰色系 */
.tag-industry{background:#F1EFE8;color:#5F5E5A}
/* 量子 / 前沿研究 — 粉色系 */
.tag-quantum{background:#FBEAF0;color:#993556}
/* Meta / 社交媒体 — 深蓝系 */
.tag-meta{background:#E6F1FB;color:#0C447C}
/* Anthropic / Claude — 珊瑚色系 */
.tag-anthropic{background:#FAECE7;color:#993C1D}
/* 字节跳动 / ByteDance */
.tag-bytedance{background:#E6F7FF;color:#006680}
/* 阿里 / Alibaba */
.tag-alibaba{background:#FDF7E8;color:#856404}
/* 智谱 / Zhipu */
.tag-zhipu{background:#F0F9FF;color:#075985}
/* 监管 / 法律 — 琥珀色系 */
.tag-regulation{background:#FAEEDA;color:#633806}
</style>
```

---

## 完整结构模板

```html
<style>
/* 粘贴上方完整 CSS，并加入需要的 tag 颜色类 */
</style>

<div class="wrap">
 <!-- 顶部 header -->
 <div class="header">
 <div class="date-badge">{YYYY}年{MM}月{DD}日 · 星期{X}</div>
 <div class="headline">AI 日报</div>
 <div class="sub">今日要点：{一句话总结当天最重要的2-3个事件}</div>
 </div>

 <!-- 数字亮点（3个） -->
 <div class="highlight-row">
 <div class="stat-box">
 <div class="stat-num">{数字1}</div>
 <div class="stat-label">{说明1}</div>
 </div>
 <div class="stat-box">
 <div class="stat-num">{数字2}</div>
 <div class="stat-label">{说明2}</div>
 </div>
 <div class="stat-box">
 <div class="stat-num">{数字3}</div>
 <div class="stat-label">{说明3}</div>
 </div>
 </div>

 <!-- 头条 -->
 <div class="section-title">🔥 头条</div>
 <div class="card">
 <span class="card-tag tag-{category}">{分类名}</span>
 <div class="card-title">{新闻标题}</div>
 <div class="card-body">{2-3句摘要}</div>
 </div>
 <!-- 重复 card... -->

 <div class="divider"></div>

 <!-- 国内动态 -->
 <div class="section-title">🇨🇳 国内动态</div>
 <!-- cards... -->

 <div class="divider"></div>

 <!-- 海外动态 -->
 <div class="section-title">🌐 海外动态</div>
 <!-- cards... -->

 <div class="divider"></div>

 <!-- 产业与资本（有内容时显示） -->
 <div class="section-title">📈 产业与资本</div>
 <!-- cards... -->

 <!-- 研究前沿（可选，有重要论文/突破时显示） -->
 <!-- <div class="divider"></div>
 <div class="section-title">🔬 研究前沿</div> -->

 <!-- 底部 footer -->
 <div class="footer">数据来源：{来源列表} · 截至今日北京时间</div>
</div>
```

---

## 渲染调用示例

```
visualize:show_widget(
 title: "ai_daily_{YYYYMMDD}",
 loading_messages: ["聚合今日AI情报...", "整理头条资讯...", "排版日报中..."],
 widget_code: <完整 HTML>
)
```

---

## 深色模式说明

所有 tag 的背景色使用了色板的 50 号硬编码色（如 `#E6F1FB`）。这在浅色模式下没问题，但在深色模式下会有些突出。如需完美支持深色模式，可改用 CSS 变量：

```css
.tag-openai {
 background: var(--color-background-info);
 color: var(--color-text-info);
}
```

但这样所有"信息类"tag 颜色会相同。根据视觉需求选择方案。
