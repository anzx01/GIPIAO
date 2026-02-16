"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Briefcase,
  TrendingUp,
  TrendingDown,
  PieChart,
  BarChart3,
  Plus,
  ArrowUpRight,
  ArrowDownRight,
  DollarSign,
  Percent,
} from "lucide-react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";

const portfolio = {
  totalValue: 1250000,
  totalReturn: 12.8,
  dailyReturn: 1.25,
  positions: 8,
};

const performanceData = [
  { month: "8月", value: 1000000, benchmark: 1000000 },
  { month: "9月", value: 1050000, benchmark: 1020000 },
  { month: "10月", value: 1030000, benchmark: 1010000 },
  { month: "11月", value: 1100000, benchmark: 1040000 },
  { month: "12月", value: 1150000, benchmark: 1060000 },
  { month: "1月", value: 1200000, benchmark: 1080000 },
  { month: "2月", value: 1250000, benchmark: 1100000 },
];

const holdings = [
  { code: "600519", name: "贵州茅台", weight: 25, return: 15.2, value: 312500, shares: 185 },
  { code: "000858", name: "五粮液", weight: 18, return: 12.8, value: 225000, shares: 1200 },
  { code: "601318", name: "中国平安", weight: 15, return: -2.5, value: 187500, shares: 2500 },
  { code: "600036", name: "招商银行", weight: 12, return: 8.3, value: 150000, shares: 4500 },
  { code: "600900", name: "长江电力", weight: 10, return: 5.2, value: 125000, shares: 5500 },
  { code: "300750", name: "宁德时代", weight: 8, return: 22.5, value: 100000, shares: 280 },
  { code: "002594", name: "比亚迪", weight: 7, return: 18.7, value: 87500, shares: 350 },
  { code: "现金", name: "现金", weight: 5, return: 0, value: 62500, shares: 0 },
];

const sectorAllocation = [
  { name: "白酒", value: 43, color: "hsl(199, 89%, 48%)" },
  { name: "金融", value: 27, color: "hsl(280, 65%, 60%)" },
  { name: "新能源", value: 15, color: "hsl(160, 84%, 39%)" },
  { name: "电力", value: 10, color: "hsl(38, 92%, 50%)" },
  { name: "现金", value: 5, color: "hsl(215, 20%, 65%)" },
];

const riskMetrics = [
  { name: "年化收益率", value: "18.5%", icon: TrendingUp, color: "text-success" },
  { name: "夏普比率", value: "1.85", icon: BarChart3, color: "text-primary" },
  { name: "最大回撤", value: "-8.2%", icon: TrendingDown, color: "text-danger" },
  { name: "波动率", value: "15.3%", icon: PieChart, color: "text-warning" },
  { name: "Alpha", value: "5.2%", icon: DollarSign, color: "text-chart-2" },
  { name: "Beta", value: "0.85", icon: Percent, color: "text-chart-3" },
];

export default function PortfolioPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-display font-bold">组合管理</h1>
          <p className="text-muted-foreground mt-1">投资组合监控与绩效分析</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline">
            <Plus className="h-4 w-4 mr-2" />
            调仓
          </Button>
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            新建组合
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="glow-effect">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">总资产</p>
                <p className="text-2xl font-display font-bold mt-1">
                  ¥{(portfolio.totalValue / 10000).toFixed(1)}万
                </p>
              </div>
              <div className="h-12 w-12 rounded-xl bg-primary/10 flex items-center justify-center">
                <Briefcase className="h-6 w-6 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="glow-effect">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">总收益率</p>
                <p className="text-2xl font-display font-bold mt-1 text-success">
                  +{portfolio.totalReturn}%
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
                <p className="text-sm text-muted-foreground">日收益率</p>
                <p className="text-2xl font-display font-bold mt-1 text-success">
                  +{portfolio.dailyReturn}%
                </p>
              </div>
              <div className="h-12 w-12 rounded-xl bg-chart-2/10 flex items-center justify-center">
                <ArrowUpRight className="h-6 w-6 text-chart-2" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="glow-effect">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">持仓数量</p>
                <p className="text-2xl font-display font-bold mt-1">{portfolio.positions}</p>
              </div>
              <div className="h-12 w-12 rounded-xl bg-chart-4/10 flex items-center justify-center">
                <PieChart className="h-6 w-6 text-chart-4" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-lg">收益走势</CardTitle>
            <div className="flex gap-2">
              <Button variant="ghost" size="sm">1月</Button>
              <Button variant="ghost" size="sm">3月</Button>
              <Button variant="default" size="sm">6月</Button>
              <Button variant="ghost" size="sm">1年</Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="h-[350px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={performanceData}>
                  <defs>
                    <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="hsl(199, 89%, 48%)" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="hsl(199, 89%, 48%)" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="colorBenchmark" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="hsl(215, 20%, 65%)" stopOpacity={0.2} />
                      <stop offset="95%" stopColor="hsl(215, 20%, 65%)" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(217, 33%, 17%)" />
                  <XAxis dataKey="month" stroke="hsl(215, 20%, 65%)" fontSize={12} />
                  <YAxis stroke="hsl(215, 20%, 65%)" fontSize={12} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(222, 47%, 8%)',
                      border: '1px solid hsl(217, 33%, 17%)',
                      borderRadius: '12px',
                    }}
                    formatter={(value: number) => [`¥${(value / 10000).toFixed(1)}万`, '']}
                  />
                  <Area
                    type="monotone"
                    dataKey="value"
                    stroke="hsl(199, 89%, 48%)"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#colorValue)"
                    name="组合收益"
                  />
                  <Area
                    type="monotone"
                    dataKey="benchmark"
                    stroke="hsl(215, 20%, 65%)"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#colorBenchmark)"
                    name="基准收益"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">行业配置</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[280px]">
              <ResponsiveContainer width="100%" height="100%">
                <RechartsPieChart>
                  <Pie
                    data={sectorAllocation}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={2}
                    dataKey="value"
                  >
                    {sectorAllocation.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(222, 47%, 8%)',
                      border: '1px solid hsl(217, 33%, 17%)',
                      borderRadius: '12px',
                    }}
                    formatter={(value: number) => [`${value}%`, '']}
                  />
                  <Legend />
                </RechartsPieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-lg">持仓明细</CardTitle>
          <div className="flex gap-2">
            <Input type="search" placeholder="搜索股票..." className="w-48 h-9" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-white/5">
                  <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">股票代码</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">名称</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground">持仓占比</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground">持仓数量</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground">持仓市值</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground">收益率</th>
                </tr>
              </thead>
              <tbody>
                {holdings.map((holding) => (
                  <tr key={holding.code} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                    <td className="py-3 px-4 font-mono text-sm">{holding.code}</td>
                    <td className="py-3 px-4 font-medium">{holding.name}</td>
                    <td className="py-3 px-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <div className="w-16 h-2 rounded-full bg-white/5 overflow-hidden">
                          <div
                            className="h-full rounded-full bg-primary"
                            style={{ width: `${holding.weight}%` }}
                          />
                        </div>
                        <span className="text-sm">{holding.weight}%</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-right font-mono">{holding.shares.toLocaleString()}</td>
                    <td className="py-3 px-4 text-right">¥{(holding.value / 10000).toFixed(1)}万</td>
                    <td className="py-3 px-4 text-right">
                      <div className="flex items-center justify-end gap-1">
                        {holding.return > 0 ? (
                          <ArrowUpRight className="h-4 w-4 text-success" />
                        ) : holding.return < 0 ? (
                          <ArrowDownRight className="h-4 w-4 text-danger" />
                        ) : null}
                        <span className={holding.return > 0 ? "text-success" : holding.return < 0 ? "text-danger" : ""}>
                          {holding.return > 0 ? "+" : ""}{holding.return}%
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
          <CardTitle className="text-lg">风险指标</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {riskMetrics.map((metric) => {
              const Icon = metric.icon;
              return (
                <div key={metric.name} className="p-4 rounded-xl bg-white/5 border border-white/5">
                  <div className="flex items-center gap-2 mb-2">
                    <Icon className={`h-4 w-4 ${metric.color}`} />
                    <span className="text-sm text-muted-foreground">{metric.name}</span>
                  </div>
                  <p className={`text-2xl font-display font-bold ${metric.color}`}>{metric.value}</p>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
