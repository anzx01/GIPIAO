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
  Cell,
} from "recharts";

interface BacktestConfig {
  startDate: string;
  endDate: string;
  initialCapital: number;
  commission: number;
  slippage: number;
}

interface BacktestResult {
  total_return?: number;
  annual_return?: number;
  sharpe_ratio?: number;
  max_drawdown?: number;
  win_rate?: number;
  volatility?: number;
  total_trades?: number;
  avg_win?: number;
  avg_loss?: number;
  trades?: Array<{ date: string; type: string; code: string; price?: number; reason?: string }>;
  portfolio_values?: Array<{ date: string; value: number; return?: number }>;
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

  const [stocks, setStocks] = useState<StockPosition[]>([]);

  const [backtestResult, setBacktestResult] = useState<BacktestResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [showConfig, setShowConfig] = useState(false);

  const equityCurve = backtestResult?.portfolio_values || [];
  let equityPeak = 0;
  const drawdownData = equityCurve.map((point) => {
    equityPeak = Math.max(equityPeak, point.value);
    const peak = equityPeak;
    const drawdown = peak > 0 ? ((point.value - peak) / peak) * 100 : 0;
    return { date: point.date, drawdown: Number(drawdown.toFixed(2)) };
  });
  const monthlyReturns = equityCurve
    .filter((point) => typeof point.return === "number")
    .map((point) => ({
      month: point.date,
      return: Number(((point.return || 0) * 100).toFixed(2)),
    }));
  const trades = backtestResult?.trades || [];
  const formatPercent = (value?: number, signed = false) => {
    if (typeof value !== "number") return "暂无";
    const prefix = signed && value > 0 ? "+" : "";
    return `${prefix}${value}%`;
  };
  const formatNumber = (value?: number) => (typeof value === "number" ? String(value) : "暂无");
  const profitLossRatio =
    typeof backtestResult?.avg_win === "number" && typeof backtestResult?.avg_loss === "number" && backtestResult.avg_loss !== 0
      ? (backtestResult.avg_win / Math.abs(backtestResult.avg_loss)).toFixed(2)
      : "暂无";

  const handleRunBacktest = async () => {
    if (stocks.length === 0) {
      alert("请先添加至少一只股票");
      return;
    }
    if (Math.abs(getTotalWeight() - 100) > 0.1) {
      alert("持仓权重总和必须为100%");
      return;
    }

    const portfolio = stocks.reduce((acc, stock) => {
      const code = stock.code.trim().toUpperCase();
      if (code) {
        acc[code] = stock.weight / 100;
      }
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
                  {formatPercent(backtestResult?.total_return, true)}
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
                  {formatPercent(backtestResult?.annual_return, true)}
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
                <p className="text-2xl font-display font-bold mt-1">{formatNumber(backtestResult?.sharpe_ratio)}</p>
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
                  {formatPercent(backtestResult?.max_drawdown)}
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
                <p className="text-lg font-display font-bold">{formatPercent(backtestResult?.win_rate)}</p>
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
                <p className="text-lg font-display font-bold">{formatPercent(backtestResult?.volatility)}</p>
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
                <p className="text-lg font-display font-bold">{formatNumber(backtestResult?.total_trades)}</p>
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
                <p className="text-lg font-display font-bold text-success">{formatPercent(backtestResult?.avg_win, true)}</p>
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
                <p className="text-lg font-display font-bold text-danger">{formatPercent(backtestResult?.avg_loss)}</p>
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
                <p className="text-lg font-display font-bold">{profitLossRatio}</p>
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
              {equityCurve.length > 0 ? (
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
              ) : (
                <div className="flex h-full items-center justify-center text-muted-foreground">暂无回测曲线</div>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">回撤曲线</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              {drawdownData.length > 0 ? (
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
              ) : (
                <div className="flex h-full items-center justify-center text-muted-foreground">暂无回撤数据</div>
              )}
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
              {monthlyReturns.length > 0 ? (
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
                        <Cell key={`cell-${index}`} fill={entry.return >= 0 ? 'hsl(160, 84%, 39%)' : 'hsl(0, 84%, 60%)'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex h-full items-center justify-center text-muted-foreground">暂无月度收益</div>
              )}
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
            {trades.length > 0 ? (
              trades.map((trade, index) => (
                <div key={index} className="flex items-center justify-between p-3 rounded-xl bg-white/5 border border-white/5">
                  <div className="flex items-center gap-3">
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      trade.type === '买入' ? 'bg-success/10 text-success' : 'bg-danger/10 text-danger'
                    }`}>
                      {trade.type}
                    </span>
                    <span className="font-mono text-sm">{trade.code}</span>
                    {typeof trade.price === "number" && (
                      <span className="text-muted-foreground">@¥{trade.price}</span>
                    )}
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-muted-foreground">{trade.reason || ""}</span>
                    <span className="text-xs text-muted-foreground">{trade.date}</span>
                  </div>
                </div>
              ))
            ) : (
              <div className="flex h-[180px] items-center justify-center text-muted-foreground">暂无交易记录</div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
