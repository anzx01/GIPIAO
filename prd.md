# MVP PRD：AI 股票量化研究平台（不交易版）

## 1. 产品名称

**AI Quant Research Hub（AIQRH）**

 **定位** ：

> 面向投资顾问或机构用户，提供 AI 驱动的股票量化分析、策略评分、回测模拟及可视化报告。

---

## 2. 用户场景

| 用户类型      | 使用场景                               | 输出结果                             |
| ------------- | -------------------------------------- | ------------------------------------ |
| 投资顾问      | 每日筛选优质股票组合，支持客户投资决策 | 股票评分表 + 风险分析 + 图表报告     |
| 量化分析师    | 快速验证策略、回测组合、模拟风险       | 回测报告 + 策略优化建议              |
| 创始人/决策者 | 了解整体投资策略和风险                 | 综合可视化 Dashboard + 每日/每周报告 |

---

## 3. 核心目标（MVP）

1. 自动抓取股票行情及新闻数据
2. 使用 AI 模型生成股票评分与策略分析
3. 风控模拟（回测、最大回撤、夏普比率）
4. 输出自动化报告（PDF / Web Dashboard）
5. 模块化可扩展（OpenCode + OMO + Skills）

---

## 4. 系统架构

<pre class="overflow-visible! px-0!" data-start="686" data-end="1498"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-[calc(var(--sticky-padding-top)+9*var(--spacing))]"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>          +</span><span>-------------------------+</span><span>
          |     用户 / 投资顾问    |
          | Web / Dashboard / PDF  |
          +</span><span>-----------+-------------+</span><span>
                      |
                      v
         +</span><span>-------------------------+</span><span>
         |  OpenCode 执行内核      |
         | 调度 Skills + 流程解析 |
         +</span><span>-----------+-------------+</span><span>
                      |
          +</span><span>-----------+-------------+</span><span>
          | Oh-my-opencode (OMO)   |
          | 插件管理 + 流程编排    |
          +</span><span>-----------+-------------+</span><span>
          |           |             |
          v           v             v
   +</span><span>-------------+ +-------------+ +-------------+</span><span>
   | skill_data  | | skill_ai    | | skill_report|
   | 数据采集    | | 策略分析    | | 报告生成    |
   +</span><span>-------------+ +-------------+ +-------------+</span><span>
          |
          v
     数据仓库/日志/模型存储
</span></span></code></div></div></pre>

---

## 5. 核心模块（Skills）

### 5.1 数据采集（skill_data）

* 功能：
  * 股票历史行情、财务数据抓取
  * 新闻、舆情、社交媒体情绪抓取
  * 数据清洗、标准化、存储
* 技术：
  * Python + Pandas + Finance API
  * MongoDB/SQL 数据库
  * 支持数据版本管理

### 5.2 策略分析（skill_ai）

* 功能：
  * 股票评分：因子模型、技术指标、财务指标综合评分
  * 风险模拟：波动率、最大回撤、组合分散
  * 可模拟多策略（多 agent 协作，每个 Skill 代表一个分析角色）
* 技术：
  * LLM / Transformer / RL 模型
  * 支持多模型并行计算
  * 模型版本可迭代训练

### 5.3 风控模拟（skill_risk）

* 功能：
  * 回测策略：模拟历史收益、风险指标
  * 生成风险警示指标
  * 支持组合优化建议
* 技术：
  * 回测引擎（如 Backtrader、Zipline）
  * 可导出可视化指标图表

### 5.4 报告生成（skill_report）

* 功能：
  * PDF / Web Dashboard 自动生成
  * 图表可视化（价格趋势、评分、回测、风险指标）
  * 每日 / 每周 / 月度报告
* 技术：
  * Plotly / Matplotlib / D3.js
  * ReportLab / HTML→PDF

### 5.5 系统运维（skill_ops）

* 功能：
  * 心跳调度：每日/每小时自动执行任务
  * 日志记录和异常报警
  * 任务监控与复盘

---

## 6. MVP 功能清单

| 功能     | 说明                | MVP 可选功能             |
| -------- | ------------------- | ------------------------ |
| 数据抓取 | 股票历史行情 + 新闻 | 初期只抓取主要指数/股票  |
| 策略分析 | AI 模型生成评分     | 简单均线 + 因子评分      |
| 风控模拟 | 回测组合            | 简单最大回撤和收益率计算 |
| 报告生成 | PDF / Web Dashboard | 每日单页报告，可视化图表 |
| 循环调度 | 自动执行流程        | 每日/每小时执行一次      |
| 模块扩展 | 可添加新 Skill      | 支持新增分析或数据源     |

---

## 7. 技术选型

| 模块             | 技术/框架                        |
| ---------------- | -------------------------------- |
| 执行核心         | OpenCode CLI / Python            |
| 插件管理         | Oh-my-opencode (OMO)             |
| 数据存储         | MongoDB / PostgreSQL             |
| AI 模型          | LLM / Transformer / RL 模型      |
| 回测             | Backtrader / Zipline             |
| 报告 & Dashboard | Plotly / D3 / ReportLab / HTML   |
| 调度             | Cron / APScheduler / Docker 容器 |

---

## 8. 可扩展方向（Future Enhancements）

1. **多市场分析** ：A股、港股、美股、期货
2. **宏观事件驱动预测** ：结合重大新闻/政策/舆情
3. **策略优化平台** ：AI 自动迭代优化模型
4. **商业化功能** ：用户订阅 / API 输出 / 投资建议 SaaS

---

## 9. 输出示例

* **每日报告** ：
* 股票评分表（Top 10）
* 风险指标图表
* AI 策略分析摘要
* **Dashboard** ：
* 股票趋势图
* 历史回测收益对比
* 风险敞口可视化

---

## 10. MVP 核心价值

* 自动化量化分析，减少人工研究成本
* AI 职能拆分，提高分析专业性和可解释性
* 可扩展、可迭代，支持未来添加更多数据源和策略
* 安全、无真实交易风险
