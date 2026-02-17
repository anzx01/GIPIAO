"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import api from "@/lib/api";
import {
  FlaskConical,
  Play,
  Calendar,
  Clock,
  TrendingUp,
  TrendingDown,
  BarChart3,
  RefreshCw,
  Download,
  Settings,
  Plus,
  Trash2,
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

interface BacktestConfig {
  startDate: string;
  endDate: string;
  initialCapital: number;
  commission: number;
  slippage: number;
}

interface BacktestResult {
  totalReturn: number;
  annualReturn: number;
  sharpeRatio: number;
  maxDrawdown: number;
  winRate: number;
  volatility: number;
  totalTrades: number;
  avgWin: number;
  avgLoss: number;
  portfolioValues?: Array<{ date: string; value: number }>;
}

interface StockPosition {
  code: string;
  weight: number;
}

export default function BacktestPage() {
  const [backtestConfig, setBacktestConfig] = useState<BacktestConfig>({
    startDate: "2023-01-01",
    endDate: "2024-02-16",
    initialCapital: 1000000,
    commission: 0.0003,
    slippage: 0.001,
  });

  const [stocks, setStocks] = useState<StockPosition[]>([
    { code: "600519.SH", weight: 30 },
    { code: "000858.SH", weight: 30 },
    { code: "601318.SH", weight: 20 },
    { code: "600036.SH", weight: 20 },
  ]);

  const [backtestResult, setBacktestResult] = useState<BacktestResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [showConfig, setShowConfig] = useState(false);

  const equityCurve = backtestResult?.portfolioValues || [
    { date: "2023-01", value: 1000000 },
    { date: "2023-02", value: 1050000 },
    { date: "2023-03", value: 1080000 },
    { date: "2023-04", value: 1120000 },
    { date: "2023-05", value: 1180000 },
    { date: "2023-06", value: 1150000 },
    { date: "2023-07", value: 1200000 },
    { date: "2023-08", value: 1250000 },
    { date: "2023-09", value: 1220000 },
    { date: "2023-10", value: 1280000 },
    { date: "2023-11", value: 1320000 },
    { date: "2023-12", value: 1350000 },
    { date: "2024-01", value: 1420000 },
    { date: "2024-02", value: 1485000 },
  ];

  const drawdownData = [
    { date: "2023-01", drawdown: 0 },
    { date: "2023-02", drawdown: -2.5 },
    { date: "2023-03", drawdown: -1.8 },
    { date: "2023-04", drawdown: -3.2 },
    { date: "2023-05", drawdown: -5.5 },
    { date: "2023-06", drawdown: -12.8 },
    { date: "2023-07", drawdown: -8.5 },
    { date: "2023-08", drawdown: -6.2 },
    { date: "2023-09", drawdown: -9.8 },
    { date: "2023-10", drawdown: -5.2 },
    { date: "2023-11", drawdown: -3.5 },
    { date: "2023-12", drawdown: -2.8 },
    { date: "2024-01", drawdown: -1.5 },
    { date: "2024-02", drawdown: 0 },
  ];

  const monthlyReturns = [
    { month: "1月", return: 5.2 },
    { month: "2月", return: 3.8 },
    { month: "3月", return: -2.5 },
    { month: "4月", return: 4.2 },
    { month: "5月", return: 6.5 },
    { month: "6月", return: -8.2 },
    { month: "7月", return: 4.8 },
    { month: "8月", return: 3.2 },
    { month: "9月", return: -5.5 },
    { month: "10月", return: 8.2 },
    { month: "11月", return: 3.5 },
    { month: "12月", return: 2.8 },
  ];

  const trades = [
    { date: "2024-02-16", type: "买入", code: "600519", price: 1685.5, reason: "MA金叉" },
    { date: "2024-02-15", type: "卖出", code: "601318", price: 45.2, reason: "止盈" },
    { date: "2024-02-14", type: "买入", code: "000858", price: 158.5, reason: "突破买入" },
    { date: "2024-02-13", type: "卖出", code: "600036", price: 35.8, reason: "止损" },
    { date: "2024-02-12", type: "买入", code: "300750", price: 185.2, reason: "趋势跟随" },
  ];

  const handleRunBacktest = async () => {
    const portfolio = stocks.reduce((acc, stock) => {
      acc[stock.code] = stock.weight / 100;
      return acc;
    }, {} as Record<string, number>);

    setLoading(true);
    try {
      const res = await api.runBacktest(
        portfolio,
        backtestConfig.startDate,
        backtestConfig.endDate,
        backtestConfig.initialCapital
      );

      if (res?.data) {
        setBacktestResult(res.data);
      }
    } catch (error) {
      console.error('Backtest failed:', error);
      alert("回测失败，请检查参数");
    } finally {
      setLoading(false);
    }
  };

  const handleAddStock = () => {
    setStocks([...stocks, { code: "", weight: 10 }]);
  };

  const handleRemoveStock = (index: number) => {
    setStocks(stocks.filter((_, i) => i !== index));
  };

  const handleUpdateStock = (index: number, field: keyof StockPosition, value: string | number) => {
    const newStocks = [...stocks];
    if (field === "weight") {
      newStocks[index][field] = Number(value) as number;
    } else {
      newStocks[index][field] = value as string;
    }
    setStocks(newStocks);
  };

  const getTotalWeight = () => {
    return stocks.reduce((sum, stock) => sum + stock.weight, 0);
  };
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-display font-bold">回测分析</h1>
          <p className="text-muted-foreground mt-1">策略回测与绩效评估</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" onClick={() => setShowConfig(!showConfig)}>
            <Settings className="h-4 w-4 mr-2" />
            {showConfig ? "隐藏配置" : "策略设置"}
          </Button>
          <Button onClick={handleRunBacktest} disabled={loading}>
            <Play className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            {loading ? "回测中..." : "开始回测"}
          </Button>
        </div>
      </div>

      {showConfig && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Settings className="h-5 w-5 text-primary" />
              回测参数配置
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
              <div>
                <label className="text-sm text-muted-foreground">开始日期</label>
                <div className="flex items-center gap-2 mt-1.5">
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                  <Input 
                    type="date" 
                    value={backtestConfig.startDate}
                    onChange={(e) => setBacktestConfig({ ...backtestConfig, startDate: e.target.value })}
                    className="flex-1" 
                  />
                </div>
              </div>
              <div>
                <label className="text-sm text-muted-foreground">结束日期</label>
                <div className="flex items-center gap-2 mt-1.5">
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                  <Input 
                    type="date" 
                    value={backtestConfig.endDate}
                    onChange={(e) => setBacktestConfig({ ...backtestConfig, endDate: e.target.value })}
                    className="flex-1" 
                  />
                </div>
              </div>
              <div>
                <label className="text-sm text-muted-foreground">初始资金</label>
                <div className="flex items-center gap-2 mt-1.5">
                  <span className="text-lg">¥</span>
                  <Input 
                    type="number" 
                    value={backtestConfig.initialCapital}
                    onChange={(e) => setBacktestConfig({ ...backtestConfig, initialCapital: Number(e.target.value) })}
                    className="flex-1" 
                  />
                </div>
              </div>
              <div>
                <label className="text-sm text-muted-foreground">手续费率</label>
                <div className="flex items-center gap-2 mt-1.5">
                  <Input 
                    type="number" 
                    step="0.0001"
                    value={backtestConfig.commission}
                    onChange={(e) => setBacktestConfig({ ...backtestConfig, commission: Number(e.target.value) })}
                    className="flex-1" 
                  />
                  <span className="text-sm text-muted-foreground">%</span>
                </div>
              </div>
              <div>
                <label className="text-sm text-muted-foreground">滑点</label>
                <div className="flex items-center gap-2 mt-1.5">
                  <Input 
                    type="number" 
                    step="0.001"
                    value={backtestConfig.slippage}
                    onChange={(e) => setBacktestConfig({ ...backtestConfig, slippage: Number(e.target.value) })}
                    className="flex-1" 
                  />
                  <span className="text-sm text-muted-foreground">%</span>
                </div>
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-3">
                <label className="text-sm font-medium">持仓配置</label>
                <div className="flex items-center gap-3">
                  <span className={`text-sm ${getTotalWeight() === 100 ? 'text-success' : 'text-warning'}`}>
                    总权重: {getTotalWeight()}%
                  </span>
                  <Button variant="outline" size="sm" onClick={handleAddStock}>
                    <Plus className="h-4 w-4 mr-2" />
                    添加股票
                  </Button>
                </div>
              </div>
              <div className="space-y-2">
                {stocks.map((stock, index) => (
                  <div key={index} className="flex items-center gap-3">
                    <Input
                      type="text"
                      placeholder="股票代码 (如: 600519.SH)"
                      value={stock.code}
                      onChange={(e) => handleUpdateStock(index, "code", e.target.value)}
                      className="flex-1"
                    />
                    <Input
                      type="number"
                      min="0"
                      max="100"
                      step="1"
                      value={stock.weight}
                      onChange={(e) => handleUpdateStock(index, "weight", e.target.value)}
                      className="w-24"
                    />
                    <span className="text-sm text-muted-foreground">%</span>
                    <Button variant="ghost" size="sm" onClick={() => handleRemoveStock(index)}>
                      <Trash2 className="h-4 w-4 text-danger" />
                    </Button>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="glow-effect">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">总收益率</p>
                <p className="text-2xl font-display font-bold mt-1 text-success">
                  +{backtestResult.totalReturn}%
                </p>
              </div>
              <div className="h-12 w-12 rounded-xl bg-success/10 flex items-center justify-center">
                <TrendingUp className="h-6 w-6 text-success" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="glow-effect">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">年化收益率</p>
                <p className="text-2xl font-display font-bold mt-1 text-success">
                  +{backtestResult.annualReturn}%
                </p>
              </div>
              <div className="h-12 w-12 rounded-xl bg-primary/10 flex items-center justify-center">
                <BarChart3 className="h-6 w-6 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="glow-effect">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">夏普比率</p>
                <p className="text-2xl font-display font-bold mt-1">{backtestResult.sharpeRatio}</p>
              </div>
              <div className="h-12 w-12 rounded-xl bg-chart-2/10 flex items-center justify-center">
                <FlaskConical className="h-6 w-6 text-chart-2" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="glow-effect">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">最大回撤</p>
                <p className="text-2xl font-display font-bold mt-1 text-danger">
                  {backtestResult.maxDrawdown}%
                </p>
              </div>
              <div className="h-12 w-12 rounded-xl bg-danger/10 flex items-center justify-center">
                <TrendingDown className="h-6 w-6 text-danger" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
        <Card className="glow-effect">
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <div className="h-10 w-10 rounded-lg bg-chart-3/10 flex items-center justify-center">
                <Clock className="h-5 w-5 text-chart-3" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">胜率</p>
                <p className="text-lg font-display font-bold">{backtestResult?.winRate ?? 62.5}%</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="glow-effect">
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <div className="h-10 w-10 rounded-lg bg-chart-4/10 flex items-center justify-center">
                <BarChart3 className="h-5 w-5 text-chart-4" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">波动率</p>
                <p className="text-lg font-display font-bold">{backtestResult?.volatility ?? 15.2}%</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="glow-effect">
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                <RefreshCw className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">交易次数</p>
                <p className="text-lg font-display font-bold">{backtestResult?.totalTrades ?? 156}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="glow-effect">
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <div className="h-10 w-10 rounded-lg bg-success/10 flex items-center justify-center">
                <TrendingUp className="h-5 w-5 text-success" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">平均盈利</p>
                <p className="text-lg font-display font-bold text-success">+{backtestResult?.avgWin ?? 3.2}%</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="glow-effect">
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <div className="h-10 w-10 rounded-lg bg-danger/10 flex items-center justify-center">
                <TrendingDown className="h-5 w-5 text-danger" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">平均亏损</p>
                <p className="text-lg font-display font-bold text-danger">{backtestResult?.avgLoss ?? -1.8}%</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="glow-effect">
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <div className="h-10 w-10 rounded-lg bg-chart-2/10 flex items-center justify-center">
                <Download className="h-5 w-5 text-chart-2" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">盈亏比</p>
                <p className="text-lg font-display font-bold">{((backtestResult?.avgWin ?? 3.2) / Math.abs(backtestResult?.avgLoss ?? 1.8)).toFixed(2)}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-lg">权益曲线</CardTitle>
            <div className="flex gap-2">
              <Button variant="ghost" size="sm">对数</Button>
              <Button variant="default" size="sm">普通</Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={equityCurve}>
                  <defs>
                    <linearGradient id="colorEquity" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="hsl(199, 89%, 48%)" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="hsl(199, 89%, 48%)" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(217, 33%, 17%)" />
                  <XAxis dataKey="date" stroke="hsl(215, 20%, 65%)" fontSize={12} />
                  <YAxis stroke="hsl(215, 20%, 65%)" fontSize={12} tickFormatter={(v) => `${(v/10000).toFixed(0)}万`} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(222, 47%, 8%)',
                      border: '1px solid hsl(217, 33%, 17%)',
                      borderRadius: '12px',
                    }}
                    formatter={(value: number) => [`¥${(value/10000).toFixed(1)}万`, '权益']}
                  />
                  <Area
                    type="monotone"
                    dataKey="value"
                    stroke="hsl(199, 89%, 48%)"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#colorEquity)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">回撤曲线</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={drawdownData}>
                  <defs>
                    <linearGradient id="colorDrawdown" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="hsl(0, 84%, 60%)" stopOpacity={0} />
                      <stop offset="95%" stopColor="hsl(0, 84%, 60%)" stopOpacity={0.3} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(217, 33%, 17%)" />
                  <XAxis dataKey="date" stroke="hsl(215, 20%, 65%)" fontSize={12} />
                  <YAxis stroke="hsl(215, 20%, 65%)" fontSize={12} tickFormatter={(v) => `${v}%`} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(222, 47%, 8%)',
                      border: '1px solid hsl(217, 33%, 17%)',
                      borderRadius: '12px',
                    }}
                    formatter={(value: number) => [`${value}%`, '回撤']}
                  />
                  <Area
                    type="monotone"
                    dataKey="drawdown"
                    stroke="hsl(0, 84%, 60%)"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#colorDrawdown)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">月度收益</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[280px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={monthlyReturns}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(217, 33%, 17%)" />
                  <XAxis dataKey="month" stroke="hsl(215, 20%, 65%)" fontSize={12} />
                  <YAxis stroke="hsl(215, 20%, 65%)" fontSize={12} tickFormatter={(v) => `${v}%`} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(222, 47%, 8%)',
                      border: '1px solid hsl(217, 33%, 17%)',
                      borderRadius: '12px',
                    }}
                    formatter={(value: number) => [`${value}%`, '收益率']}
                  />
                  <Bar dataKey="return" radius={[4, 4, 0, 0]}>
                    {monthlyReturns.map((entry, index) => (
                      <cell key={`cell-${index}`} fill={entry.return >= 0 ? 'hsl(160, 84%, 39%)' : 'hsl(0, 84%, 60%)'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-lg">近期交易记录</CardTitle>
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              导出
            </Button>
          </CardHeader>
          <CardContent className="space-y-3">
            {trades.map((trade, index) => (
              <div key={index} className="flex items-center justify-between p-3 rounded-xl bg-white/5 border border-white/5">
                <div className="flex items-center gap-3">
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    trade.type === '买入' ? 'bg-success/10 text-success' : 'bg-danger/10 text-danger'
                  }`}>
                    {trade.type}
                  </span>
                  <span className="font-mono text-sm">{trade.code}</span>
                  <span className="text-muted-foreground">@¥{trade.price}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-muted-foreground">{trade.reason}</span>
                  <span className="text-xs text-muted-foreground">{trade.date}</span>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
