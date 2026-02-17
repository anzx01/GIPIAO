"""
PDF报告生成模块
"""

from typing import Dict, List, Any
from datetime import datetime
from jinja2 import Template
from weasyprint import HTML, CSS
import os


class PDFGenerator:
    def __init__(self, template_dir: str = "templates"):
        self.template_dir = template_dir
        self.ensure_template_dir()
    
    def ensure_template_dir(self):
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir)
    
    def generate_daily_report(self, data: Dict[str, Any]) -> str:
        template_content = self._get_daily_report_template()
        template = Template(template_content)
        
        html_content = template.render(
            title=f"AI量化分析日报 - {data.get('date', datetime.now().strftime('%Y-%m-%d'))}",
            date=data.get('date', datetime.now().strftime('%Y-%m-%d')),
            summary=data.get('summary', ''),
            highlights=data.get('highlights', []),
            market_data=data.get('market_data', {}),
            top_stocks=data.get('top_stocks', []),
            sectors=data.get('sectors', []),
            generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        css_content = self._get_report_css()
        
        output_path = f"reports/daily_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        os.makedirs("reports", exist_ok=True)
        
        HTML(string=html_content).write_pdf(
            output_path,
            stylesheets=[CSS(string=css_content)]
        )
        
        return output_path
    
    def generate_weekly_report(self, data: Dict[str, Any]) -> str:
        template_content = self._get_weekly_report_template()
        template = Template(template_content)
        
        html_content = template.render(
            title=f"AI量化分析周报 - {data.get('week', '')}",
            week=data.get('week', ''),
            summary=data.get('summary', ''),
            highlights=data.get('highlights', []),
            market_summary=data.get('market_summary', {}),
            top_stocks=data.get('top_stocks', []),
            sector_performance=data.get('sector_performance', []),
            risk_analysis=data.get('risk_analysis', {}),
            generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        css_content = self._get_report_css()
        
        output_path = f"reports/weekly_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        os.makedirs("reports", exist_ok=True)
        
        HTML(string=html_content).write_pdf(
            output_path,
            stylesheets=[CSS(string=css_content)]
        )
        
        return output_path
    
    def generate_backtest_report(self, data: Dict[str, Any]) -> str:
        template_content = self._get_backtest_report_template()
        template = Template(template_content)
        
        html_content = template.render(
            title=f"回测报告 - {data.get('strategy_name', '策略')}",
            strategy_name=data.get('strategy_name', '策略'),
            backtest_period=f"{data.get('start_date', '')} 至 {data.get('end_date', '')}",
            summary=data.get('summary', ''),
            metrics=data.get('metrics', {}),
            portfolio=data.get('portfolio', {}),
            performance=data.get('performance', {}),
            trades=data.get('trades', [])[:20],
            generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        css_content = self._get_report_css()
        
        output_path = f"reports/backtest_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        os.makedirs("reports", exist_ok=True)
        
        HTML(string=html_content).write_pdf(
            output_path,
            stylesheets=[CSS(string=css_content)]
        )
        
        return output_path
    
    def _get_daily_report_template(self) -> str:
        return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
</head>
<body>
    <div class="header">
        <h1>{{ title }}</h1>
        <p class="date">生成时间: {{ generated_at }}</p>
    </div>
    
    <div class="section">
        <h2>市场摘要</h2>
        <p>{{ summary }}</p>
    </div>
    
    <div class="section">
        <h2>市场亮点</h2>
        <div class="highlights">
            {% for highlight in highlights %}
            <div class="highlight-item">
                <span class="highlight-title">{{ highlight.title }}</span>
                <span class="highlight-value">{{ highlight.value }}</span>
            </div>
            {% endfor %}
        </div>
    </div>
    
    <div class="section">
        <h2>市场数据</h2>
        <table class="data-table">
            <tr>
                <td>上证指数</td>
                <td>{{ market_data.sh_index|default('--') }}</td>
            </tr>
            <tr>
                <td>深证成指</td>
                <td>{{ market_data.sz_index|default('--') }}</td>
            </tr>
            <tr>
                <td>创业板指</td>
                <td>{{ market_data.cy_index|default('--') }}</td>
            </tr>
            <tr>
                <td>成交额</td>
                <td>{{ market_data.volume|default('--') }}</td>
            </tr>
        </table>
    </div>
    
    <div class="section">
        <h2>AI评分TOP10</h2>
        <table class="data-table">
            <thead>
                <tr>
                    <th>排名</th>
                    <th>代码</th>
                    <th>名称</th>
                    <th>评分</th>
                </tr>
            </thead>
            <tbody>
                {% for stock in top_stocks %}
                <tr>
                    <td>{{ loop.index }}</td>
                    <td>{{ stock.code }}</td>
                    <td>{{ stock.name }}</td>
                    <td>{{ stock.score|round(2) }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    
    <div class="section">
        <h2>板块表现</h2>
        <table class="data-table">
            <thead>
                <tr>
                    <th>板块</th>
                    <th>涨跌幅</th>
                    <th>热度</th>
                </tr>
            </thead>
            <tbody>
                {% for sector in sectors %}
                <tr>
                    <td>{{ sector.name }}</td>
                    <td>{{ sector.pct_change }}%</td>
                    <td>{{ sector.heat }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    
    <div class="footer">
        <p>AI量化研究平台 | 本报告由AI自动生成，仅供参考</p>
    </div>
</body>
</html>
"""
    
    def _get_weekly_report_template(self) -> str:
        return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
</head>
<body>
    <div class="header">
        <h1>{{ title }}</h1>
        <p class="date">生成时间: {{ generated_at }}</p>
    </div>
    
    <div class="section">
        <h2>本周摘要</h2>
        <p>{{ summary }}</p>
    </div>
    
    <div class="section">
        <h2>市场亮点</h2>
        <div class="highlights">
            {% for highlight in highlights %}
            <div class="highlight-item">
                <span class="highlight-title">{{ highlight.title }}</span>
                <span class="highlight-value">{{ highlight.value }}</span>
            </div>
            {% endfor %}
        </div>
    </div>
    
    <div class="section">
        <h2>市场概览</h2>
        <table class="data-table">
            <tr>
                <td>上证指数周涨跌</td>
                <td>{{ market_summary.sh_change|default('--') }}</td>
            </tr>
            <tr>
                <td>深证成指周涨跌</td>
                <td>{{ market_summary.sz_change|default('--') }}</td>
            </tr>
            <tr>
                <td>创业板指周涨跌</td>
                <td>{{ market_summary.cy_change|default('--') }}</td>
            </tr>
            <tr>
                <td>周均成交额</td>
                <td>{{ market_summary.avg_volume|default('--') }}</td>
            </tr>
        </table>
    </div>
    
    <div class="section">
        <h2>AI评分TOP10</h2>
        <table class="data-table">
            <thead>
                <tr>
                    <th>排名</th>
                    <th>代码</th>
                    <th>名称</th>
                    <th>评分</th>
                    <th>周涨跌</th>
                </tr>
            </thead>
            <tbody>
                {% for stock in top_stocks %}
                <tr>
                    <td>{{ loop.index }}</td>
                    <td>{{ stock.code }}</td>
                    <td>{{ stock.name }}</td>
                    <td>{{ stock.score|round(2) }}</td>
                    <td>{{ stock.weekly_change|default('--') }}%</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    
    <div class="section">
        <h2>板块表现</h2>
        <table class="data-table">
            <thead>
                <tr>
                    <th>板块</th>
                    <th>周涨跌</th>
                    <th>资金流入</th>
                </tr>
            </thead>
            <tbody>
                {% for sector in sector_performance %}
                <tr>
                    <td>{{ sector.name }}</td>
                    <td>{{ sector.weekly_change }}%</td>
                    <td>{{ sector.inflow|default('--') }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    
    <div class="section">
        <h2>风险分析</h2>
        <table class="data-table">
            <tr>
                <td>市场风险等级</td>
                <td>{{ risk_analysis.level|default('--') }}</td>
            </tr>
            <tr>
                <td>波动率</td>
                <td>{{ risk_analysis.volatility|default('--') }}</td>
            </tr>
            <tr>
                <td>最大回撤</td>
                <td>{{ risk_analysis.max_drawdown|default('--') }}</td>
            </tr>
        </table>
    </div>
    
    <div class="footer">
        <p>AI量化研究平台 | 本报告由AI自动生成，仅供参考</p>
    </div>
</body>
</html>
"""
    
    def _get_backtest_report_template(self) -> str:
        return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
</head>
<body>
    <div class="header">
        <h1>{{ title }}</h1>
        <p class="date">生成时间: {{ generated_at }}</p>
    </div>
    
    <div class="section">
        <h2>回测摘要</h2>
        <p>{{ summary }}</p>
        <p><strong>回测期间:</strong> {{ backtest_period }}</p>
    </div>
    
    <div class="section">
        <h2>绩效指标</h2>
        <table class="data-table">
            <tr>
                <td>总收益率</td>
                <td>{{ metrics.total_return|default('--') }}%</td>
            </tr>
            <tr>
                <td>年化收益率</td>
                <td>{{ metrics.annual_return|default('--') }}%</td>
            </tr>
            <tr>
                <td>夏普比率</td>
                <td>{{ metrics.sharpe_ratio|default('--') }}</td>
            </tr>
            <tr>
                <td>最大回撤</td>
                <td>{{ metrics.max_drawdown|default('--') }}%</td>
            </tr>
            <tr>
                <td>波动率</td>
                <td>{{ metrics.volatility|default('--') }}%</td>
            </tr>
            <tr>
                <td>胜率</td>
                <td>{{ metrics.win_rate|default('--') }}%</td>
            </tr>
            <tr>
                <td>交易次数</td>
                <td>{{ metrics.total_trades|default('--') }}</td>
            </tr>
        </table>
    </div>
    
    <div class="section">
        <h2>持仓配置</h2>
        <table class="data-table">
            <thead>
                <tr>
                    <th>代码</th>
                    <th>权重</th>
                </tr>
            </thead>
            <tbody>
                {% for code, weight in portfolio.items() %}
                <tr>
                    <td>{{ code }}</td>
                    <td>{{ (weight * 100)|round(2) }}%</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    
    <div class="section">
        <h2>近期交易记录</h2>
        <table class="data-table">
            <thead>
                <tr>
                    <th>日期</th>
                    <th>类型</th>
                    <th>代码</th>
                    <th>价格</th>
                    <th>原因</th>
                </tr>
            </thead>
            <tbody>
                {% for trade in trades %}
                <tr>
                    <td>{{ trade.date }}</td>
                    <td>{{ trade.type }}</td>
                    <td>{{ trade.code }}</td>
                    <td>{{ trade.price }}</td>
                    <td>{{ trade.reason }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    
    <div class="footer">
        <p>AI量化研究平台 | 本报告由AI自动生成，仅供参考</p>
    </div>
</body>
</html>
"""
    
    def _get_report_css(self) -> str:
        return """
@page {
    size: A4;
    margin: 2cm;
}

body {
    font-family: 'Microsoft YaHei', 'SimHei', Arial, sans-serif;
    font-size: 12px;
    line-height: 1.6;
    color: #333;
}

.header {
    text-align: center;
    margin-bottom: 30px;
    border-bottom: 2px solid #1a73e8;
    padding-bottom: 20px;
}

.header h1 {
    font-size: 24px;
    color: #1a73e8;
    margin: 0 0 10px 0;
}

.header .date {
    color: #666;
    font-size: 11px;
}

.section {
    margin-bottom: 25px;
}

.section h2 {
    font-size: 16px;
    color: #1a73e8;
    border-left: 4px solid #1a73e8;
    padding-left: 10px;
    margin-bottom: 15px;
}

.highlights {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

.highlight-item {
    flex: 1;
    min-width: 150px;
    background: #f5f5f5;
    padding: 10px;
    border-radius: 5px;
}

.highlight-title {
    display: block;
    font-size: 11px;
    color: #666;
    margin-bottom: 5px;
}

.highlight-value {
    display: block;
    font-size: 18px;
    font-weight: bold;
    color: #1a73e8;
}

.data-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
}

.data-table th,
.data-table td {
    border: 1px solid #ddd;
    padding: 8px 12px;
    text-align: left;
}

.data-table th {
    background-color: #1a73e8;
    color: white;
    font-weight: bold;
}

.data-table tr:nth-child(even) {
    background-color: #f9f9f9;
}

.data-table tr:hover {
    background-color: #f0f0f0;
}

.footer {
    text-align: center;
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid #ddd;
    color: #999;
    font-size: 10px;
}
"""
