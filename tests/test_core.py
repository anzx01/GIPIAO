import pytest
from datetime import datetime
import pandas as pd
import numpy as np


class TestStockScorer:
    """股票评分器测试"""
    
    def test_score_pe_under_10(self):
        from skills.skill_ai.scorer import StockScorer
        scorer = StockScorer()
        
        score = scorer._score_pe(8)
        assert score == 100
    
    def test_score_pe_10_to_20(self):
        from skills.skill_ai.scorer import StockScorer
        scorer = StockScorer()
        
        score = scorer._score_pe(15)
        assert score == 80
    
    def test_score_pe_over_50(self):
        from skills.skill_ai.scorer import StockScorer
        scorer = StockScorer()
        
        score = scorer._score_pe(60)
        assert score == 20
    
    def test_score_pe_none(self):
        from skills.skill_ai.scorer import StockScorer
        scorer = StockScorer()
        
        score = scorer._score_pe(None)
        assert score == 50
    
    def test_score_pb_under_1(self):
        from skills.skill_ai.scorer import StockScorer
        scorer = StockScorer()
        
        score = scorer._score_pb(0.8)
        assert score == 100
    
    def test_score_roe_high(self):
        from skills.skill_ai.scorer import StockScorer
        scorer = StockScorer()
        
        score = scorer._score_roe(28)
        assert score == 100
    
    def test_score_roe_low(self):
        from skills.skill_ai.scorer import StockScorer
        scorer = StockScorer()
        
        score = scorer._score_roe(3)
        assert score == 20
    
    def test_get_top_stocks(self):
        from skills.skill_ai.scorer import StockScorer
        scorer = StockScorer()
        
        df = pd.DataFrame({
            'code': ['600519.SH', '000858.SH', '601318.SH'],
            'total_score': [85, 75, 65]
        })
        
        top = scorer.get_top_stocks(df, 2)
        assert len(top) == 2
        assert '600519.SH' in top
    
    def test_generate_recommendation_buy(self):
        from skills.skill_ai.scorer import StockScorer
        scorer = StockScorer()
        
        rec = scorer.generate_recommendation('600519.SH', 85)
        assert '买入' in rec
    
    def test_generate_recommendation_sell(self):
        from skills.skill_ai.scorer import StockScorer
        scorer = StockScorer()
        
        rec = scorer.generate_recommendation('600519.SH', 30)
        assert '卖出' in rec


class TestBacktestEngine:
    """回测引擎测试"""
    
    def test_empty_portfolio(self):
        from skills.skill_risk.backtest import BacktestEngine
        
        engine = BacktestEngine()
        result = engine.run_backtest({}, {})
        
        assert result['total_return'] == 0
    
    def test_calculate_sharpe(self):
        from skills.skill_risk.backtest import BacktestEngine
        
        engine = BacktestEngine()
        returns = np.array([0.01, -0.005, 0.015, 0.008, -0.002])
        
        sharpe = engine._calculate_sharpe(returns)
        assert isinstance(sharpe, float)
    
    def test_calculate_sortino(self):
        from skills.skill_risk.backtest import BacktestEngine
        
        engine = BacktestEngine()
        returns = np.array([0.01, -0.005, 0.015, 0.008, -0.002])
        
        sortino = engine._calculate_sortino(returns)
        assert isinstance(sortino, float)
    
    def test_compare_strategies(self):
        from skills.skill_risk.backtest import BacktestEngine
        
        engine = BacktestEngine()
        
        results = [
            {'name': 'Strategy 1', 'total_return': 10, 'annual_return': 10,
             'max_drawdown': 5, 'sharpe_ratio': 1.5, 'win_rate': 60, 'volatility': 12},
            {'name': 'Strategy 2', 'total_return': 15, 'annual_return': 15,
             'max_drawdown': 8, 'sharpe_ratio': 1.2, 'win_rate': 55, 'volatility': 15}
        ]
        
        df = engine.compare_strategies(results)
        
        assert not df.empty
        assert len(df) == 2


class TestDataFetcher:
    """数据获取器测试"""
    
    def test_calculate_technical_indicators(self):
        from skills.skill_data.fetcher import StockDataFetcher
        
        fetcher = StockDataFetcher()
        
        dates = pd.date_range('2023-01-01', periods=30, freq='D')
        df = pd.DataFrame({
            'date': dates,
            'close': 100 + np.cumsum(np.random.randn(30) * 2),
            'volume': np.random.randint(1000000, 5000000, 30)
        })
        
        result = fetcher.calculate_technical_indicators(df)
        
        assert 'ma5' in result.columns
        assert 'ma10' in result.columns
        assert 'ma20' in result.columns
        assert 'rsi' in result.columns
        assert 'macd' in result.columns
    
    def test_generate_mock_data(self):
        from skills.skill_data.fetcher import StockDataFetcher
        
        fetcher = StockDataFetcher()
        
        df = fetcher._generate_mock_data('600519.SH', '20230101', '20231231')
        
        assert not df.empty
        assert 'close' in df.columns
        assert 'volume' in df.columns
    
    def test_generate_mock_financial(self):
        from skills.skill_data.fetcher import StockDataFetcher
        
        fetcher = StockDataFetcher()
        
        data = fetcher._generate_mock_financial('600519.SH')
        
        assert 'pe' in data
        assert 'pb' in data
        assert 'roe' in data
        assert data['pe'] > 0


class TestReportGenerator:
    """报告生成器测试"""
    
    def test_generate_json_report(self):
        import os
        import tempfile
        from skills.skill_report.generator import ReportGenerator
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {'output_dir': tmpdir}
            generator = ReportGenerator(config)
            
            data = {
                'stock_scores': [
                    {'code': '600519.SH', 'total_score': 85}
                ],
                'risk_metrics': {
                    'total_return': 10.5,
                    'sharpe_ratio': 1.2
                }
            }
            
            path = generator.generate_json_report(data)
            
            assert os.path.exists(path)
            
            with open(path, 'r') as f:
                content = f.read()
                assert '600519.SH' in content
    
    def test_generate_html_report(self):
        import tempfile
        from skills.skill_report.generator import ReportGenerator
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {'output_dir': tmpdir}
            generator = ReportGenerator(config)
            
            data = {
                'stock_scores': [
                    {'code': '600519.SH', 'total_score': 85, 'rank': 1,
                     'pe_score': 80, 'momentum_score': 85, 'roe_score': 90}
                ],
                'risk_metrics': {
                    'total_return': 10.5,
                    'annual_return': 12.0,
                    'sharpe_ratio': 1.2,
                    'max_drawdown': 5.0,
                    'volatility': 15.0,
                    'win_rate': 60.0
                },
                'market_summary': {
                    'total_stocks': 5000,
                    'up_count': 2000,
                    'down_count': 2500,
                    'flat_count': 500
                }
            }
            
            path = generator.generate_daily_report(data)
            
            assert os.path.exists(path)
            assert path.endswith('.html')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
