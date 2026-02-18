"""手动运行股票分析并保存评分数据"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.engine import QuantEngine

if __name__ == "__main__":
    print("正在初始化引擎...")
    engine = QuantEngine("config.yaml")

    print("开始运行每日分析...")
    result = engine.run_daily_analysis()

    if result["status"] == "success":
        print(f"✓ 分析完成！耗时: {result.get('duration', 0)}秒")
        scores = result.get("data", {}).get("stock_scores", [])
        print(f"✓ 生成了 {len(scores)} 条评分数据")
        print("\n评分数据已保存到 data/scores/ 目录")
    else:
        print(f"✗ 分析失败: {result.get('error')}")
