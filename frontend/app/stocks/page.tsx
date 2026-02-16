"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import api from "@/lib/api";
import {
  Search,
  TrendingUp,
  TrendingDown,
  Star,
  Activity,
  BarChart3,
  Newspaper,
  Filter,
  Download,
} from "lucide-react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from "recharts";

const stockDetail = {
  code: "600519",
  name: "贵州茅台",
  price: 1685.5,
  change: 2.35,
  volume: 2845000,
  amount: 4780000000,
  pe: 32.5,
  pb: 8.2,
  marketCap: 2118000000000,
};

const priceHistory = [
  { date: "02-09", price: 1620 },
  { date: "02-10", price: 1635 },
  { date: "02-11", price: 1642 },
  { date: "02-12", price: 1638 },
  { date: "02-13", price: 1655 },
  { date: "02-14", price: 1668 },
  { date: "02-15", price: 1675 },
  { date: "02-16", price: 1685 },
];

const factorData = [
  { factor: "估值", value: 75, fullMark: 100 },
  { factor: "成长", value: 85, fullMark: 100 },
  { factor: "盈利", value: 92, fullMark: 100 },
  { factor: "动量", value: 68, fullMark: 100 },
  { factor: "质量", value: 88, fullMark: 100 },
  { factor: "波动", value: 45, fullMark: 100 },
];

const newsData = [
  { title: "茅台发布2024年财报预告，净利润同比增长15%", time: "2小时前", sentiment: "positive" },
  { title: "白酒行业迎来消费旺季，经销商备货积极", time: "5小时前", sentiment: "positive" },
  { title: "机构上调茅台目标价至1800元", time: "1天前", sentiment: "positive" },
  { title: "高端白酒市场价格波动引起关注", time: "2天前", sentiment: "neutral" },
];

const technicalIndicators = [
  { name: "MA5", value: 1658, signal: "买入" },
  { name: "MA10", value: 1642, signal: "买入" },
  { name: "MA20", value: 1635, signal: "买入" },
  { name: "RSI", value: 72.5, signal: "超买" },
  { name: "MACD", value: 15.8, signal: "金叉" },
  { name: "KDJ", value: 85, signal: "超买" },
];

interface StockDetail {
  code: string;
  name: string;
  price: number;
  change: number;
  volume: number;
  amount: number;
  pe: number;
  pb: number;
  marketCap: number;
}

interface PriceData {
  date: string;
  close: number;
}

interface FactorData {
  factor: string;
  value: number;
  fullMark: number;
}

interface TechnicalIndicator {
  name: string;
  value: number;
  signal: string;
}

export default function StocksPage() {
  const [searchCode, setSearchCode] = useState("600519.SH");
  const [stockDetail, setStockDetail] = useState<StockDetail>({
    code: "600519",
    name: "贵州茅台",
    price: 1685.5,
    change: 2.35,
    volume: 2845000,
    amount: 4780000000,
    pe: 32.5,
    pb: 8.2,
    marketCap: 2118000000000,
  });
  const [priceHistory, setPriceHistory] = useState<PriceData[]>([]);
  const [factorData, setFactorData] = useState<FactorData[]>([]);
  const [technicalIndicators, setTechnicalIndicators] = useState<TechnicalIndicator[]>([]);
  const [newsData, setNewsData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (searchCode) {
      fetchStockData(searchCode);
    }
  }, []);

  const fetchStockData = async (code: string) => {
    setLoading(true);
    try {
      const detailRes = await api.getStockDetail(code, 60);
      if (detailRes?.data) {
        const data = detailRes.data;
        
        setStockDetail({
          code: data.code?.replace('.SH', '').replace('.SZ', '') || code,
          name: data.name || code,
          price: data.latest_price?.close || 0,
          change: data.latest_price?.pct_change || 0,
          volume: data.latest_price?.volume || 0,
          amount: data.latest_price?.amount || 0,
          pe: data.financial_data?.pe || 0,
          pb: data.financial_data?.pb || 0,
          marketCap: data.financial_data?.market_cap || 0,
        });

        if (data.price_data) {
          const prices = data.price_data.slice(-30).map((p: any) => ({
            date: p.date?.slice(5, 10) || '',
            close: p.close || 0,
          }));
          setPriceHistory(prices);
        }

        if (data.technical_indicators) {
          const ti = data.technical_indicators;
          setTechnicalIndicators([
            { name: "MA5", value: ti.ma?.ma5 || 0, signal: "买入" },
            { name: "MA10", value: ti.ma?.ma10 || 0, signal: "买入" },
            { name: "MA20", value: ti.ma?.ma20 || 0, signal: "观望" },
            { name: "RSI", value: ti.rsi || 0, signal: ti.rsi > 70 ? "超买" : ti.rsi < 30 ? "超卖" : "正常" },
            { name: "MACD", value: ti.macd?.value || 0, signal: ti.macd?.histogram > 0 ? "金叉" : "死叉" },
            { name: "KDJ", value: 0, signal: "观望" },
          ]);
        }

        if (data.news) {
          setNewsData(data.news.slice(0, 5));
        }

        const scoresRes = await api.getStockScores(1);
        if (scoresRes?.data?.items?.[0]) {
          const score = scoresRes.data.items[0];
          setFactorData([
            { factor: "估值", value: score.pe_score || 75, fullMark: 100 },
            { factor: "成长", value: score.roe_score || 85, fullMark: 100 },
            { factor: "盈利", value: score.total_score || 92, fullMark: 100 },
            { factor: "动量", value: score.momentum_score || 68, fullMark: 100 },
            { factor: "质量", value: score.roe_score || 88, fullMark: 100 },
            { factor: "波动", value: score.volatility_score || 45, fullMark: 100 },
          ]);
        }
      }
    } catch (error) {
      console.error('Failed to fetch stock data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    const code = searchCode.includes('.') ? searchCode : searchCode + '.SH';
    fetchStockData(code);
  };
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-display font-bold">股票分析</h1>
          <p className="text-muted-foreground mt-1">深度分析个股，AI 评分与因子分析</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input 
              type="search" 
              placeholder="输入股票代码..." 
              className="w-64 pl-10"
              value={searchCode}
              onChange={(e) => setSearchCode(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            />
          </div>
          <Button variant="outline" onClick={handleSearch}>
            <Filter className="h-4 w-4 mr-2" />
            搜索
          </Button>
        </div>
      </div>

      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="h-16 w-16 rounded-2xl bg-gradient-to-br from-primary/20 to-purple-500/20 flex items-center justify-center border border-white/10">
                <span className="text-2xl font-display font-bold gradient-text">600519</span>
              </div>
              <div>
                <h2 className="text-2xl font-display font-bold">{stockDetail.name}</h2>
                <p className="text-muted-foreground">贵州茅台股份有限公司</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-3xl font-display font-bold">{stockDetail.price.toFixed(2)}</p>
              <div className="flex items-center gap-1 justify-end mt-1">
                {stockDetail.change > 0 ? (
                  <TrendingUp className="h-5 w-5 text-success" />
                ) : (
                  <TrendingDown className="h-5 w-5 text-danger" />
                )}
                <span className={stockDetail.change > 0 ? "text-success" : "text-danger"}>
                  {stockDetail.change > 0 ? "+" : ""}{stockDetail.change}%
                </span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mt-6 pt-6 border-t border-white/5">
            <div>
              <p className="text-sm text-muted-foreground">成交量</p>
              <p className="text-lg font-medium mt-1">{(stockDetail.volume / 10000).toFixed(0)}万</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">成交额</p>
              <p className="text-lg font-medium mt-1">{(stockDetail.amount / 100000000).toFixed(1)}亿</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">市盈率</p>
              <p className="text-lg font-medium mt-1">{stockDetail.pe}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">市净率</p>
              <p className="text-lg font-medium mt-1">{stockDetail.pb}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">总市值</p>
              <p className="text-lg font-medium mt-1">{(stockDetail.marketCap / 100000000).toFixed(0)}亿</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">AI 评分</p>
              <div className="flex items-center gap-1 mt-1">
                <Star className="h-5 w-5 text-warning fill-warning" />
                <span className="text-lg font-bold text-warning">92</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-lg">价格走势</CardTitle>
            <div className="flex gap-2">
              <Button variant="ghost" size="sm">MACD</Button>
              <Button variant="ghost" size="sm">KDJ</Button>
              <Button variant="default" size="sm">K线</Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="h-[350px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={priceHistory}>
                  <defs>
                    <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="hsl(199, 89%, 48%)" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="hsl(199, 89%, 48%)" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(217, 33%, 17%)" />
                  <XAxis dataKey="date" stroke="hsl(215, 20%, 65%)" fontSize={12} />
                  <YAxis stroke="hsl(215, 20%, 65%)" fontSize={12} domain={['dataMin - 20', 'dataMax + 20']} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(222, 47%, 8%)',
                      border: '1px solid hsl(217, 33%, 17%)',
                      borderRadius: '12px',
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="price"
                    stroke="hsl(199, 89%, 48%)"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#colorPrice)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">因子雷达图</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={factorData}>
                  <PolarGrid stroke="hsl(217, 33%, 17%)" />
                  <PolarAngleAxis dataKey="factor" stroke="hsl(215, 20%, 65%)" fontSize={12} />
                  <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="hsl(215, 20%, 65%)" fontSize={10} />
                  <Radar
                    name="因子评分"
                    dataKey="value"
                    stroke="hsl(199, 89%, 48%)"
                    fill="hsl(199, 89%, 48%)"
                    fillOpacity={0.3}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-primary" />
              技术指标
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              {technicalIndicators.map((indicator) => (
                <div key={indicator.name} className="p-4 rounded-xl bg-white/5 border border-white/5">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">{indicator.name}</span>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      indicator.signal === '买入' || indicator.signal === '金叉'
                        ? 'bg-success/10 text-success'
                        : indicator.signal === '超买' || indicator.signal === '超卖'
                        ? 'bg-warning/10 text-warning'
                        : 'bg-white/5 text-muted-foreground'
                    }`}>
                      {indicator.signal}
                    </span>
                  </div>
                  <p className="text-xl font-display font-bold mt-2">{indicator.value}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Newspaper className="h-5 w-5 text-primary" />
              最新新闻
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {newsData.map((news, index) => (
              <div key={index} className="p-4 rounded-xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors cursor-pointer">
                <div className="flex items-start justify-between gap-2">
                  <p className="text-sm font-medium">{news.title}</p>
                  <span className={`w-2 h-2 rounded-full shrink-0 mt-2 ${
                    news.sentiment === 'positive' ? 'bg-success' :
                    news.sentiment === 'negative' ? 'bg-danger' : 'bg-warning'
                  }`} />
                </div>
                <p className="text-xs text-muted-foreground mt-2">{news.time}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-lg">AI 分析摘要</CardTitle>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            导出报告
          </Button>
        </CardHeader>
        <CardContent>
          <div className="p-6 rounded-2xl bg-gradient-to-r from-primary/10 to-purple-500/10 border border-primary/20">
            <h4 className="font-display font-semibold text-lg mb-3">综合评估</h4>
            <p className="text-muted-foreground leading-relaxed">
              贵州茅台当前 AI 综合评分为 92 分，属于高价值成长股。从因子分析来看，
              盈利因子（92分）和质量因子（88分）表现突出，显示公司具有较强的盈利能力和财务质量。
              估值因子（75分）处于合理区间，股息率稳定。技术面上，MACD 呈现金叉形态，
              短期均线呈多头排列，建议关注。风险提示：当前 RSI 处于超买区域，注意短期回调风险。
            </p>
            <div className="flex gap-4 mt-4">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-success" />
                <span className="text-sm">长期看好</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-warning" />
                <span className="text-sm">短期注意风险</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
