# 🔧 后端启动问题解决方案

## 问题诊断
遇到 `WinError 10013` 错误，这是Windows端口权限问题。

## ✅ 解决方案（按顺序尝试）

### 方案1: 以管理员身份运行（推荐）

1. **右键点击** `start-backend.bat`
2. 选择 **"以管理员身份运行"**
3. 等待看到 "Application startup complete"

### 方案2: 使用命令提示符（管理员）

1. **按 Win+X**，选择 **"Windows PowerShell (管理员)"** 或 **"命令提示符 (管理员)"**

2. **执行以下命令**：
```bash
cd g:\myaist\gupiao
C:\Python314\python.exe -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8001
```

3. **等待启动成功**，看到：
```
INFO:     Uvicorn running on http://127.0.0.1:8001
INFO:     Application startup complete.
```

### 方案3: 使用不同端口

如果8001端口确实被占用，使用8003端口：

```bash
cd g:\myaist\gupiao
C:\Python314\python.exe -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8003
```

然后修改前端配置：
```bash
# 编辑 frontend/.env.local
NEXT_PUBLIC_API_URL=http://127.0.0.1:8003
```

### 方案4: 检查并清理占用端口的程序

```bash
# 查找占用8001端口的程序
netstat -ano | findstr :8001

# 如果有输出，记下最后一列的PID，然后结束进程
taskkill /F /PID <进程ID>
```

## 🎯 推荐操作流程

### 第1步：以管理员身份启动后端

**右键点击** → **以管理员身份运行**：
```
g:\myaist\gupiao\start-backend.bat
```

### 第2步：验证后端运行

在浏览器访问：
```
http://127.0.0.1:8001/health
```

应该看到：
```json
{"status":"healthy"}
```

### 第3步：重启前端

```bash
cd g:\myaist\gupiao\frontend
pnpm dev
```

### 第4步：测试功能

1. 访问 http://localhost:3000
2. 搜索股票代码 `600519`
3. 查看数据

## 📋 完整的启动检查清单

- [ ] 以管理员身份运行命令提示符
- [ ] 进入项目目录 `cd g:\myaist\gupiao`
- [ ] 启动后端服务
- [ ] 看到 "Application startup complete" 消息
- [ ] 浏览器测试 http://127.0.0.1:8001/health
- [ ] 重启前端服务
- [ ] 测试股票查询功能

## ⚠️ 常见问题

### Q1: 为什么需要管理员权限？
A: Windows对某些端口（特别是低于1024的端口）有权限限制。虽然8001不在这个范围，但某些安全软件可能会限制端口绑定。

### Q2: 如何确认后端真的在运行？
A:
1. 命令行窗口应该保持打开，显示日志
2. 浏览器访问 http://127.0.0.1:8001/health 返回 `{"status":"healthy"}`
3. `netstat -ano | findstr :8001` 应该有输出

### Q3: 前端连接不上后端怎么办？
A:
1. 确认后端正在运行
2. 检查 `frontend/.env.local` 中的 API 地址
3. 重启前端服务
4. 清除浏览器缓存

### Q4: 可以用其他端口吗？
A: 可以！使用任何未被占用的端口（如8003、8080等），记得同步修改前端配置。

## 🔍 调试技巧

### 查看详细错误日志
```bash
cd g:\myaist\gupiao
C:\Python314\python.exe -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8001 --log-level debug
```

### 测试Python环境
```bash
C:\Python314\python.exe -c "import fastapi; print('FastAPI OK')"
```

### 检查防火墙
确保Windows防火墙允许Python访问网络。

## 📞 如果仍然无法启动

请提供以下信息：
1. 完整的错误消息
2. `netstat -ano | findstr :8001` 的输出
3. 是否以管理员身份运行
4. 杀毒软件/防火墙设置

---

## 🎉 成功标志

当您看到以下内容时，表示启动成功：

```
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**现在请以管理员身份运行 start-backend.bat！**
