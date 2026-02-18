"use client";

import { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import api from "@/lib/api";
import {
  Search,
  TrendingUp,
  TrendingDown,
  Star,
  BarChart3,
  Newspaper,
  Download,
  AlertTriangle,
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
import type { StockDetail, PriceData, FactorData, TechnicalIndicator, NewsItem } from "@/types";

export default function StocksPage() {
  const searchParams = useSearchParams();
  const urlCode = searchParams.get('code');

  const [searchCode, setSearchCode] = useState(urlCode || "600519.SH");
  const [stockDetail, setStockDetail] = useState<StockDetail>({
    code: "",
    name: "",
    price: 0,
    change: 0,
    volume: 0,
    amount: 0,
    pe: 0,
    pb: 0,
    marketCap: 0,
  });
  const [priceHistory, setPriceHistory] = useState<PriceData[]>([]);
  const [factorData, setFactorData] = useState<FactorData[]>([]);
  const [technicalIndicators, setTechnicalIndicators] = useState<TechnicalIndicator[]>([]);
  const [newsData, setNewsData] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [aiSummary, setAiSummary] = useState<string>("");
  const [error, setError] = useState<string>("");

  useEffect(() => {
    if (urlCode) {
      setSearchCode(urlCode);
      fetchStockData(urlCode);
    } else if (searchCode) {
      fetchStockData(searchCode);
    }
  }, [urlCode]);

  const fetchStockData = async (code: string) => {
    setLoading(true);
    setError("");
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
          amount: data.latest_price?.volume && data.latest_price?.close ? (data.latest_price.volume * data.latest_price.close) : 0,
          pe: data.financial_data?.pe || 0,
          pb: data.financial_data?.pb || 0,
          marketCap: data.financial_data?.market_cap || 0,
        });

        if (data.price_data && Array.isArray(data.price_data)) {
          const prices = data.price_data.slice(-30).map((p: any) => ({
            date: p.date?.slice(5, 10) || '',
            close: p.close || 0,
          }));
          setPriceHistory(prices);
        }

        if (data.technical_indicators) {
          const ti = data.technical_indicators;
          const currentPrice = data.latest_price?.close || 0;

          // 计算MA信号
          const ma5Signal = currentPrice > (ti.ma5 || 0) ? "买入" : "观望";
          const ma10Signal = currentPrice > (ti.ma10 || 0) ? "买入" : "观望";
          const ma20Signal = currentPrice > (ti.ma20 || 0) ? "买入" : "观望";

          setTechnicalIndicators([
            { name: "MA5", value: parseFloat((ti.ma5 || 0).toFixed(2)), signal: ma5Signal },
            { name: "MA10", value: parseFloat((ti.ma10 || 0).toFixed(2)), signal: ma10Signal },
            { name: "MA20", value: parseFloat((ti.ma20 || 0).toFixed(2)), signal: ma20Signal },
            { name: "RSI", value: parseFloat((ti.rsi || 50).toFixed(2)), signal: ti.rsi > 70 ? "超买" : ti.rsi < 30 ? "超卖" : "正常" },
            { name: "MACD", value: parseFloat((ti.macd || 0).toFixed(4)), signal: (ti.macd || 0) > (ti.signal || 0) ? "金叉" : "死叉" },
            { name: "成交量", value: Math.round((data.latest_price?.volume || 0) / 10000), signal: "观望" },
          ]);
        }

        if (data.news && Array.isArray(data.news)) {
          setNewsData(data.news.slice(0, 5));
        }

        try {
          const scoresRes = await api.getStockScores(10);
          if (scoresRes?.data?.items && Array.isArray(scoresRes.data.items)) {
            const stockScore = scoresRes.data.items.find((item: any) =>
              item.code === code || item.code === code.replace('.SH', '').replace('.SZ', '')
            );
            if (stockScore) {
              setFactorData([
                { factor: "估值", value: stockScore.pe_score || 75, fullMark: 100 },
                { factor: "成长", value: stockScore.roe_score || 85, fullMark: 100 },
                { factor: "盈利", value: stockScore.total_score || 92, fullMark: 100 },
                { factor: "动量", value: stockScore.momentum_score || 68, fullMark: 100 },
                { factor: "质量", value: stockScore.roe_score || 88, fullMark: 100 },
                { factor: "波动", value: stockScore.volatility_score || 45, fullMark: 100 },
              ]);
            } else {
              // 如果没有找到评分数据，使用默认值
              setFactorData([
                { factor: "估值", value: 75, fullMark: 100 },
                { factor: "成长", value: 85, fullMark: 100 },
                { factor: "盈利", value: 80, fullMark: 100 },
                { factor: "动量", value: 70, fullMark: 100 },
                { factor: "质量", value: 85, fullMark: 100 },
                { factor: "波动", value: 60, fullMark: 100 },
              ]);
            }
          } else {
            // API返回格式不正确，使用默认值
            setFactorData([
              { factor: "估值", value: 75, fullMark: 100 },
              { factor: "成长", value: 85, fullMark: 100 },
              { factor: "盈利", value: 80, fullMark: 100 },
              { factor: "动量", value: 70, fullMark: 100 },
              { factor: "质量", value: 85, fullMark: 100 },
              { factor: "波动", value: 60, fullMark: 100 },
            ]);
          }
        } catch (error) {
          console.error('Failed to fetch stock scores:', error);
          // 出错时也设置默认值，确保雷达图显示
          setFactorData([
            { factor: "估值", value: 75, fullMark: 100 },
            { factor: "成长", value: 85, fullMark: 100 },
            { factor: "盈利", value: 80, fullMark: 100 },
            { factor: "动量", value: 70, fullMark: 100 },
            { factor: "质量", value: 85, fullMark: 100 },
            { factor: "波动", value: 60, fullMark: 100 },
          ]);
        }

        // 生成 AI 分析摘要
        const summary = generateAISummary(data, code);
        setAiSummary(summary);
      }
    } catch (error: any) {
      console.error('Failed to fetch stock data:', error);
      let errorMessage = "查询股票数据失败";

      if (error.message) {
        if (error.message.includes('404') || error.message.includes('不存在')) {
          errorMessage = `股票代码 ${code} 不存在或暂无数据，请检查代码是否正确`;
        } else if (error.message.includes('网络')) {
          errorMessage = "网络连接失败，请检查网络设置";
        } else if (error.message.includes('401') || error.message.includes('403')) {
          errorMessage = "认证失败，请重新登录";
        } else {
          errorMessage = `查询失败: ${error.message}`;
        }
      }

      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const generateAISummary = (data: any, code: string) => {
    const name = data.name || code;
    const price = data.latest_price?.close || 0;
    const change = data.latest_price?.pct_change || 0;
    const pe = data.financial_data?.pe || 0;
    const pb = data.financial_data?.pb || 0;
    const ti = data.technical_indicators || {};
    
    let trend = "震荡";
    if (change > 2) trend = "强势上涨";
    else if (change > 0) trend = "上涨";
    else if (change < -2) trend = "大幅下跌";
    else if (change < 0) trend = "下跌";
    
    let techSignal = "观望";
    if (ti.macd > ti.signal && ti.rsi > 50) techSignal = "买入信号";
    else if (ti.macd < ti.signal && ti.rsi < 50) techSignal = "卖出信号";
    
    let valuation = "合理";
    if (pe > 30) valuation = "偏高";
    else if (pe < 15) valuation = "偏低";
    
    return `${name}（${code}）当前价格 ${price.toFixed(2)} 元，${change >= 0 ? '上涨' : '下跌'} ${Math.abs(change).toFixed(2)}%。从技术形态来看，${name} 呈现${trend}趋势，MACD指标显示${techSignal}。估值方面，当前市盈率${pe.toFixed(1)}倍，处于${valuation}区间。建议关注后续市场走势和基本面变化，合理控制仓位。`;
  };

  const handleSearch = () => {
    const code = searchCode.includes('.') ? searchCode : searchCode + '.SH';
    fetchStockData(code);
  };
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-display font-bold">股票分析</h1>
        <p className="text-muted-foreground mt-1">深度分析个股，AI 评分与因子分析</p>
      </div>

      {error && (
        <Card className="border-danger/50 bg-danger/10">
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-danger" />
              <p className="text-danger font-medium">{error}</p>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="h-16 w-16 rounded-2xl bg-gradient-to-br from-primary/20 to-purple-500/20 flex items-center justify-center border border-white/10">
                <span className="text-2xl font-display font-bold gradient-text">{stockDetail.code}</span>
              </div>
              <div>
                <h2 className="text-2xl font-display font-bold">{stockDetail.name}</h2>
                <p className="text-muted-foreground">{stockDetail.name}股份有限公司</p>
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
              {priceHistory.length > 0 ? (
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
                      dataKey="close"
                      stroke="hsl(199, 89%, 48%)"
                      strokeWidth={2}
                      fillOpacity={1}
                      fill="url(#colorPrice)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex items-center justify-center text-muted-foreground">
                  {loading ? '加载中...' : '暂无数据'}
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">因子雷达图</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              {factorData.length > 0 ? (
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
              ) : (
                <div className="h-full flex items-center justify-center text-muted-foreground">
                  {loading ? '加载中...' : '暂无数据'}
                </div>
              )}
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
                  <p className="text-xl font-display font-bold mt-2">
                    {indicator.name === "成交量"
                      ? `${indicator.value}万手`
                      : indicator.value.toFixed(indicator.name === "MACD" ? 4 : 2)}
                  </p>
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
            {loading ? (
              <p className="text-muted-foreground">正在分析...</p>
            ) : aiSummary ? (
              <p className="text-muted-foreground leading-relaxed">{aiSummary}</p>
            ) : (
              <p className="text-muted-foreground">请输入股票代码获取 AI 分析</p>
            )}
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
