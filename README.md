# AI Quant Research Hub (AIQRH)

> AI 驱动股票量化研究平台 - 面向投资顾问或机构用户，提供 AI 驱动的股票量化分析、策略评分、回测模拟及可视化报告。

![alt text](image.png)

## 功能特性

### 核心功能
- 📊 **股票数据抓取与存储** - 支持多数据源（AkShare、Tushare）
- 🤖 **AI 驱动的股票评分系统** - 因子模型、技术指标、财务指标综合评分
- 📈 **回测引擎与风险指标分析** - 最大回撤、夏普比率、波动率等
- 📄 **自动化报告生成** - HTML/PDF 格式日报、周报
- 🔌 **RESTful API 服务** - 完整的后端 API 接口
- 🖥️ **Web Dashboard 可视化** - 现代化的前端界面

### 前端模块
- 📊 **仪表盘** - 市场概览、AI 评分 TOP 10、风险监控
- 📈 **股票分析** - 股票详情、价格走势、技术指标
- 💼 **组合管理** - 持仓管理、收益分析、行业配置
- 🧪 **回测分析** - 策略回测、权益曲线、交易记录
- 📄 **报告中心** - 报告列表、生成日报/周报、下载功能
- ⚙️ **设置页面** - API 配置、数据设置、通知

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- MongoDB 4.4+（可选，系统支持内存模式）

### 安装依赖

#### 后端依赖
```bash
cd g:\myaist\gupiao
pip install -r requirements.txt
```

#### 前端依赖
```bash
cd g:\myaist\gupiao\frontend
pnpm install
```

### 配置

#### 1. 创建 .env 文件

```bash
cd g:\myaist\gupiao
copy .env.example .env
```

#### 2. 配置 MongoDB（可选）

**方式一：使用本地 MongoDB**
```bash
# 下载并安装 MongoDB
# https://www.mongodb.com/try/download/community

# 启动 MongoDB 服务
net start MongoDB
```

**方式二：使用 Docker**
```bash
docker run -d --name mongodb -p 27017:27017 mongo:latest
```

**方式三：使用 MongoDB Atlas（云端）**
1. 注册账号：https://www.mongodb.com/cloud/atlas
2. 创建免费集群
3. 获取连接字符串，更新 `.env` 文件

#### 3. 配置 JWT 密钥

在 `.env` 文件中设置安全的 JWT 密钥：
```env
JWT_SECRET_KEY=your-super-secret-key-change-in-production
```

#### 4. 配置数据源

项目默认使用 **AkShare**（免费，无需 API Key），如需使用其他数据源：

**Tushare（推荐用于生产环境）**
1. 注册账号：https://tushare.pro/register
2. 获取 API Token
3. 更新 `config.yaml`：
   ```yaml
   data_source:
     primary: "tushare"
   ```
4. 在 `.env` 中添加：
   ```env
   TUSHARE_TOKEN=your_tushare_token_here
   ```

### 启动服务

#### PowerShell

```powershell
# 终端 1 - 启动后端
cd g:\myaist\gupiao
python -m uvicorn api.main:app --reload --port 8001

# 终端 2 - 启动前端
cd g:\myaist\gupiao\frontend
pnpm dev
```

#### CMD / Bash

```bash
# 终端 1 - 启动后端
cd g:\myaist\gupiao
python -m uvicorn api.main:app --reload --port 8001

# 终端 2 - 启动前端
cd g:\myaist\gupiao\frontend
pnpm dev
```

### 访问应用

- 🌐 **前端界面**：http://localhost:3000
- 🔧 **后端 API**：http://127.0.0.1:8001
- 📚 **API 文档**：http://127.0.0.1:8001/docs

## Docker 部署

### 使用 Docker Compose

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 停止服务
docker-compose down

# 查看日志
docker-compose logs -f
```

### 手动部署

#### 后端部署

```bash
# 使用 Gunicorn 启动
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
```

#### 前端部署

```bash
cd frontend
pnpm build
pnpm start
```

## API 接口

### 认证

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/login | 用户登录 |
| POST | /api/auth/register | 用户注册 |
| GET | /api/auth/me | 获取当前用户 |

### 股票

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/stocks/list | 股票列表 |
| GET | /api/stocks/scores | AI 评分 |
| GET | /api/stocks/{code} | 股票详情 |
| GET | /api/stocks/{code}/price | 价格数据 |
| GET | /api/stocks/{code}/indicators | 技术指标 |

### 市场

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/market/summary | 市场概览 |
| GET | /api/market/indices | 指数行情 |
| GET | /api/market/industry/heat | 行业热度 |
| GET | /api/market/sector/performance | 板块表现 |

### 组合

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/portfolio/list | 组合列表 |
| GET | /api/portfolio/{id} | 组合详情 |
| POST | /api/portfolio | 创建组合 |
| PUT | /api/portfolio/{id} | 更新组合 |
| DELETE | /api/portfolio/{id} | 删除组合 |
| GET | /api/portfolio/{id}/performance | 组合绩效 |

### 回测

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/backtest/run | 运行回测 |
| GET | /api/backtest/history | 回测历史 |
| POST | /api/backtest/compare | 比较策略 |

### 报告

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/reports/list | 报告列表 |
| GET | /api/reports/download/{id} | 下载报告 |
| POST | /api/reports/generate/daily | 生成日报 |
| POST | /api/reports/generate/weekly | 生成周报 |
| DELETE | /api/reports/{id} | 删除报告 |

## 配置说明

编辑 `config.yaml` 自定义：

### 股票池配置
```yaml
stock_pool:
  indices:
    - "000300.SH"  # 沪深300
    - "000905.SH"  # 中证500
  stocks:
    - "600519.SH"  # 贵州茅台
    - "000858.SH"  # 五粮液
```

### 数据源配置
```yaml
data_source:
  primary: "akshare"  # akshare / tushare
  cache_enabled: true
  cache_ttl: 3600
```

### AI 模型配置
```yaml
ai_model:
  scoring_method: "factor"  # factor / ai / hybrid
  factors:
    - "pe_ratio"
    - "pb_ratio"
    - "roe"
    - "momentum"
```

### 风控配置
```yaml
risk:
  backtest_period_days: 252
  max_drawdown_threshold: 0.2
  min_sharpe_ratio: 0.5
```

### 报告配置
```yaml
report:
  output_format: "pdf"  # pdf / html / dashboard
  charts:
    - "price_trend"
    - "scoring"
    - "backtest"
  daily_schedule: "09:00"
  weekly_schedule: "monday 09:00"
```

### 调度配置
```yaml
scheduler:
  enabled: true
  timezone: "Asia/Shanghai"
  jobs:
    - id: "daily_analysis"
      trigger: "cron"
      hour: 9
      minute: 0
```

## 环境变量

### 后端 (.env)

```bash
# MongoDB Configuration
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_USER=
MONGO_PASSWORD=
MONGO_DB=aiqrh
MONGO_CONNECTION=mongodb://localhost:27017/aiqrh

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-change-in-production

# Logging
LOG_LEVEL=INFO

# Data
DATA_DIR=data
```

### 前端

```bash
NEXT_PUBLIC_API_URL=http://localhost:8001
```

## 项目结构

```
gupiao/
├── main.py              # 主入口
├── config.yaml          # 配置文件
├── .env                 # 环境变量
├── requirements.txt     # Python 依赖
├── Dockerfile           # Docker 配置
├── docker-compose.yml   # 服务编排
├── SETUP.md            # 安装配置指南
├── core/
│   ├── engine.py        # 核心引擎
│   ├── models.py        # 数据模型
│   └── database.py      # 数据库连接
├── skills/
│   ├── skill_data/      # 数据采集
│   │   ├── fetcher.py
│   │   ├── mongo_storage.py
│   │   └── news.py
│   ├── skill_ai/        # 策略分析
│   │   ├── scorer.py
│   │   ├── analyzer.py
│   │   └── factors.py
│   ├── skill_risk/      # 风控模拟
│   │   ├── backtest.py
│   │   └── metrics.py
│   ├── skill_report/    # 报告生成
│   │   ├── generator.py
│   │   └── charts.py
│   └── skill_ops/       # 系统运维
│       ├── scheduler.py
│       └── logger.py
├── api/                 # FastAPI 服务
│   ├── main.py
│   ├── auth.py
│   └── routes/
│       ├── stocks.py
│       ├── market.py
│       ├── portfolio.py
│       ├── backtest.py
│       └── reports.py
├── frontend/           # Next.js 前端
│   ├── app/
│   │   ├── page.tsx              # 仪表盘
│   │   ├── stocks/              # 股票分析
│   │   ├── portfolio/           # 组合管理
│   │   ├── backtest/            # 回测分析
│   │   ├── reports/             # 报告中心
│   │   └── settings/            # 设置页面
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   └── Sidebar.tsx
│   │   └── ui/
│   │       ├── button.tsx
│   │       ├── card.tsx
│   │       └── input.tsx
│   └── lib/
│       ├── api.ts
│       └── utils.ts
├── data/               # 数据目录
├── reports/            # 报告输出
├── logs/              # 日志文件
└── tests/               # 单元测试
    ├── test_core.py
    └── test_api.py
```

## 测试

```bash
# 运行单元测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_core.py -v
```

## 技术栈

| 模块 | 技术 |
|------|------|
| 后端 | Python 3.10+, FastAPI, Uvicorn |
| 数据库 | MongoDB, PyMongo |
| 认证 | JWT, bcrypt |
| 前端 | Next.js 14, React 18, TypeScript |
| 图表 | Recharts |
| 样式 | Tailwind CSS |
| 容器 | Docker, Docker Compose |
| 数据分析 | Pandas, NumPy, SciPy |
| 机器学习 | Scikit-learn |

## 故障排查

### MongoDB 连接失败

```bash
# 检查 MongoDB 是否运行
# Windows
sc query MongoDB

# Linux
systemctl status mongod
```

### 端口冲突

如果端口 8001 或 3000 被占用，修改启动命令：

```bash
# 后端使用其他端口
python -m uvicorn api.main:app --reload --port 8002

# 前端使用其他端口
pnpm dev -- -p 3001
```

### 依赖安装失败

```bash
# 使用国内镜像源
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

## 安全建议

- 修改默认的 JWT 密钥
- 使用强密码
- 配置防火墙规则
- 定期备份数据库
- 使用 HTTPS（生产环境）

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

- 项目地址：https://github.com/yourusername/ai-quant-research-hub
- 问题反馈：https://github.com/yourusername/ai-quant-research-hub/issues
