import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import loguru


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.logger = loguru.logger
        
        self.output_dir = self.config.get('output_dir', 'reports')
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    def generate_daily_report(self, data: Dict) -> str:
        """生成每日报告"""
        
        report_date = datetime.now().strftime("%Y%m%d")
        
        html_content = self._generate_html_report(data, report_date)
        
        output_path = os.path.join(
            self.output_dir, 
            f"daily_report_{report_date}.html"
        )
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"生成每日报告: {output_path}")
        
        return output_path
    
    def generate_weekly_report(self, data: Dict) -> str:
        """生成每周报告"""
        
        week = datetime.now().strftime("%Y-W%W")
        
        html_content = self._generate_weekly_html(data)
        
        output_path = os.path.join(
            self.output_dir,
            f"weekly_report_{week}.html"
        )
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"生成每周报告: {output_path}")
        
        return output_path
    
    def _generate_html_report(self, data: Dict, date: str) -> str:
        """生成HTML报告"""
        
        stock_scores = data.get('stock_scores', [])
        risk_metrics = data.get('risk_metrics', {})
        market_summary = data.get('market_summary', {})
        
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI量化研究日报 - {date}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 28px;
        }}
        .header .date {{
            opacity: 0.8;
            font-size: 14px;
        }}
        .section {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            margin-top: 0;
            color: #1a1a2e;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        th {{
            background: #f8f9fa;
            font-weight: 600;
            color: #333;
        }}
        .score-high {{
            color: #28a745;
            font-weight: bold;
        }}
        .score-medium {{
            color: #ffc107;
            font-weight: bold;
        }}
        .score-low {{
            color: #dc3545;
            font-weight: bold;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        .metric-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #1a1a2e;
        }}
        .metric-label {{
            color: #666;
            font-size: 14px;
            margin-top: 5px;
        }}
        .footer {{
            text-align: center;
            color: #666;
            font-size: 12px;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>AI Quant Research Hub</h1>
        <div class="date">日报日期: {date}</div>
    </div>
    
    <div class="section">
        <h2>市场概览</h2>
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{market_summary.get('total_stocks', 'N/A')}</div>
                <div class="metric-label">股票总数</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color: #28a745;">{market_summary.get('up_count', 'N/A')}</div>
                <div class="metric-label">上涨</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color: #dc3545;">{market_summary.get('down_count', 'N/A')}</div>
                <div class="metric-label">下跌</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{market_summary.get('flat_count', 'N/A')}</div>
                <div class="metric-label">平盘</div>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2>股票评分榜 (Top 10)</h2>
        <table>
            <thead>
                <tr>
                    <th>排名</th>
                    <th>股票代码</th>
                    <th>综合评分</th>
                    <th>估值评分</th>
                    <th>动量评分</th>
                    <th>质量评分</th>
                    <th>建议</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for _, row in enumerate(stock_scores[:10], 1):
            score = row.get('total_score', 0)
            if score >= 70:
                score_class = 'score-high'
                recommendation = '买入'
            elif score >= 50:
                score_class = 'score-medium'
                recommendation = '持有'
            else:
                score_class = 'score-low'
                recommendation = '卖出'
            
            html += f"""
                <tr>
                    <td>{row.get('rank', _)}</td>
                    <td>{row.get('code', '')}</td>
                    <td class="{score_class}">{score}</td>
                    <td>{row.get('pe_score', 0):.0f}</td>
                    <td>{row.get('momentum_score', 0):.0f}</td>
                    <td>{row.get('roe_score', 0):.0f}</td>
                    <td class="{score_class}">{recommendation}</td>
                </tr>
"""
        
        html += """
            </tbody>
        </table>
    </div>
    
    <div class="section">
        <h2>风险指标</h2>
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{risk_metrics.get('total_return', 0):.2f}%</div>
                <div class="metric-label">总收益率</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{risk_metrics.get('annual_return', 0):.2f}%</div>
                <div class="metric-label">年化收益率</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{risk_metrics.get('sharpe_ratio', 0):.2f}</div>
                <div class="metric-label">夏普比率</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{risk_metrics.get('max_drawdown', 0):.2f}%</div>
                <div class="metric-label">最大回撤</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{risk_metrics.get('volatility', 0):.2f}%</div>
                <div class="metric-label">波动率</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{risk_metrics.get('win_rate', 0):.2f}%</div>
                <div class="metric-label">胜率</div>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p>本报告由 AI Quant Research Hub 自动生成 | 仅供研究参考，不构成投资建议</p>
        <p>生成时间: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
    </div>
</body>
</html>
"""
        
        return html
    
    def _generate_weekly_html(self, data: Dict) -> str:
        """生成周报HTML"""
        
        return self._generate_html_report(data, datetime.now().strftime("%Y-W%W"))
    
    def generate_pdf(self, html_path: str, output_path: str = None) -> str:
        """将HTML转换为PDF"""
        try:
            import weasyprint
            
            if output_path is None:
                output_path = html_path.replace('.html', '.pdf')
            
            weasyprint.HTML(filename=html_path).write_pdf(output_path)
            
            self.logger.info(f"生成PDF: {output_path}")
            return output_path
            
        except ImportError:
            self.logger.warning("weasyprint未安装，无法生成PDF")
            return html_path
        except Exception as e:
            self.logger.error(f"PDF生成失败: {e}")
            return html_path
    
    def generate_json_report(self, data: Dict) -> str:
        """生成JSON格式报告"""
        import json
        
        report_date = datetime.now().strftime("%Y%m%d")
        output_path = os.path.join(
            self.output_dir,
            f"report_{report_date}.json"
        )
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"生成JSON报告: {output_path}")
        return output_path
