import numpy as np
import pandas as pd
from typing import Dict, List, Optional
import loguru


class ChartGenerator:
    """图表生成器"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.logger = loguru.logger
        
        self._try_import_plotly()
    
    def _try_import_plotly(self):
        """尝试导入plotly"""
        try:
            import plotly.graph_objects as go
            import plotly.express as px
            from plotly.subplots import make_subplots
            
            self.go = go
            self.px = px
            self.make_subplots = make_subplots
            self.has_plotly = True
            
        except ImportError:
            self.has_plotly = False
            self.logger.warning("plotly未安装，将使用matplotlib")
            
            try:
                import matplotlib.pyplot as plt
                import matplotlib
                matplotlib.use('Agg')
                self.plt = plt
                self.has_mpl = True
            except ImportError:
                self.has_mpl = False
    
    def plot_price_trend(self, price_data: Dict[str, pd.DataFrame],
                        stock_codes: List[str] = None) -> str:
        """绘制价格趋势图"""
        
        if not self.has_plotly and not self.has_mpl:
            return None
        
        if stock_codes is None:
            stock_codes = list(price_data.keys())[:5]
        
        if self.has_plotly:
            return self._plot_price_plotly(price_data, stock_codes)
        else:
            return self._plot_price_mpl(price_data, stock_codes)
    
    def _plot_price_plotly(self, price_data: Dict[str, pd.DataFrame],
                          stock_codes: List[str]) -> str:
        """使用plotly绘制"""
        
        fig = self.make_subplots(
            rows=1, cols=1,
            subplot_titles=('股价走势',),
            vertical_spacing=0.1
        )
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        
        for i, code in enumerate(stock_codes):
            if code in price_data:
                df = price_data[code]
                
                fig.add_trace(
                    self.go.Scatter(
                        x=df['date'],
                        y=df['close'],
                        mode='lines',
                        name=code,
                        line=dict(color=colors[i % len(colors)], width=2)
                    ),
                    row=1, col=1
                )
        
        fig.update_layout(
            title='股票价格走势',
            xaxis_title='日期',
            yaxis_title='价格',
            height=400,
            showlegend=True,
            template='plotly_white'
        )
        
        output_path = 'data/charts/price_trend.html'
        import os
        os.makedirs('data/charts', exist_ok=True)
        
        fig.write_html(output_path)
        
        return output_path
    
    def _plot_price_mpl(self, price_data: Dict[str, pd.DataFrame],
                       stock_codes: List[str]) -> str:
        """使用matplotlib绘制"""
        
        import matplotlib.pyplot as plt
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        
        for i, code in enumerate(stock_codes):
            if code in price_data:
                df = price_data[code]
                ax.plot(df['date'], df['close'], 
                       label=code, color=colors[i % len(colors)])
        
        ax.set_title('股票价格走势')
        ax.set_xlabel('日期')
        ax.set_ylabel('价格')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        output_path = 'data/charts/price_trend.png'
        import os
        os.makedirs('data/charts', exist_ok=True)
        
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def plot_stock_scores(self, scores_df: pd.DataFrame, top_n: int = 10) -> str:
        """绘制股票评分图"""
        
        if scores_df.empty:
            return None
        
        df_top = scores_df.head(top_n)
        
        if self.has_plotly:
            fig = self.go.Figure()
            
            fig.add_trace(self.go.Bar(
                x=df_top['code'],
                y=df_top['total_score'],
                marker_color=df_top['total_score'].apply(
                    lambda x: '#28a745' if x >= 70 else '#ffc107' if x >= 50 else '#dc3545'
                ),
                text=df_top['total_score'],
                textposition='outside'
            ))
            
            fig.update_layout(
                title=f'Top {top_n} 股票评分',
                xaxis_title='股票代码',
                yaxis_title='综合评分',
                height=400,
                template='plotly_white'
            )
            
            output_path = 'data/charts/stock_scores.html'
            import os
            os.makedirs('data/charts', exist_ok=True)
            
            fig.write_html(output_path)
            
            return output_path
        
        return None
    
    def plot_backtest_results(self, backtest_result: Dict) -> str:
        """绘制回测结果"""
        
        if not backtest_result or 'portfolio_values' not in backtest_result:
            return None
        
        values = backtest_result['portfolio_values']
        
        if not values:
            return None
        
        df = pd.DataFrame(values)
        
        if 'date' not in df.columns:
            return None
        
        if self.has_plotly:
            fig = self.make_subplots(
                rows=2, cols=2,
                subplot_titles=('组合价值', '收益率', '回撤', '收益分布'),
                vertical_spacing=0.15,
                horizontal_spacing=0.1
            )
            
            fig.add_trace(
                self.go.Scatter(
                    x=df['date'],
                    y=df['value'],
                    mode='lines',
                    name='组合价值',
                    line=dict(color='#1f77b4', width=2)
                ),
                row=1, col=1
            )
            
            if 'return' in df.columns:
                fig.add_trace(
                    self.go.Scatter(
                        x=df['date'],
                        y=df['return'] * 100,
                        mode='lines',
                        name='收益率(%)',
                        line=dict(color='#ff7f0e', width=1),
                        fill='tozeroy'
                    ),
                    row=1, col=2
                )
            
            df['cummax'] = df['value'].cummax()
            df['drawdown'] = (df['value'] - df['cummax']) / df['cummax'] * 100
            
            fig.add_trace(
                self.go.Scatter(
                    x=df['date'],
                    y=df['drawdown'],
                    mode='lines',
                    name='回撤(%)',
                    line=dict(color='#dc3545', width=1),
                    fill='tozeroy'
                ),
                row=2, col=1
            )
            
            if 'return' in df.columns:
                fig.add_trace(
                    self.go.Histogram(
                        x=df['return'] * 100,
                        name='收益分布',
                        marker_color='#2ca02c'
                    ),
                    row=2, col=2
                )
            
            fig.update_layout(
                height=600,
                showlegend=False,
                template='plotly_white'
            )
            
            output_path = 'data/charts/backtest_results.html'
            import os
            os.makedirs('data/charts', exist_ok=True)
            
            fig.write_html(output_path)
            
            return output_path
        
        return None
    
    def plot_risk_metrics(self, risk_metrics: Dict) -> str:
        """绘制风险指标仪表盘"""
        
        if not risk_metrics:
            return None
        
        if self.has_plotly:
            fig = self.make_subplots(
                rows=2, cols=3,
                subplot_titles=(
                    '年化收益率', '夏普比率', '最大回撤',
                    '波动率', '胜率', '风险等级'
                ),
                specs=[
                    [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
                    [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]
                ]
            )
            
            fig.add_trace(
                self.go.Indicator(
                    mode="gauge+number",
                    value=risk_metrics.get('annual_return', 0),
                    title={'text': "年化收益率(%)"},
                    gauge={'axis': {'range': [-50, 50]}}
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                self.go.Indicator(
                    mode="gauge+number",
                    value=risk_metrics.get('sharpe_ratio', 0),
                    title={'text': "夏普比率"},
                    gauge={'axis': {'range': [0, 3]}}
                ),
                row=1, col=2
            )
            
            fig.add_trace(
                self.go.Indicator(
                    mode="gauge+number",
                    value=risk_metrics.get('max_drawdown', 0),
                    title={'text': "最大回撤(%)"},
                    gauge={'axis': {'range': [0, 100]}}
                ),
                row=1, col=3
            )
            
            fig.add_trace(
                self.go.Indicator(
                    mode="gauge+number",
                    value=risk_metrics.get('volatility', 0),
                    title={'text': "波动率(%)"},
                    gauge={'axis': {'range': [0, 50]}}
                ),
                row=2, col=1
            )
            
            fig.add_trace(
                self.go.Indicator(
                    mode="gauge+number",
                    value=risk_metrics.get('win_rate', 0),
                    title={'text': "胜率(%)"},
                    gauge={'axis': {'range': [0, 100]}}
                ),
                row=2, col=2
            )
            
            fig.update_layout(
                height=600,
                template='plotly_white'
            )
            
            output_path = 'data/charts/risk_metrics.html'
            import os
            os.makedirs('data/charts', exist_ok=True)
            
            fig.write_html(output_path)
            
            return output_path
        
        return None
    
    def create_dashboard(self, data: Dict) -> str:
        """创建综合仪表盘"""
        
        if not self.has_plotly:
            return None
        
        import os
        os.makedirs('data/charts', exist_ok=True)
        
        self.plot_price_trend(data.get('price_data', {}))
        self.plot_stock_scores(data.get('stock_scores', pd.DataFrame()))
        self.plot_backtest_results(data.get('backtest_result', {}))
        self.plot_risk_metrics(data.get('risk_metrics', {}))
        
        return 'data/charts/'
