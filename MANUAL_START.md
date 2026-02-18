# 手动启动后端服务

## 问题说明
自动启动遇到端口权限问题。需要您手动启动后端服务。

## 启动步骤

### 方法1: 使用启动脚本（推荐）

**双击运行**：
```
g:\myaist\gupiao\start-backend.bat
```

### 方法2: 手动命令行启动

1. **打开新的命令提示符窗口**（以管理员身份运行）

2. **进入项目目录**：
```bash
cd g:\myaist\gupiao
```

3. **启动后端服务**：
```bash
C:\Python314\python.exe -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8001
```

4. **等待看到以下输出**：
```
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Application startup complete.
```

## 验证服务

### 在浏览器中访问：
- http://127.0.0.1:8001/health

应该看到：
```json
{"status":"healthy"}
```

## 前端配置

前端已配置为连接 http://127.0.0.1:8001

**文件**: `frontend/.env.local`
```
NEXT_PUBLIC_API_URL=http://127.0.0.1:8001
```

## 完整流程

### 终端1 - 后端
```bash
cd g:\myaist\gupiao
C:\Python314\python.exe -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8001
```

### 终端2 - 前端
```bash
cd g:\myaist\gupiao\frontend
pnpm dev
```

### 访问应用
- 前端: http://localhost:3000
- 后端: http://127.0.0.1:8001

## 故障排查

### 如果端口被占用

查找占用进程：
```bash
netstat -ano | findstr :8001
```

结束进程（替换PID）：
```bash
taskkill /F /PID <进程ID>
```

### 如果权限不足

以管理员身份运行命令提示符：
1. 搜索 "cmd"
2. 右键 -> "以管理员身份运行"
3. 执行启动命令

## 测试股票查询

启动成功后：
1. 访问 http://localhost:3000
2. 搜索 `600519`
3. 应该能看到贵州茅台的数据

---

**请手动启动后端服务，然后重启前端即可使用！**
