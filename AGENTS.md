# AI Quant Research Hub - 开发规范

## 开发环境

- Python 3.10+
- Windows/Linux

## 运行命令

```bash
# 安装依赖
pip install -r requirements.txt

# 每日分析
python main.py --mode daily

# 回测
python main.py --mode backtest

# 启动调度服务
python main.py --mode serve
```

## 代码检查

```bash
# 安装pre-commit
pip install pre-commit

# 运行检查
python -m py_compile main.py
python -m py_compile core/engine.py
```

## 目录结构

- `core/` - 核心引擎
- `skills/` - 功能模块
- `data/` - 数据存储
- `logs/` - 日志
- `reports/` - 报告输出
