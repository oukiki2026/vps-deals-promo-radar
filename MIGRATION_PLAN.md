# kikomono.com Hugo 迁移方案（Phase 1）

> 状态：方案待皇上过目。**未开始实施，未 push 任何内容。**
> 约束：老架构（`~/workspace/kikomono`）的日更定时任务 `kikomono-daily-article` 不停更、不触碰；本方案所有工作在 `~/workspace/kikomono-hugo` 独立克隆中进行。

## 1. 目标与非目标

**目标**：把渲染层从自研 Python 构建器（`build.py`）迁到 Hugo；Python 只保留数据层（`scraper.py` 抓取/核验报价 → `data/offers.json`）。之后加功能（如署名、sitemap 调整）走 Hugo 模板，一改全生效。

**非目标**：
- 不改变任何 URL（45 个页面路径零变化，Google 已收录 52 页——这是硬指标）。
- 不改变读者可见内容与广告披露（affiliate 规范逐字节保留）。
- 不重写抓取/核验逻辑（`scraper.py`、`active_offers` 规则、`AGENTS.md` 铁律全部保留）。
- 不处理已验证未推送的 IONOS 解析修复（以当前 main 为准；该修复获批 push 后再 rebase 进迁移分支）。

## 2. 现状盘点

### 2.1 页面清单（45 个 URL，构建实测）

| 来源模块 | 页面 |
|---|---|
| `build.py` core | `/`, `/hosting/`, `/offers/`, `/compare/`, `/methodology/`, `/privacy/`, `/about/`, `/contact/`, `/providers/ionos/`, `/providers/digitalocean/`, `/providers/hetzner/` |
| `build.py` core（动态） | `/deals/{id}/`（当前 0 个；有报价时按 `offers.json` 生成） |
| `beginner_content.py` | `/start/`, `/free-ai/` |
| `ai_content.py` | `/ai-tools/`（hub）+ `/ai-tools/cursor/`, `/ai-tools/github-copilot/`, `/ai-tools/hostinger-ai-builder/`, `/ai-tools/hugging-face-inference-endpoints/`, `/ai-tools/coding-assistant-checklist/`, `/ai-tools/ai-app-budget/` |
| `meeting_content.py` | `/ai-tools/ai-meeting-notes/`, `/ai-tools/audio-video-transcription/`, `/ai-tools/verify-ai-meeting-summaries/` |
| `muse_content.py` | `/ai-tools/meta-muse-guide/` |
| `pdf_content.py` | `/ai-tools/scanned-pdf-to-text/` |
| `export_content.py` | `/ai-tools/check-free-ai-export/` |
| `quota_content.py` | `/ai-tools/save-free-ai-progress/` |
| `citation_content.py` | `/ai-tools/check-ai-citations/` |
| `freshness_content.py` | `/ai-tools/check-ai-source-updates/` |
| `clarification_content.py` | `/ai-tools/ask-about-missing-details/` |
| `table_state_content.py` | `/ai-tools/keep-zero-blank-unknown/` |
| `unit_content.py` | `/ai-tools/check-units-in-ai-tables/` |
| `currency_content.py` | `/ai-tools/keep-currency-codes-in-ai-tables/` |
| `cursor_access_content.py` | `/ai-tools/cursor-free-access/` |
| `student_content.py` | `/ai-tools/free-ai-tools-for-students/`（署名 By Lika） |
| `writing_content.py` | `/ai-tools/free-ai-tools-for-writing/`（署名 By Lika） |
| `image_content.py` | `/ai-tools/free-ai-tools-for-images/`（署名 By Lika） |
| `guides.py` | `/guides/how-to-choose-first-vps/`, `/guides/how-to-read-vps-promo-terms/`, `/guides/vps-vs-managed-static-hosting/`, `/guides/evaluate-new-ai-model/`, `/guides/ai-subscription-vs-api/`, `/ai-news/`, `/ai-news/gemini-flash-migration-check/` |
| `guide_directory.py` | `/guides/`（自动索引 `/ai-tools/`, `/guides/`, `/ai-news/` 下页面） |

### 2.2 当前构建管线

```
site-config/site.conf ─┬─→ scraper.py ──→ data/offers.json（原始报价记录）
                       └─→ build.py ──→ site/（45 页 HTML + sitemap.xml + robots.txt + _headers + 404.html + data/offers.json 公开子集）
                                     └─→ validate.py（sitemap/canonical/内链/JSON-LD/署名校验）
```

- 部署：Cloudflare Pages，构建命令 `python build.py`，输出目录 `site/`。
- 定时 `update.yml`（每 6 小时）：unittest → scraper.py → build.py → validate.py → commit `data/`/`README.md`/workflow。
- 测试：`tests/test_pipeline.py`（解析器、去重、过期剔除、配置变更）、`tests/test_ai_content.py`（`ai_tools_enabled` 开关）。

### 2.3 必须逐字节保留的合规要素

- Affiliate 广告：`AFFILIATE ADVERTISEMENT` 眉题、`rel="sponsored noopener"`、佣金披露句、privacy 链接。位置：首页（Systeme.io、Wondershare）、AI Tools hub（Proton Lumo）、meeting 指南（Notta 官方横幅）、pdf/转录指南（Wondershare）。
- `MONETIZATION.md` 的投放清单与页面实际状态一致。
- `mitgo` / `impact` / `commission-factory` 三个站长验证 meta（在 `base.html` head）。
- CSP `_headers`（GA4 启用时动态拼接）。

## 3. 目标架构

```
site-config/site.conf ─┬─→ scraper.py ──→ data/offers.json（原始记录，不变）
                       │
                       └─→ tools/prebuild.py ─┬─→ hugo.yaml（由 site.conf 生成，含 style.css hash、GA4、开关）
                                              ├─→ data/active_offers.json（active_offers() 过滤结果，供模板）
                                              ├─→ content/deals/{id}.md（每个有效报价一篇，gitignore，不提交）
                                              ├─→ static/data/offers.json（公开子集）
                                              └─→ static/_headers（CSP，按 GA4 开关生成）
content/（已提交的 Markdown：全部文章/指南/静态页）
layouts/（Hugo 模板，复刻现有 HTML）
static/（assets 原样搬迁：style.css、logo.svg、og.png、affiliate/、editorial/、practice/、analytics.js、tutorial-actions.js）
                           ↓
                    hugo --minify -d site → site/ → validate.py（移植版）
```

**设计原则**：
- 业务逻辑（过期剔除、去重、`ai_tools_enabled` 开关、署名规则）**全部留在 Python**（`prebuild.py` 复用现有函数），Hugo 只做纯渲染。这样现有 `test_pipeline.py` 的数据层测试几乎不用改。
- `content/` 里的 Markdown 是编辑层：定时任务以后写 `.md` 而不是写 `.py` 模块。
- 输出目录保持 `site/`，Cloudflare Pages 构建命令改为 `python tools/prebuild.py && hugo --minify -d site`（Hugo 版本 pin `0.167.0`，与 china0432 一致；Pages 原生支持 Hugo，或改走 china0432 已验证的 wrangler-action workflow——二选一，Phase 2 定）。

## 4. 内容迁移：模块 → Markdown 映射

| 现状 | 迁移后 | 说明 |
|---|---|---|
| 19 个 `*_content.py` 的 `BODY`（HTML 字符串） | `content/ai-tools/{slug}.md` 等 Markdown 文件 | BODY 原样作为 Markdown 正文（HTML 透传，需 `markup.goldmark.renderer.unsafe: true`）；`TITLE`→`title`，`DESCRIPTION`→`description`，`lastmod=`→ front matter `date` |
| `student/writing/image_content.py` 三篇 | 同上 | 署名不再写在正文里 |
| `guides.py` 的 `GUIDES` 列表 | `content/guides/{slug}.md` | 同上 |
| `guide_directory.py` 的 `/guides/` 索引 | `content/guides/_index.md` + section 模板 | 按前缀自动索引逻辑搬进模板 |
| `beginner_content.py` 的 `/start/`、`/free-ai/` | `content/start.md`、`content/free-ai.md` | 同上 |
| `build.py` 内联的 `/`, `/hosting/`, `/offers/`, `/compare/`, `/methodology/`, `/privacy/`, `/about/`, `/contact/` | `content/_index.md`、`content/{hosting,offers,compare,methodology,privacy,about,contact}.md` + 专用 layout | 模板从现有 `templates/*.html` 移植 |
| `/providers/{id}/`、`/deals/{id}/` | `tools/prebuild.py` 动态生成（gitignore） | 字段全部进 front matter，模板纯渲染 |

**转换方式**：写一次性脚本 `tools/convert_content.py`（Phase 2 用完即弃），从各模块提取 `TITLE/DESCRIPTION/BODY/lastmod/path` 生成 Markdown；人工抽查 5 篇 diff 确认无内容丢失。

## 5. 模板方案（layouts ← templates 映射）

| 现状 | Hugo |
|---|---|
| `templates/base.html` | `layouts/_default/baseof.html`（header/nav/footer/JSON-LD 面包屑全部保留） |
| 各页面 `page()` 拼装 | `layouts/index.html`（首页）、`layouts/_default/single.html`（文章/指南）、section `_index` 模板 |
| `build.py` 署名注入（free-ai-tools-* → `By Lika`） | `single.html` 模板条件：路径前缀匹配则渲染 `<p class="byline">By Lika</p>`；正文自带 byline 则跳过（沿用 china0432 已验证模式） |
| JSON-LD（BreadcrumbList 全站；ItemList 在 hosting/offers/compare/providers；Offer+seller 在 deals；Service 在 providers） | 模板内 `dict` + `jsonify` 拼装，字段来源 front matter / `data/active_offers.json` |
| sitemap | 自定义 `layouts/sitemap.xml`，**精确复刻现有格式**（仅 `<loc>` + `<lastmod>`，无 priority/changefreq）；lastmod 取 front matter `date`，deal 页取 `fetched_at` |
| robots.txt | 自定义 `layouts/robots.txt`（`Allow: /` + Sitemap 行；Hugo 默认 robots 与现状不同，不可用默认） |
| 404 | `layouts/404.html`（精确复刻：无 header/footer、noindex、回首页按钮） |
| `style.css?v={sha12}` | `prebuild.py` 计算 sha256 → `hugo.yaml` params → 模板拼接（行为与现状一致） |
| GA4（`analytics.js` + measurement-id，开关控制） | 模板 `if` 条件渲染；`analytics_scripts` 变量逻辑保留 |
| `tutorial-actions.js` 条件加载（正文含 blockquote/pre/practice-checklist 才加） | 模板内 `in .Content "<blockquote"` 等条件判断 |
| affiliate 广告块（NOTTA/Wondershare/Lumo/Systeme.io） | **第一阶段原样内联**在转换后的 Markdown 里（HTML 透传，零风险）；shortcode 化列为可选后续优化 |
| `_headers`（CSP） | `prebuild.py` 生成 `static/_headers`，逻辑照搬 `build.py` |

## 6. Deal 管线设计（Python 数据预处理 → Hugo 渲染）

```
scraper.py（不变：robots 检查、官方源抓取、去重、写入 data/offers.json）
   ↓
tools/prebuild.py（新，复用 build.py 的 active_offers/config 逻辑）：
   1. load_config(site.conf) → 生成 hugo.yaml（含 baseURL、brand、tagline、GA4、ai_tools_enabled→ignoreFiles、style hash）
   2. active_offers(cfg, data/offers.json) → data/active_offers.json
   3. 为每个有效 offer 生成 content/deals/{id}.md（front matter：title/price/currency/period/specs/terms/source_url/evidence/fetched_at/source_sha256/affiliate_target/rel/disclosure/schema 字段；正文为空，模板渲染）
   4. 生成 content/providers/{id}.md（front matter 带 provider 信息；卡片列表由模板 range active_offers）
   5. 写 static/data/offers.json（公开子集，字段与现状一致）
   6. 写 static/_headers
   ↓
hugo --minify -d site（纯渲染，无业务逻辑）
   ↓
validate.py（移植：见 §7）
```

`ai_tools_enabled=false` 的处理：`prebuild.py` 在生成的 `hugo.yaml` 里写 `ignoreFiles: ["content/ai-tools/.*"]`（对应现有 `test_ai_content.py` 的断言）。

## 7. 校验对等方案

现有 `validate.py` 几乎全部是**产物断言**（sitemap/canonical/内链/JSON-LD/署名），与生成器无关——**原样保留**，只需把输入目录指向 Hugo 产物（两者都叫 `site/`，零改动）。

新增**新旧对等校验**（`tools/parity_check.py`，Phase 2 实现，CI 常驻）：
1. **URL 集合对等**：新旧 sitemap 的 URL 集合必须 45/45 完全一致（含尾部斜杠），差一个即失败。
2. **HTML 归一化 diff**：逐页对比（去除 `style.css?v=` hash、`fetched_at` 时间戳等已知变量后），差异超过白名单即失败。deal 页为空时（当前状态）跳过 deal 相关断言。
3. **合规断言**：每个含广告的页面必须含 `AFFILIATE ADVERTISEMENT` + `rel="sponsored"`；`_headers` 含 CSP；`robots.txt` 含 Sitemap 行。

测试去留：
- 保留：`test_pipeline.py` 的 scraper/解析/去重/过期测试、`test_ai_content.py` 改写为测 `prebuild.py` 的 `ignoreFiles` 行为。
- 重写：原来直接调 `build()` 的集成测试 → 改为调 `prebuild.py` + `hugo` 子进程（或测 prebuild 产物）。

## 8. 定时任务与日常运营变更

| 事项 | 现状 | 迁移后 |
|---|---|---|
| `kikomono-daily-article`（09:21） | 写 `*_content.py` Python 模块 → unittest → build.py → validate.py → `gh_push.py` | 写 `content/ai-tools/{slug}.md`（Markdown + front matter：title/description/date）→ unittest → `prebuild.py` → `hugo` → validate.py → `gh_push.py`（推送方式不变） |
| 署名 | cron 指令要求手写（现已改为构建自动注入） | 模板自动注入，写文章时**完全不用管署名** |
| 去 AI 味写作规范 | 不变 | 不变（只换载体） |
| `update.yml`（每 6h） | unittest → scraper → build → validate → commit data/ | unittest → scraper → prebuild → hugo → validate → commit data/（`content/deals/` gitignore，不提交） |
| 推送工具 | `gh_push.py`（Git Data API） | 不变（推文件集合变化而已） |

## 9. 切换方案与回滚预案

**切换**（全部在迁移分支验证通过后）：
1. 迁移分支 `hugo-migration` 上完成实现 + parity 检查全绿。
2. 皇上过目 → 合并到 `main`。
3. Cloudflare Pages 构建命令改为 `python tools/prebuild.py && hugo --minify -d site`（HUGO_VERSION=0.167.0；或改走 wrangler workflow，二选一）。
4. 部署后：抽查 5 页线上 HTML（含 1 篇 deal 页如有）、sitemap、robots.txt；GSC URL 检查抽查；盯 1–2 周收录曲线。

**回滚**：`git revert` 合并提交 → Pages 自动用旧命令重建（Python 构建器仍在 git 历史里）。回滚窗口：切换后 48 小时内如发现收录异常立即回滚。**回滚不需要改动线上数据**，纯静态站点。

**迁移窗口期的日更**：老架构继续每天发文；切换瞬间把窗口期内新增的 3–7 篇文章转成 Markdown 一并带入（转换脚本复用）。

## 10. 风险清单

| # | 风险 | 缓解 |
|---|---|---|
| 1 | URL 漂移（SEO 灾难） | parity 检查强制 45/45 URL 集合一致；Hugo 默认 pretty URL 即 `path/index.html`，与现状同构 |
| 2 | sitemap XML 格式差异（Hugo 默认模板可能多字段） | 自定义 sitemap 模板精确复刻；diff 校验 |
| 3 | lastmod 语义差异（Hugo 用文件时间 vs 现状用 front matter/业务时间） | front matter 显式写 `date`/`lastmod`；`enableGitInfo=false` |
| 4 | affiliate 披露丢失/错位 | 合规断言进 CI；第一阶段广告块原样内联不重构 |
| 5 | `update.yml` 改造后 6 小时定时任务失效 | 先在分支跑完整 workflow（含手动触发），再合并 |
| 6 | Pages 构建环境缺 Hugo | HUGO_VERSION 环境变量（Pages 原生支持）或 wrangler workflow；分支上先验证一次真实部署 |
| 7 | 切换后 GSC 抓取异常 | 切换后立即 GSC URL 检查 + 1–2 周收录监控；48h 回滚窗口 |
| 8 | 定时任务改写引入人为失误（Markdown front matter 写错） | validate 校验 front matter 必填字段；cron 指令给出 front matter 模板 |
| 9 | IONOS 修复与迁移分支冲突 | 迁移基于当前 main；IONOS 修复获批后先合入 main 再 rebase（已在非目标中声明） |

## 11. Phase 2 实施步骤（待批准后执行）

1. 建分支 `hugo-migration`（从 main 新鲜拉取）。
2. 写 `tools/prebuild.py` + `tools/convert_content.py`；转出全部 Markdown，抽查 5 篇。
3. 写 `hugo.yaml` 生成逻辑、`layouts/` 全套模板、`static/` 资源搬迁。
4. 本地构建 → 跑 `parity_check.py`（URL 集合 + HTML diff）→ 修到全绿。
5. 移植 `validate.py` 断言，跑通 `unittest`。
6. 改造 `update.yml`（分支上手动触发验证）。
7. 汇报：parity 报告 + 待皇上批准切换。
8. （切换批准后）改写 `kikomono-daily-article` cron 指令为 Markdown 流；更新交接文档同步 Rita。

**工作量估算**：约 2–4 天专注工作（含 parity 调优）。风险最高的不是内容转换（机械），而是模板与现状 HTML 的逐字节对齐（sitemap/JSON-LD/广告块）。

---
*方案编写：2026-10-17（Lika）｜状态：待皇上过目*
