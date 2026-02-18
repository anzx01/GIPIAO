# 快速启动指南

## 问题：网络连接失败

您看到的错误 `网络连接失败，请检查网络设置` 表示前端无法连接到后端服务。

## 解决方案

### 方法1: 使用启动脚本（推荐）

#### Windows用户
```bash
# 双击运行或在命令行执行
start-backend.bat
```

#### Linux/Mac用户
```bash
# 添加执行权限
chmod +x start-backend.sh

# 运行脚本
./start-backend.sh
```

### 方法2: 手动启动

#### 1. 打开新的终端窗口

#### 2. 进入项目目录
```bash
cd g:\myaist\gupiao
```

#### 3. 启动后端服务
```bash
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8001
```

#### 4. 等待看到以下输出
```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 方法3: 检查是否已经运行

如果后端已经在运行但前端连接不上，可能是端口或地址配置问题。

#### 测试后端连接
在浏览器中访问：
- http://127.0.0.1:8001/health
- http://localhost:8001/health

如果能看到 `{"status":"healthy"}`，说明后端正常运行。

## 常见问题

### 问题1: 端口被占用
```
ERROR: [Errno 10048] error while attempting to bind on address ('0.0.0.0', 8001)
```

**解决方案**:
```bash
# 查找占用8001端口的进程
netstat -ano | findstr :8001

# 结束进程（替换PID为实际进程ID）
taskkill /PID <PID> /F

# 或使用其他端口
python -m uvicorn api.main:app --reload --port 8002
```

### 问题2: 缺少依赖包
```
ModuleNotFoundError: No module named 'fastapi'
```

**解决方案**:
```bash
pip install -r requirements.txt
```

### 问题3: JWT密钥错误
```
ValueError: 检测到不安全的JWT密钥！
```

**解决方案**:
您的 `.env` 文件中已经设置了安全的JWT密钥，这个问题应该不会出现。

### 问题4: 前端连接错误地址

检查前端是否连接到正确的地址：

**文件**: `frontend/.env.local`（如果不存在则创建）
```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8001
```

然后重启前端：
```bash
cd frontend
npm run dev
# 或
pnpm dev
```

## 验证服务正常

### 1. 后端健康检查
```bash
curl http://127.0.0.1:8001/health
```

应该返回：
```json
{"status":"healthy"}
```

### 2. 测试股票API
```bash
curl http://127.0.0.1:8001/api/stocks/list
```

### 3. 在浏览器中测试
访问：http://127.0.0.1:8001

应该看到API信息页面。

## 完整启动流程

### 终端1 - 启动后端
```bash
cd g:\myaist\gupiao
python -m uvicorn api.main:app --reload --port 8001
```

### 终端2 - 启动前端
```bash
cd g:\myaist\gupiao\frontend
pnpm dev
```

### 访问应用
- 前端: http://localhost:3000
- 后端: http://127.0.0.1:8001
- API文档: http://127.0.0.1:8001/docs

## 调试技巧

### 查看后端日志
```bash
tail -f logs/app.log
```

### 查看前端控制台
按 F12 打开浏览器开发者工具，查看 Console 和 Network 标签。

### 测试网络连接
```bash
# Windows
ping 127.0.0.1

# 测试端口
telnet 127.0.0.1 8001
```

## 需要帮助？

如果问题仍然存在：
1. 确保后端服务正在运行（终端中应该看到 uvicorn 的输出）
2. 检查防火墙是否阻止了8001端口
3. 尝试使用 `localhost` 而不是 `127.0.0.1`
4. 查看后端日志文件 `logs/app.log`
5. 检查浏览器控制台的详细错误信息
