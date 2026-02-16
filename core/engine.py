import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import time

from skills.skill_data import StockDataFetcher, DataStorage, NewsFetcher
from skills.skill_ai import StockScorer, StrategyAnalyzer, FactorModel
from skills.skill_risk import BacktestEngine, RiskMetrics
from skills.skill_report import ReportGenerator, ChartGenerator
from skills.skill_ops import TaskScheduler, AppLogger


class QuantEngine:
    """AI量化研究引擎 - 核心"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        
        self.logger = AppLogger({
            'log_dir': self.config.get('logging', {}).get('file', 'logs').rsplit('/', 1)[0],
            'level': self.config.get('logging', {}).get('level', 'INFO')
        }).get_logger()
        
        self._init_components()
        
        self.scheduler = TaskScheduler(self.config.get('scheduler', {}))
        
        self.logger.info("AI Quant Engine 初始化完成")
    
    def _load_config(self, config_path: str) -> dict:
        """加载配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"配置加载失败: {e}")
            return {}
    
    def _init_components(self):
        """初始化组件"""
        
        self.fetcher = StockDataFetcher(self.config.get('data_source', {}))
        self.storage = DataStorage(self.config.get('data_dir', 'data'))
        self.news_fetcher = NewsFetcher()
        
        self.scorer = StockScorer(self.config.get('ai_model', {}))
        self.analyzer = StrategyAnalyzer()
        self.factor_model = FactorModel()
        
        self.backtest = BacktestEngine(self.config.get('risk', {}))
        self.risk_metrics = RiskMetrics()
        
        self.report_gen = ReportGenerator(self.config.get('report', {}))
        self.chart_gen = ChartGenerator()
        
        self.logger.info("所有组件初始化完成")
    
    def run_daily_analysis(self) -> Dict:
        """运行每日分析"""
        start_time = time.time()
        self.logger.info("开始每日分析")
        
        result = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'data': {}
        }
        
        try:
            stock_list = self._get_stock_list()
            
            self.logger.info(f"分析股票列表: {stock_list}")
            
            self.logger.info("步骤1: 抓取行情数据")
            price_data = self.fetcher.fetch_price_data(stock_list)
            
            for code, df in price_data.items():
                df = self.fetcher.calculate_technical_indicators(df)
                self.storage.save_price_data(code, df)
            
            self.logger.info("步骤2: 抓取财务数据")
            financial_data = self.fetcher.fetch_financial_data(stock_list)
            
            for code, data in financial_data.items():
                self.storage.save_financial_data(code, data)
            
            self.logger.info("步骤3: 抓取新闻数据")
            news_data = self.news_fetcher.fetch_news(stock_list)
            
            for code, news in news_data.items():
                self.storage.save_news(code, news)
            
            self.logger.info("步骤4: 股票评分")
            scores = self.scorer.score_stocks(price_data, financial_data, news_data)
            result['data']['stock_scores'] = scores.to_dict('records') if not scores.empty else []
            
            self.logger.info("步骤5: 策略分析")
            strategy = self.analyzer.analyze_strategy(price_data, stock_list)
            result['data']['strategy_analysis'] = strategy
            
            self.logger.info("步骤6: 风控模拟")
            top_stocks = self.scorer.get_top_stocks(scores, 5)
            
            if top_stocks:
                portfolio = {code: 1/len(top_stocks) for code in top_stocks}
                backtest_result = self.backtest.run_backtest(price_data, portfolio)
                result['data']['backtest_result'] = backtest_result
                result['data']['risk_metrics'] = {
                    'total_return': backtest_result.get('total_return', 0),
                    'annual_return': backtest_result.get('annual_return', 0),
                    'sharpe_ratio': backtest_result.get('sharpe_ratio', 0),
                    'max_drawdown': backtest_result.get('max_drawdown', 0),
                    'volatility': backtest_result.get('volatility', 0),
                    'win_rate': backtest_result.get('win_rate', 0)
                }
            
            self.logger.info("步骤7: 市场概览")
            market_summary = self.fetcher.fetch_market_summary()
            result['data']['market_summary'] = market_summary
            
            self.logger.info("步骤8: 生成报告")
            report_path = self.report_gen.generate_daily_report(result['data'])
            result['data']['report_path'] = report_path
            
            self.logger.info("步骤9: 生成图表")
            self.chart_gen.create_dashboard({
                'price_data': price_data,
                'stock_scores': scores,
                'backtest_result': result['data'].get('backtest_result'),
                'risk_metrics': result['data'].get('risk_metrics')
            })
            
            duration = time.time() - start_time
            result['duration'] = round(duration, 2)
            
            self.logger.info(f"每日分析完成，耗时: {duration:.2f}秒")
            
        except Exception as e:
            self.logger.error(f"每日分析失败: {e}")
            result['status'] = 'error'
            result['error'] = str(e)
        
        return result
    
    def run_weekly_report(self) -> Dict:
        """运行周报"""
        start_time = time.time()
        self.logger.info("开始生成周报")
        
        result = {
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            stock_list = self._get_stock_list()
            
            price_data = {}
            for code in stock_list:
                df = self.storage.load_all_price_data(code)
                if not df.empty:
                    price_data[code] = df
            
            financial_data = {}
            for code in stock_list:
                data = self.storage.load_financial_data(code)
                if data:
                    financial_data[code] = data
            
            news_data = {}
            for code in stock_list:
                news = self.storage.load_news(code)
                if news:
                    news_data[code] = news
            
            scores = self.scorer.score_stocks(price_data, financial_data, news_data)
            result['data'] = {
                'stock_scores': scores.to_dict('records') if not scores.empty else []
            }
            
            report_path = self.report_gen.generate_weekly_report(result['data'])
            result['report_path'] = report_path
            
            duration = time.time() - start_time
            result['duration'] = round(duration, 2)
            
            self.logger.info(f"周报生成完成，耗时: {duration:.2f}秒")
            
        except Exception as e:
            self.logger.error(f"周报生成失败: {e}")
            result['status'] = 'error'
            result['error'] = str(e)
        
        return result
    
    def backtest_portfolio(self, portfolio: Dict[str, float],
                          start_date: str = None,
                          end_date: str = None) -> Dict:
        """回测投资组合"""
        
        stock_list = list(portfolio.keys())
        
        price_data = self.fetcher.fetch_price_data(stock_list)
        
        result = self.backtest.run_backtest(
            price_data, 
            portfolio,
            start_date,
            end_date
        )
        
        return result
    
    def optimize_portfolio(self, stock_list: List[str]) -> Dict:
        """优化投资组合"""
        
        price_data = self.fetcher.fetch_price_data(stock_list)
        
        result = self.analyzer.optimize_weights(price_data, stock_list)
        
        return result
    
    def _get_stock_list(self) -> List[str]:
        """获取股票列表"""
        
        pool = self.config.get('stock_pool', {})
        
        stock_list = pool.get('stocks', [])
        
        indices = pool.get('indices', [])
        
        return stock_list if stock_list else ['600519.SH', '000858.SH', '601318.SH']
    
    def setup_scheduler(self):
        """设置调度任务"""
        
        scheduler_config = self.config.get('scheduler', {})
        
        if not scheduler_config.get('enabled', True):
            return
        
        daily_time = self.config.get('report', {}).get('daily_schedule', '09:00')
        hour, minute = map(int, daily_time.split(':'))
        
        self.scheduler.add_job(
            'daily_analysis',
            self.run_daily_analysis,
            trigger='cron',
            hour=hour,
            minute=minute
        )
        
        self.logger.info(f"调度任务已设置: 每日 {daily_time}")
    
    def start(self):
        """启动引擎"""
        self.setup_scheduler()
        self.scheduler.start()
        self.logger.info("引擎已启动")
    
    def stop(self):
        """停止引擎"""
        self.scheduler.stop()
        self.logger.info("引擎已停止")
