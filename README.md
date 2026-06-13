<div align="center">

# S Research Skill

**A Codex skill for Serenity-style source cleanup, industry-chain research, China-company benchmarking, and browser-rendered HTML/PDF report generation.**

<p>
  <strong>Architecture migration</strong> -> <strong>Real chokepoint</strong> -> <strong>Supply-chain validation</strong> -> <strong>Equity result</strong>
</p>

</div>

---

## English

### Overview

S Research Skill is a Codex skill designed for two connected workflows:

| Mode | What It Does | Typical Output |
|---|---|---|
| Author-only X research | Clean and analyze Serenity / `@aleabitoreddit` X exports while separating author text from quotes, UI noise, and third-party summaries. | Clean CSV files, ticker tables, thesis tags, source-grounded methodology notes. |
| Industry-chain deep dive | Apply the S_research framework to industries, map real bottlenecks, compare global leaders with Chinese companies, and produce research reports. | Designed HTML reports and browser-rendered PDF reports. |

The skill is especially useful for industry research where the key question is not simply *which theme is hot*, but *which part of the supply chain is truly scarce, hard to replicate, underpriced, or becoming strategically important*.

---

### Core Research Logic

The S_research workflow follows this structure:

1. **Architecture migration**  
   Identify the structural, technological, regulatory, or demand-side shift.

2. **Real chokepoint**  
   Find what is physically scarce, hard to manufacture, difficult to certify, capacity-constrained, regulated, or strategically important.

3. **Supply-chain validation**  
   Map the bottleneck to actual companies, orders, capacity, qualification, customer relationships, or technical milestones.

4. **China-company benchmark**  
   Compare global leaders with representative Chinese companies by function, not by market cap or market hype.

5. **Equity translation**  
   Separate industrial importance from equity attractiveness: who captures margin, who gets commoditized, and what events validate or invalidate the thesis.

---

### PDF Report Preview

The report generator now follows this primary pipeline:

```text
JSON report spec -> designed HTML/CSS report -> Edge/Chrome browser-printed PDF
```

This keeps the PDF visually close to the HTML preview and avoids the plain layout produced by direct PDF drawing engines.

![S_research PDF report preview page 1](assets/report-preview-1.jpg)

![S_research PDF report preview page 2](assets/report-preview-2.jpg)

---

### Repository Structure

```text
s-research-skill/
  SKILL.md
  agents/
    openai.yaml
  assets/
    report-preview-1.jpg
    report-preview-2.jpg
  references/
    case-study-template.md
    china-company-benchmark.md
    report-output-template.md
    serenity-methodology.md
    taxonomy.md
  scripts/
    build_report_pdf.py
    clean_x_export.py
    fetch_status_details_cdp.mjs
    tag_ai_compute_chain.py
  .gitignore
  README.md
```

| Path | Purpose |
|---|---|
| `SKILL.md` | Main Codex skill instructions. |
| `agents/openai.yaml` | UI-facing metadata. |
| `assets/` | Preview images and other public visual assets. |
| `references/` | Methodology notes, templates, taxonomy, and China-company benchmarking rules. |
| `scripts/` | Reusable scripts for X export cleanup, tagging, CDP fetching, and HTML/PDF report generation. |

---

### Installation

Clone the repository into your local Codex skills directory:

```bash
git clone https://github.com/qianbab/qianbaobao.git <codex-skills-dir>/s-research-skill
```

Replace `<codex-skills-dir>` with the actual skills directory used by your Codex environment.

---

### Dependencies

The core skill instructions work without extra dependencies. Some scripts use optional local tools:

| Feature | Dependency |
|---|---|
| Browser-rendered PDF output | Microsoft Edge, Google Chrome, Chromium, or another supported Chromium browser |
| ReportLab fallback PDF | Python package `reportlab` |
| X status detail fetching through CDP | Node package `playwright` and a logged-in Chromium/Edge browser exposing a local CDP endpoint |

Optional installs:

```bash
pip install reportlab
npm install playwright
```

---

### Usage: X Export Cleanup

Clean a browser or timeline export:

```bash
python scripts/clean_x_export.py input.csv --out cleaned.csv --ticker-out ticker_frequency.csv
```

Tag cleaned rows by sector and thesis labels:

```bash
python scripts/tag_ai_compute_chain.py cleaned.csv --out tagged.csv --summary-out layer_summary.csv
```

Fetch fuller visible status-page text through a logged-in browser CDP session:

```bash
node scripts/fetch_status_details_cdp.mjs cleaned.csv --out status_details.csv
```

---

### Usage: Industry Report HTML/PDF

Create a JSON report spec following `references/report-output-template.md`, then run:

```bash
python scripts/build_report_pdf.py report_spec.json --html report.html --pdf report.pdf
```

By default, the script:

1. Builds a designed HTML/CSS report.
2. Uses Edge/Chrome headless printing to create the PDF.
3. Falls back to a simpler ReportLab PDF only if no supported browser is available.

Supported report elements:

| Element | Supported |
|---|---|
| Cover title and subtitle | Yes |
| Date and method line | Yes |
| Metric cards | Yes |
| Headings and paragraphs | Yes |
| Notes and bullet lists | Yes |
| Tables | Yes |
| Source list and disclaimer | Yes |
| Microsoft YaHei on Windows | Yes, through browser CSS or fallback font registration |

---

### China-Company Benchmarking

When benchmarking Chinese companies, the skill prioritizes **functional comparability** over market-cap comparability.

Recommended fields:

| Field | Meaning |
|---|---|
| Segment | The exact value-chain layer. |
| Bottleneck | The scarce or difficult capability. |
| Global leaders | Representative non-Chinese leaders. |
| Chinese companies | Mainland, Hong Kong, Taiwan-listed, or private Chinese companies. |
| Comparison logic | Why the comparison is valid and where it breaks. |
| Validation signals | Orders, revenue mix, qualification, capacity, approvals, margin, customer certification, or technical milestones. |
| Risks | Price war, substitution, policy, customer concentration, regulation, safety, or balance-sheet risk. |

See `references/china-company-benchmark.md` for more detail.

---

### Data and Privacy Notes

This public repository does **not** include:

- Raw X exports
- Cookies
- Browser profiles
- HAR files
- Login sessions
- Private notes
- Local machine paths

Do not commit private exports or browser-session artifacts. The `.gitignore` file excludes common temporary, browser, and export-related files.

---

### Limitations

- Browser timeline text can be truncated or contaminated by quoted posts and UI labels.
- X status-page fetching depends on login state, CDP availability, and visible-page content.
- Industry reports require up-to-date source verification when market data, company data, regulation, or product status may have changed.
- Investment-related output is research support only and is not personalized financial advice.

---

### Disclaimer

This repository is for research workflow automation and educational use. It does not provide investment, legal, medical, or financial advice. Users are responsible for verifying sources, respecting platform terms, and protecting private data.

---

<div align="center">

# S Research Skill 中文说明

**一个用于 Codex 的研究技能：支持 Serenity 风格信息清洗、产业链深度研究、中国企业对标，以及浏览器渲染版 HTML/PDF 研究报告输出。**

<p>
  <strong>架构迁移</strong> -> <strong>真实瓶颈</strong> -> <strong>供应链验证</strong> -> <strong>股权结果</strong>
</p>

</div>

---

## 中文

### 概览

S Research Skill 主要服务于两类相关工作流：

| 模式 | 功能 | 典型输出 |
|---|---|---|
| 作者本人 X 内容研究 | 清洗并分析 Serenity / `@aleabitoreddit` 的 X 导出内容，区分作者原文、引用帖、界面噪音和第三方总结。 | 清洗后的 CSV、ticker 表、thesis 标签、基于来源的方法论总结。 |
| 产业链深度研究 | 将 S_research 框架应用到具体产业，识别真实瓶颈，进行全球公司与中国企业对标，并生成研究报告。 | 设计化 HTML 报告和浏览器渲染版 PDF 报告。 |

这个 skill 最适合回答的问题不是“哪个概念最热”，而是“产业链中哪个环节真正稀缺、难以复制、尚未充分定价，或者正在变得具有战略意义”。

---

### 核心研究逻辑

S_research 工作流遵循以下结构：

1. **架构迁移**  
   识别产业正在发生的结构性、技术性、监管性或需求侧变化。

2. **真实瓶颈**  
   找到真正稀缺、难制造、难认证、受产能约束、受监管约束或具备战略重要性的环节。

3. **供应链验证**  
   将瓶颈映射到真实公司、订单、产能、客户认证、技术节点或商业化里程碑。

4. **中国企业对标**  
   按功能和产业链位置对标中国企业，而不是简单按市值、热度或概念对标。

5. **股权结果转化**  
   区分“产业重要性”和“股权吸引力”：谁能获得利润，谁会被商品化，哪些事件会验证或推翻 thesis。

---

### PDF 报告效果预览

当前报告生成器的主路径是：

```text
JSON 报告规格 -> 设计化 HTML/CSS 报告 -> Edge/Chrome 浏览器打印 PDF
```

这样可以让 PDF 尽量保持 HTML 预览版式，避免直接绘制 PDF 时过于朴素的排版效果。

![S_research PDF 报告预览第 1 页](assets/report-preview-1.jpg)

![S_research PDF 报告预览第 2 页](assets/report-preview-2.jpg)

---

### 仓库结构

```text
s-research-skill/
  SKILL.md
  agents/
    openai.yaml
  assets/
    report-preview-1.jpg
    report-preview-2.jpg
  references/
    case-study-template.md
    china-company-benchmark.md
    report-output-template.md
    serenity-methodology.md
    taxonomy.md
  scripts/
    build_report_pdf.py
    clean_x_export.py
    fetch_status_details_cdp.mjs
    tag_ai_compute_chain.py
  .gitignore
  README.md
```

| 路径 | 用途 |
|---|---|
| `SKILL.md` | Codex 使用该 skill 的核心说明。 |
| `agents/openai.yaml` | 面向界面展示的元数据。 |
| `assets/` | 预览图和其他公开视觉资源。 |
| `references/` | 方法论、模板、分类体系和中国企业对标规则。 |
| `scripts/` | 可复用脚本，包括 X 导出清洗、标签分类、CDP 抓取和 HTML/PDF 报告生成。 |

---

### 安装方式

将仓库克隆到你的 Codex skills 目录：

```bash
git clone https://github.com/qianbab/qianbaobao.git <codex-skills-dir>/s-research-skill
```

请将 `<codex-skills-dir>` 替换为你本地 Codex 环境实际使用的 skills 目录。

---

### 依赖

skill 的核心说明不需要额外依赖即可使用。部分脚本会使用可选本地工具：

| 功能 | 依赖 |
|---|---|
| 浏览器渲染 PDF 输出 | Microsoft Edge、Google Chrome、Chromium 或其他支持的 Chromium 浏览器 |
| ReportLab 兜底 PDF | Python 包 `reportlab` |
| 通过 CDP 抓取 X status 详情 | Node 包 `playwright`，以及已登录并开启本地 CDP 端口的 Chromium/Edge 浏览器 |

可选依赖安装：

```bash
pip install reportlab
npm install playwright
```

---

### 用法：X 导出清洗

清洗浏览器或时间线导出的 CSV：

```bash
python scripts/clean_x_export.py input.csv --out cleaned.csv --ticker-out ticker_frequency.csv
```

对清洗后的内容进行产业和 thesis 标签分类：

```bash
python scripts/tag_ai_compute_chain.py cleaned.csv --out tagged.csv --summary-out layer_summary.csv
```

通过已登录浏览器的 CDP 会话抓取更完整的 status 页面可见文本：

```bash
node scripts/fetch_status_details_cdp.mjs cleaned.csv --out status_details.csv
```

---

### 用法：产业研究 HTML/PDF 报告

先按照 `references/report-output-template.md` 创建 JSON 报告规格文件，然后运行：

```bash
python scripts/build_report_pdf.py report_spec.json --html report.html --pdf report.pdf
```

默认情况下，该脚本会：

1. 生成设计化 HTML/CSS 报告。
2. 使用 Edge/Chrome 无头打印生成 PDF。
3. 只有在找不到可用浏览器时，才回退到较简洁的 ReportLab PDF。

支持的报告元素：

| 元素 | 支持情况 |
|---|---|
| 封面标题和副标题 | 支持 |
| 日期和方法论说明 | 支持 |
| 指标卡片 | 支持 |
| 标题和段落 | 支持 |
| 提示说明和项目符号列表 | 支持 |
| 表格 | 支持 |
| 来源列表和免责声明 | 支持 |
| Windows 微软雅黑字体 | 支持，通过浏览器 CSS 或兜底字体注册实现 |

---

### 中国企业对标

进行中国企业对标时，本 skill 优先考虑**功能对标**，而不是简单按市值、热度或概念对标。

推荐字段：

| 字段 | 含义 |
|---|---|
| 产业链环节 | 企业实际参与竞争的位置。 |
| 真实瓶颈 | 稀缺或难以复制的能力。 |
| 全球代表企业 | 海外代表性龙头或可比公司。 |
| 中国代表企业 | A 股、港股、台股或未上市中国企业。 |
| 对标逻辑 | 为什么可比，以及对标在哪里不成立。 |
| 验证信号 | 订单、收入结构、客户认证、产能、审批、毛利率或技术里程碑。 |
| 风险 | 价格战、替代路线、政策、客户集中、监管、安全或资产负债表风险。 |

详见 `references/china-company-benchmark.md`。

---

### 数据与隐私说明

这个公开仓库不包含：

- X 原始导出数据
- Cookie
- 浏览器 profile
- HAR 文件
- 登录会话
- 私人笔记
- 本机绝对路径

请不要提交私人导出文件或浏览器会话文件。仓库中的 `.gitignore` 已经排除了常见临时文件、浏览器文件和导出数据。

---

### 限制

- 浏览器时间线文本可能被截断，也可能混入引用帖和界面标签。
- X status 页面抓取依赖登录状态、CDP 可用性和页面可见内容。
- 当市场数据、公司数据、监管状态或产品状态可能变化时，产业报告必须结合最新来源验证。
- 涉及投资的输出仅用于研究辅助，不构成个性化投资建议。

---

### 免责声明

本仓库仅用于研究流程自动化和学习用途，不提供投资、法律、医疗或财务建议。使用者应自行核验来源，遵守平台规则，并保护私人数据。
