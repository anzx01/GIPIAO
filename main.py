"""
AI Quant Research Hub (AIQRH) - Main Entry
量化研究平台主程序
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.engine import QuantEngine


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='AI Quant Research Hub - 量化研究平台'
    )
    
    parser.add_argument(
        '--mode',
        choices=['daily', 'weekly', 'backtest', 'serve'],
        default='daily',
        help='运行模式'
    )
    
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='配置文件路径'
    )
    
    parser.add_argument(
        '--stocks',
        nargs='+',
        help='指定股票代码'
    )
    
    parser.add_argument(
        '--portfolio',
        type=str,
        help='投资组合 (JSON格式，如: {"600519.SH": 0.3, "000858.SH": 0.7})'
    )
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("AI Quant Research Hub")
    print("AI 量化研究平台")
    print("=" * 50)
    
    engine = QuantEngine(args.config)
    
    if args.mode == 'daily':
        print("\n执行每日分析...")
        result = engine.run_daily_analysis()
        
        if result['status'] == 'success':
            print(f"\n✓ 每日分析完成")
            print(f"  耗时: {result.get('duration', 0)}秒")
            print(f"  报告: {result.get('data', {}).get('report_path', 'N/A')}")
        else:
            print(f"\n✗ 分析失败: {result.get('error', 'Unknown error')}")
            sys.exit(1)
    
    elif args.mode == 'weekly':
        print("\n生成周报...")
        result = engine.run_weekly_report()
        
        if result['status'] == 'success':
            print(f"\n✓ 周报生成完成")
            print(f"  耗时: {result.get('duration', 0)}秒")
        else:
            print(f"\n✗ 周报生成失败: {result.get('error')}")
            sys.exit(1)
    
    elif args.mode == 'backtest':
        import json
        
        if args.portfolio:
            portfolio = json.loads(args.portfolio)
        else:
            portfolio = {
                '600519.SH': 0.25,
                '000858.SH': 0.25,
                '601318.SH': 0.25,
                '600036.SH': 0.25
            }
        
        print(f"\n执行回测: {portfolio}")
        
        result = engine.backtest_portfolio(portfolio)
        
        print("\n回测结果:")
        print(f"  总收益率: {result.get('total_return', 0):.2f}%")
        print(f"  年化收益率: {result.get('annual_return', 0):.2f}%")
        print(f"  夏普比率: {result.get('sharpe_ratio', 0):.2f}")
        print(f"  最大回撤: {result.get('max_drawdown', 0):.2f}%")
        print(f"  波动率: {result.get('volatility', 0):.2f}%")
        print(f"  胜率: {result.get('win_rate', 0):.2f}%")
    
    elif args.mode == 'serve':
        print("\n启动服务模式...")
        engine.start()
        
        try:
            print("\n按 Ctrl+C 停止服务")
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n停止服务...")
            engine.stop()
    
    print("\n完成!")


if __name__ == '__main__':
    main()
