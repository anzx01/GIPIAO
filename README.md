# AI Quant Research Hub (AIQRH)

AI 驱动股票量化研究平台
![alt text](image.png)
## 功能特性

- 股票数据抓取与存储
- AI 驱动的股票评分系统
- 回测引擎与风险指标分析
- 自动化报告生成
- RESTful API 服务
- Web Dashboard 可视化

## 安装

```bash
pip install -r requirements.txt
```

## 快速开始

### 本地开发

```bash
# 启动后端 API 服务
python -m uvicorn api.main:app --reload --port 8000

# 启动前端开发服务器
cd frontend && pnpm dev
```

### Docker 部署

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps
```

服务地址：
- 后端 API: http://localhost:8000
- 前端 Dashboard: http://localhost:3000

## 运行模式

### 每日分析

```bash
python main.py --mode daily
```

### 生成周报

```bash
python main.py --mode weekly
```

### 回测投资组合

```bash
python main.py --mode backtest --portfolio '{"600519.SH": 0.5, "000858.SH": 0.5}'
```

### 启动调度服务

```bash
python main.py --mode serve
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

### 组合

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/portfolio/list | 组合列表 |
| GET | /api/portfolio/{id} | 组合详情 |
| POST | /api/portfolio | 创建组合 |

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
| POST | /api/reports/generate/daily | 生成日报 |
| POST | /api/reports/generate/weekly | 生成周报 |

## 配置说明

编辑 `config.yaml` 自定义:
- 股票池
- 数据源
- AI模型参数
- 风控配置
- 报告格式
- 调度时间

## 环境变量

### 后端 (.env)

```bash
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DB=aiqrh
JWT_SECRET_KEY=your-secret-key
```

### 前端

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 项目结构

```
gupiao/
├── main.py              # 主入口
├── config.yaml          # 配置文件
├── requirements.txt     # 依赖
├── Dockerfile           # Docker 配置
├── docker-compose.yml   # 服务编排
├── core/
│   ├── engine.py        # 核心引擎
│   ├── models.py        # 数据模型
│   └── database.py      # 数据库连接
├── skills/
│   ├── skill_data/      # 数据采集
│   ├── skill_ai/        # 策略分析
│   ├── skill_risk/      # 风控模拟
│   ├── skill_report/    # 报告生成
│   └── skill_ops/       # 系统运维
├── api/                 # FastAPI 服务
│   ├── main.py
│   ├── auth.py
│   └── routes/
├── frontend/           # Next.js 前端
│   ├── app/
│   ├── components/
│   └── lib/
└── tests/               # 单元测试
```

## 测试

```bash
# 运行单元测试
pytest tests/ -v
```

## 技术栈

| 模块 | 技术 |
|------|------|
| 后端 | Python 3.10+, FastAPI |
| 数据库 | MongoDB |
| 前端 | Next.js 14, React 18, TypeScript |
| 图表 | Recharts |
| 容器 | Docker, Docker Compose |
