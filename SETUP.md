# AI Quant Research Hub - 运行配置指南

## 1. 环境要求

- Python 3.10+
- Node.js 18+
- MongoDB 4.4+

## 2. 安装依赖

### 后端依赖
```bash
cd g:\myaist\gupiao
pip install -r requirements.txt
```

### 前端依赖
```bash
cd g:\myaist\gupiao\frontend
pnpm install
```

## 3. 配置文件

### 3.1 创建 .env 文件

从 `.env.example` 复制并创建 `.env` 文件：

```bash
cd g:\myaist\gupiao
copy .env.example .env
```

### 3.2 配置 MongoDB

#### 方式一：使用本地 MongoDB（需要安装）

1. 下载并安装 MongoDB：https://www.mongodb.com/try/download/community
2. 启动 MongoDB 服务：
   ```bash
   # Windows
   net start MongoDB
   ```

#### 方式二：使用 Docker（推荐）

```bash
# 启动 MongoDB 容器
docker run -d --name mongodb -p 27017:27017 mongo:latest

# 或者使用 docker-compose
docker-compose up -d mongodb
```

#### 方式三：使用 MongoDB Atlas（云端）

1. 注册账号：https://www.mongodb.com/cloud/atlas
2. 创建免费集群
3. 获取连接字符串，更新 `.env` 文件：
   ```
   MONGO_CONNECTION=mongodb+srv://username:password@cluster.mongodb.net/aiqrh
   ```

### 3.3 配置 JWT 密钥

在 `.env` 文件中设置安全的 JWT 密钥：

```env
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production-123456789
```

### 3.4 配置数据源

项目默认使用 **AkShare**（无需 API Key），如需使用其他数据源：

#### Tushare（推荐用于生产环境）

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

#### AkShare（默认，免费）

无需配置，开箱即用。

## 4. 启动服务

### 4.1 启动后端

```bash
# PowerShell
cd g:\myaist\gupiao
python -m uvicorn api.main:app --reload --port 8001

# 或使用 CMD
cd g:\myaist\gupiao
python -m uvicorn api.main:app --reload --port 8001
```

### 4.2 启动前端

```bash
# PowerShell
cd g:\myaist\gupiao\frontend
pnpm dev

# 或使用 CMD
cd g:\myaist\gupiao\frontend
pnpm dev
```

## 5. 访问应用

- 前端界面：http://localhost:3000
- 后端 API：http://localhost:8001
- API 文档：http://localhost:8001/docs

## 6. 可选配置

### 6.1 配置定时任务

在 `config.yaml` 中配置定时任务：

```yaml
scheduler:
  enabled: true
  jobs:
    - id: "daily_analysis"
      trigger: "cron"
      hour: 9
      minute: 0
```

### 6.2 配置日志级别

在 `.env` 中设置：

```env
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR
```

### 6.3 配置数据目录

在 `.env` 中设置：

```env
DATA_DIR=data
```

确保目录存在：
```bash
mkdir data
mkdir reports
mkdir logs
```

## 7. 故障排查

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
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或使用阿里云镜像
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

## 8. 生产环境部署

### 使用 Docker Compose

```bash
docker-compose up -d
```

### 手动部署

1. 使用 Gunicorn 启动后端：
   ```bash
   gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
   ```

2. 构建前端：
   ```bash
   cd frontend
   pnpm build
   pnpm start
   ```

3. 使用 Nginx 反向代理

## 9. 数据初始化

首次运行时，系统会自动：

1. 创建 MongoDB 数据库和集合
2. 初始化默认用户（如需要）
3. 抓取初始股票数据

## 10. 安全建议

- 修改默认的 JWT 密钥
- 使用强密码
- 配置防火墙规则
- 定期备份数据库
- 使用 HTTPS（生产环境）
