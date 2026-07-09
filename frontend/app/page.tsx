"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import api from "@/lib/api";
import {
  TrendingUp,
  Activity,
  Zap,
  Shield,
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
} from "recharts";

interface MarketData {
  time: string;
  index: number;
}

interface StockRanking {
  code: string;
  name: string;
  score: number;
  change: number | null;
  industry: string;
}

interface MarketSummary {
  total_stocks: number;
  up_count: number;
  down_count: number;
  up_rate: number;
  scope?: "market" | "stock_pool";
}

export default function DashboardPage() {
  // 注：/api/market/indices 与 /api/market/indices/{code} 目前没有真实数据源，
  // 因此这里不接这两个接口，市场行情走势图如实展示"暂无数据"。
  const [marketData] = useState<MarketData[]>([]);
  const [stockRankings, setStockRankings] = useState<StockRanking[]>([]);
  const [scoresTotal, setScoresTotal] = useState<number | null>(null);
  const [marketSummary, setMarketSummary] = useState<MarketSummary | null>(null);
  const [summaryLoading, setSummaryLoading] = useState(true);
  const [scoresLoading, setScoresLoading] = useState(true);
  const loading = summaryLoading || scoresLoading;

  async function fetchData() {
    setSummaryLoading(true);
    setScoresLoading(true);

    const timeout = <T,>(promise: Promise<T>, ms: number): Promise<T | null> =>
      Promise.race([
        promise,
        new Promise<null>((resolve) => setTimeout(() => resolve(null), ms)),
      ]).catch((err) => {
        console.error(err);
        return null;
      });

    const summaryTask = timeout(api.getMarketSummary(), 30000)
      .then((summaryRes) => {
        // 市场概览卡片：优先全市场真实快照；上游不可用时后端返回真实股票池摘要。
        setMarketSummary(summaryRes?.data ?? null);
      })
      .finally(() => setSummaryLoading(false));

    const scoresTask = timeout(api.getStockScores(10), 90000)
      .then((scoresRes) => {
        // AI 推荐股票 + TOP10 表格：来自 /api/stocks/scores，空缓存时后端会即时真实计算。
        if (scoresRes?.data?.items) {
          setScoresTotal(scoresRes.data.total ?? scoresRes.data.items.length);
          const stocks: StockRanking[] = scoresRes.data.items.map((s: any) => ({
            code: s.code || "",
            name: s.name || s.code || "",
            score: Math.round(s.total_score || 0),
            change: typeof s.pct_change === "number" ? s.pct_change : null,
            industry: s.industry || "未知",
          }));
          setStockRankings(stocks);
        } else {
          setScoresTotal(null);
          setStockRankings([]);
        }
      })
      .finally(() => setScoresLoading(false));

    await Promise.all([summaryTask, scoresTask]);
  }

  useEffect(() => {
    fetchData();
  }, []);

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
            <span className="text-sm">{new Date().toISOString().split("T")[0]}</span>
          </div>
          <Button variant="outline" size="icon" onClick={fetchData} disabled={loading}>
            <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="glow-effect">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">
                  {marketSummary?.scope === "stock_pool" ? "股票池涨跌家数占比" : "市场涨跌家数占比"}
                </p>
                {marketSummary ? (
                  <>
                    <p className="text-2xl font-display font-bold mt-1">{marketSummary.up_rate}%</p>
                    <div className="flex items-center gap-1 mt-2">
                      <ArrowUpRight className="h-4 w-4 text-success" />
                      <span className="text-sm text-success">{marketSummary.up_count}涨</span>
                      <ArrowDownRight className="h-4 w-4 text-danger ml-2" />
                      <span className="text-sm text-danger">{marketSummary.down_count}跌</span>
                    </div>
                  </>
                ) : (
                  <p className="text-2xl font-display font-bold mt-1 text-muted-foreground">
                    {summaryLoading ? "加载中..." : "暂无"}
                  </p>
                )}
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
                {scoresTotal !== null ? (
                  <>
                    <p className="text-2xl font-display font-bold mt-1">{scoresTotal}</p>
                    <div className="flex items-center gap-1 mt-2">
                      <span className="text-sm text-muted-foreground">共 {scoresTotal} 只股票有评分</span>
                    </div>
                  </>
                ) : (
                  <p className="text-2xl font-display font-bold mt-1 text-muted-foreground">
                    {scoresLoading ? "加载中..." : "暂无"}
                  </p>
                )}
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
                  <p className="text-2xl font-display font-bold mt-1 text-muted-foreground">
                    {summaryLoading ? "加载中..." : "暂无"}
                  </p>
                <div className="flex items-center gap-1 mt-2">
                  <span className="text-sm text-muted-foreground">组合绩效接口未接入真实计算</span>
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
                <p className="text-2xl font-display font-bold mt-1 text-muted-foreground">暂无</p>
                <div className="flex items-center gap-1 mt-2">
                  <span className="text-sm text-muted-foreground">风险模型未接入</span>
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
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              {marketData.length > 0 ? (
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
                    <YAxis stroke="hsl(215, 20%, 65%)" fontSize={12} domain={["dataMin - 20", "dataMax + 20"]} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "hsl(222, 47%, 8%)",
                        border: "1px solid hsl(217, 33%, 17%)",
                        borderRadius: "12px",
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
                ) : (
                  <div className="h-full flex items-center justify-center text-muted-foreground">
                    {summaryLoading ? "加载中..." : "暂无数据"}
                  </div>
                )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">风险监控</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[240px] flex items-center justify-center text-center text-muted-foreground text-sm">
              暂无风险监控数据
              <br />
              （风险模型尚未接入）
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-lg">AI 推荐股票 TOP 10</CardTitle>
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
                  {stockRankings.length > 0 ? (
                    stockRankings.map((stock, index) => (
                      <tr key={stock.code} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                        <td className="py-3 px-4">
                          <span
                            className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-medium ${
                              index < 3 ? "bg-primary/10 text-primary" : "bg-white/5 text-muted-foreground"
                            }`}
                          >
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
                                  background:
                                    stock.score >= 80
                                      ? "hsl(160, 84%, 39%)"
                                      : stock.score >= 60
                                      ? "hsl(38, 92%, 50%)"
                                      : "hsl(0, 84%, 60%)",
                                }}
                              />
                            </div>
                            <span className="text-sm font-medium">{stock.score}</span>
                          </div>
                        </td>
                        <td className="py-3 px-4">
                          {stock.change === null ? (
                            <span className="text-muted-foreground">--</span>
                          ) : (
                            <div className="flex items-center gap-1">
                              {stock.change > 0 ? (
                                <ArrowUpRight className="h-4 w-4 text-success" />
                              ) : (
                                <ArrowDownRight className="h-4 w-4 text-danger" />
                              )}
                              <span className={stock.change > 0 ? "text-success" : "text-danger"}>
                                {stock.change > 0 ? "+" : ""}
                                {stock.change}%
                              </span>
                            </div>
                          )}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={6} className="py-8 text-center text-muted-foreground">
                        {scoresLoading ? "加载中..." : "暂无股票数据"}
                      </td>
                    </tr>
                  )}
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
            <div className="h-[280px] flex items-center justify-center text-center text-muted-foreground text-sm">
              暂无行业分布数据
              <br />
              （尚无持仓行业归类接口）
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
