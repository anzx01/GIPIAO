"""
PDF 报告生成器
使用 ReportLab 生成 PDF 报告
"""

from typing import Dict, List, Optional
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io


class PDFGenerator:
    """PDF 报告生成器"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_styles()
    
    def _setup_styles(self):
        """设置自定义样式"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2E7D32'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1B5E20'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomSubHeading',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#388E3C'),
            spaceAfter=8,
            spaceBefore=15,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=14,
            spaceAfter=6,
            fontName='Helvetica'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomRight',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=14,
            alignment=TA_RIGHT,
            fontName='Helvetica'
        ))
    
    def generate_daily_report(
        self,
        market_summary: Dict,
        top_stocks: List[Dict],
        market_sentiment: Dict,
        output_path: Optional[str] = None
    ) -> bytes:
        """生成每日市场报告"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        story = []
        
        story.append(Paragraph("AI 量化研究平台 - 每日市场报告", self.styles['CustomTitle']))
        story.append(Spacer(1, 12))
        
        story.append(Paragraph(f"报告日期: {datetime.now().strftime('%Y年%m月%d日')}", self.styles['CustomRight']))
        story.append(Spacer(1, 24))
        
        self._add_market_summary(story, market_summary)
        self._add_top_stocks(story, top_stocks)
        self._add_market_sentiment(story, market_sentiment)
        
        doc.build(story)
        
        pdf_data = buffer.getvalue()
        buffer.close()
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(pdf_data)
        
        return pdf_data
    
    def _add_market_summary(self, story: List, data: Dict):
        """添加市场概览"""
        story.append(Paragraph("市场概览", self.styles['CustomHeading']))
        
        summary_data = [
            ['指标', '数值'],
            ['上证指数', f"{data.get('sh_index', 0):.2f}"],
            ['深证成指', f"{data.get('sz_index', 0):.2f}"],
            ['创业板指', f"{data.get('cyb_index', 0):.2f}"],
            ['成交额', f"{data.get('volume', 0):.0f}亿"],
            ['涨跌家数', f"{data.get('up_count', 0)}涨 / {data.get('down_count', 0)}跌"]
        ]
        
        table = Table(summary_data, colWidths=[2*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#4CAF50')),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 24))
    
    def _add_top_stocks(self, story: List, stocks: List[Dict]):
        """添加热门股票"""
        story.append(Paragraph("热门股票推荐", self.styles['CustomHeading']))
        
        if not stocks:
            story.append(Paragraph("暂无推荐股票", self.styles['CustomBody']))
            story.append(Spacer(1, 24))
            return
        
        table_data = [['排名', '股票代码', '股票名称', 'AI评分', '推荐理由']]
        
        for i, stock in enumerate(stocks[:10], 1):
            table_data.append([
                str(i),
                stock.get('code', ''),
                stock.get('name', ''),
                f"{stock.get('total_score', 0):.1f}",
                stock.get('reason', '')[:30] + '...' if len(stock.get('reason', '')) > 30 else stock.get('reason', '')
            ])
        
        table = Table(table_data, colWidths=[0.5*inch, 1.2*inch, 1.5*inch, 0.8*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 24))
    
    def _add_market_sentiment(self, story: List, sentiment: Dict):
        """添加市场情绪"""
        story.append(Paragraph("市场情绪分析", self.styles['CustomHeading']))
        
        sentiment_text = sentiment.get('text', '市场情绪平稳')
        score = sentiment.get('score', 5)
        
        story.append(Paragraph(f"情绪指数: {score}/10", self.styles['CustomSubHeading']))
        story.append(Paragraph(sentiment_text, self.styles['CustomBody']))
        story.append(Spacer(1, 24))
    
    def generate_backtest_report(
        self,
        backtest_result: Dict,
        output_path: Optional[str] = None
    ) -> bytes:
        """生成回测报告"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        story = []
        
        story.append(Paragraph("AI 量化研究平台 - 回测报告", self.styles['CustomTitle']))
        story.append(Spacer(1, 12))
        
        story.append(Paragraph(f"生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}", self.styles['CustomRight']))
        story.append(Spacer(1, 24))
        
        self._add_backtest_summary(story, backtest_result)
        self._add_backtest_performance(story, backtest_result)
        
        doc.build(story)
        
        pdf_data = buffer.getvalue()
        buffer.close()
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(pdf_data)
        
        return pdf_data
    
    def _add_backtest_summary(self, story: List, result: Dict):
        """添加回测概要"""
        story.append(Paragraph("回测概要", self.styles['CustomHeading']))
        
        summary_data = [
            ['指标', '数值'],
            ['回测周期', f"{result.get('start_date', '')} 至 {result.get('end_date', '')}"],
            ['初始资金', f"{result.get('initial_capital', 0):,.0f}元"],
            ['最终资金', f"{result.get('final_capital', 0):,.0f}元"],
            ['总收益率', f"{result.get('total_return', 0):.2f}%"],
            ['年化收益率', f"{result.get('annual_return', 0):.2f}%"],
            ['最大回撤', f"{result.get('max_drawdown', 0):.2f}%"],
            ['夏普比率', f"{result.get('sharpe_ratio', 0):.2f}"]
        ]
        
        table = Table(summary_data, colWidths=[2*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#2196F3')),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 24))
    
    def _add_backtest_performance(self, story: List, result: Dict):
        """添加回测表现"""
        story.append(Paragraph("回测表现分析", self.styles['CustomHeading']))
        
        performance_text = result.get('analysis', '回测表现良好')
        story.append(Paragraph(performance_text, self.styles['CustomBody']))
        story.append(Spacer(1, 24))


pdf_generator = PDFGenerator()
