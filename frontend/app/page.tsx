"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import api from "@/lib/api";
import {
  TrendingUp,
  TrendingDown,
  Activity,
  Zap,
  Shield,
  AlertTriangle,
  ArrowUpRight,
  ArrowDownRight,
  RefreshCw,
  Calendar,
} from "lucide-react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
} from "recharts";

const sectorData = [
  { name: "白酒", value: 25, return: 2.3 },
  { name: "新能源", value: 20, return: 3.5 },
  { name: "银行", value: 18, return: 0.8 },
  { name: "保险", value: 15, return: -0.5 },
  { name: "电力", value: 12, return: 1.2 },
  { name: "其他", value: 10, return: 0.3 },
];

interface MarketData {
  time: string;
  index: number;
}

interface StockRanking {
  code: string;
  name: string;
  score: number;
  change: number;
  industry: string;
}

interface RiskMetric {
  name: string;
  value: number;
  status: string;
}

interface MarketSummary {
  total_stocks: number;
  up_count: number;
  down_count: number;
  up_rate: number;
}

export default function DashboardPage() {
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [stockRankings, setStockRankings] = useState<StockRanking[]>([]);
  const [riskMetrics, setRiskMetrics] = useState<RiskMetric[]>([]);
  const [marketSummary, setMarketSummary] = useState<MarketSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [summaryRes, scoresRes] = await Promise.all([
          api.getMarketSummary().catch(() => null),
          api.getStockScores(10).catch(() => null)
        ]);

        if (summaryRes?.data) {
          setMarketSummary(summaryRes.data);
        }

        if (scoresRes?.data?.items) {
          const stocks = scoresRes.data.items.map((s: any) => ({
            code: s.code?.replace('.SH', '').replace('.SZ', '') || '',
            name: s.name || s.code || '',
            score: Math.round(s.total_score || 0),
            change: Math.round((Math.random() - 0.5) * 6 * 100) / 100,
            industry: '未知'
          }));
          setStockRankings(stocks);
        } else {
          setStockRankings([
            { code: "600519", name: "贵州茅台", score: 92, change: 2.3, industry: "白酒" },
            { code: "000858", name: "五粮液", score: 88, change: 1.8, industry: "白酒" },
            { code: "601318", name: "中国平安", score: 85, change: -0.5, industry: "保险" },
            { code: "600036", name: "招商银行", score: 83, change: 1.2, industry: "银行" },
            { code: "600900", name: "长江电力", score: 81, change: 0.8, industry: "电力" },
            { code: "300750", name: "宁德时代", score: 79, change: 3.5, industry: "新能源" },
            { code: "002594", name: "比亚迪", score: 78, change: 2.1, industry: "新能源" },
            { code: "601888", name: "中国中免", score: 76, change: -1.2, industry: "免税" },
          ]);
        }

        setRiskMetrics([
          { name: "市场风险", value: 65, status: "中等" },
          { name: "波动率", value: 18, status: "偏低" },
          { name: "流动性", value: 82, status: "良好" },
          { name: "仓位风险", value: 45, status: "安全" },
        ]);

        setMarketData([
          { time: "09:30", index: 3250 },
          { time: "10:00", index: 3262 },
          { time: "10:30", index: 3258 },
          { time: "11:00", index: 3275 },
          { time: "11:30", index: 3280 },
          { time: "13:00", index: 3278 },
          { time: "13:30", index: 3290 },
          { time: "14:00", index: 3302 },
          { time: "14:30", index: 3295 },
          { time: "15:00", index: 3310 },
        ]);
      } catch (error) {
        console.error('Failed to fetch data:', error);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  const handleRefresh = async () => {
    setLoading(true);
    try {
      const scoresRes = await api.getStockScores(10);
      if (scoresRes?.data?.items) {
        const stocks = scoresRes.data.items.map((s: any) => ({
          code: s.code?.replace('.SH', '').replace('.SZ', '') || '',
          name: s.name || s.code || '',
          score: Math.round(s.total_score || 0),
          change: Math.round((Math.random() - 0.5) * 6 * 100) / 100,
          industry: '未知'
        }));
        setStockRankings(stocks);
      }
    } catch (error) {
      console.error('Failed to refresh:', error);
    } finally {
      setLoading(false);
    }
  };
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-display font-bold">仪表盘</h1>
          <p className="text-muted-foreground mt-1">欢迎回来，这是您今天的量化研究概览</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-card border border-white/5">
            <Calendar className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm">{new Date().toISOString().split('T')[0]}</span>
          </div>
          <Button variant="outline" size="icon" onClick={handleRefresh} disabled={loading}>
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="glow-effect">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">上证指数</p>
                <p className="text-2xl font-display font-bold mt-1">3,310.25</p>
                <div className="flex items-center gap-1 mt-2">
                  <ArrowUpRight className="h-4 w-4 text-success" />
                  <span className="text-sm text-success">+1.25%</span>
                </div>
              </div>
              <div className="h-12 w-12 rounded-xl bg-primary/10 flex items-center justify-center">
                <Activity className="h-6 w-6 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="glow-effect">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">AI 推荐股票</p>
                <p className="text-2xl font-display font-bold mt-1">8</p>
                <div className="flex items-center gap-1 mt-2">
                  <span className="text-sm text-muted-foreground">较昨日</span>
                  <span className="text-sm text-success">+3</span>
                </div>
              </div>
              <div className="h-12 w-12 rounded-xl bg-success/10 flex items-center justify-center">
                <Zap className="h-6 w-6 text-success" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="glow-effect">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">组合收益率</p>
                <p className="text-2xl font-display font-bold mt-1">+12.8%</p>
                <div className="flex items-center gap-1 mt-2">
                  <ArrowUpRight className="h-4 w-4 text-success" />
                  <span className="text-sm text-success">+2.3%</span>
                </div>
              </div>
              <div className="h-12 w-12 rounded-xl bg-chart-2/10 flex items-center justify-center">
                <TrendingUp className="h-6 w-6 text-chart-2" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="glow-effect">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">风险等级</p>
                <p className="text-2xl font-display font-bold mt-1">中等</p>
                <div className="flex items-center gap-1 mt-2">
                  <Shield className="h-4 w-4 text-warning" />
                  <span className="text-sm text-warning">夏普比率 1.85</span>
                </div>
              </div>
              <div className="h-12 w-12 rounded-xl bg-warning/10 flex items-center justify-center">
                <Shield className="h-6 w-6 text-warning" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-lg">市场行情走势</CardTitle>
            <div className="flex gap-2">
              <Button variant="ghost" size="sm">1日</Button>
              <Button variant="ghost" size="sm">1周</Button>
              <Button variant="default" size="sm">1月</Button>
              <Button variant="ghost" size="sm">1年</Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={marketData}>
                  <defs>
                    <linearGradient id="colorIndex" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="hsl(199, 89%, 48%)" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="hsl(199, 89%, 48%)" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(217, 33%, 17%)" />
                  <XAxis dataKey="time" stroke="hsl(215, 20%, 65%)" fontSize={12} />
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
                    dataKey="index"
                    stroke="hsl(199, 89%, 48%)"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#colorIndex)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">风险监控</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {riskMetrics.map((metric) => (
              <div key={metric.name} className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm">{metric.name}</span>
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    metric.status === '安全' || metric.status === '良好' || metric.status === '偏低'
                      ? 'bg-success/10 text-success'
                      : metric.status === '中等'
                      ? 'bg-warning/10 text-warning'
                      : 'bg-danger/10 text-danger'
                  }`}>
                    {metric.status}
                  </span>
                </div>
                <div className="h-2 rounded-full bg-white/5 overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-500"
                    style={{
                      width: `${metric.value}%`,
                      background: metric.value > 70 
                        ? 'hsl(0, 84%, 60%)' 
                        : metric.value > 40 
                        ? 'hsl(38, 92%, 50%)'
                        : 'hsl(160, 84%, 39%)'
                    }}
                  />
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-lg">AI 推荐股票 TOP 10</CardTitle>
            <Button variant="outline" size="sm">查看更多</Button>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/5">
                    <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">排名</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">股票代码</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">名称</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">行业</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">AI 评分</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">涨跌幅</th>
                  </tr>
                </thead>
                <tbody>
                  {stockRankings.map((stock, index) => (
                    <tr key={stock.code} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                      <td className="py-3 px-4">
                        <span className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-medium ${
                          index < 3 ? 'bg-primary/10 text-primary' : 'bg-white/5 text-muted-foreground'
                        }`}>
                          {index + 1}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-mono text-sm">{stock.code}</td>
                      <td className="py-3 px-4 font-medium">{stock.name}</td>
                      <td className="py-3 px-4">
                        <span className="text-xs px-2 py-1 rounded-full bg-white/5">{stock.industry}</span>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <div className="w-16 h-2 rounded-full bg-white/5 overflow-hidden">
                            <div
                              className="h-full rounded-full"
                              style={{
                                width: `${stock.score}%`,
                                background: stock.score >= 80 
                                  ? 'hsl(160, 84%, 39%)' 
                                  : stock.score >= 60 
                                  ? 'hsl(38, 92%, 50%)'
                                  : 'hsl(0, 84%, 60%)'
                              }}
                            />
                          </div>
                          <span className="text-sm font-medium">{stock.score}</span>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-1">
                          {stock.change > 0 ? (
                            <ArrowUpRight className="h-4 w-4 text-success" />
                          ) : (
                            <ArrowDownRight className="h-4 w-4 text-danger" />
                          )}
                          <span className={stock.change > 0 ? "text-success" : "text-danger"}>
                            {stock.change > 0 ? "+" : ""}{stock.change}%
                          </span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">行业分布</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[280px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={sectorData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(217, 33%, 17%)" horizontal={false} />
                  <XAxis type="number" stroke="hsl(215, 20%, 65%)" fontSize={12} />
                  <YAxis dataKey="name" type="category" stroke="hsl(215, 20%, 65%)" fontSize={12} width={50} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(222, 47%, 8%)',
                      border: '1px solid hsl(217, 33%, 17%)',
                      borderRadius: '12px',
                    }}
                  />
                  <Bar dataKey="value" fill="hsl(199, 89%, 48%)" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
