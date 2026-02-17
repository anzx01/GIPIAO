"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import api from "@/lib/api";
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
  Edit,
  Trash2,
  Save,
  X,
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

interface Portfolio {
  id: string;
  name: string;
  stocks: Record<string, number>;
  created_at?: string;
  updated_at?: string;
}

interface Position {
  code: string;
  name: string;
  weight: number;
  return: number;
  value: number;
  shares: number;
}

export default function PortfolioPage() {
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [selectedPortfolio, setSelectedPortfolio] = useState<Portfolio | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [editName, setEditName] = useState("");
  const [editStocks, setEditStocks] = useState<Record<string, number>>({});
  const [newStockCode, setNewStockCode] = useState("");
  const [newStockWeight, setNewStockWeight] = useState(10);

  useEffect(() => {
    fetchPortfolios();
  }, []);

  const fetchPortfolios = async () => {
    try {
      const res = await api.getPortfolioList();
      if (res?.data?.items) {
        setPortfolios(res.data.items);
        if (res.data.items.length > 0 && !selectedPortfolio) {
          setSelectedPortfolio(res.data.items[0]);
        }
      }
    } catch (error) {
      console.error('Failed to fetch portfolios:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setIsCreating(true);
    setEditName("新组合");
    setEditStocks({});
  };

  const handleEdit = () => {
    if (!selectedPortfolio) return;
    setIsEditing(true);
    setEditName(selectedPortfolio.name);
    setEditStocks({ ...selectedPortfolio.stocks });
  };

  const handleSave = async () => {
    if (!editName.trim()) {
      alert("请输入组合名称");
      return;
    }

    const totalWeight = Object.values(editStocks).reduce((sum, w) => sum + w, 0);
    if (Math.abs(totalWeight - 100) > 0.1) {
      alert(`权重总和应为100%，当前为${totalWeight.toFixed(1)}%`);
      return;
    }

    setSaving(true);
    try {
      if (isCreating) {
        const res = await api.createPortfolio(editName, editStocks);
        if (res?.data) {
          await fetchPortfolios();
          setIsCreating(false);
          setIsEditing(false);
        }
      } else if (isEditing && selectedPortfolio) {
        const res = await api.updatePortfolio(selectedPortfolio.id, editStocks);
        if (res?.data) {
          await fetchPortfolios();
          setIsEditing(false);
        }
      }
    } catch (error) {
      console.error('Failed to save portfolio:', error);
      alert("保存失败");
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setIsCreating(false);
    setIsEditing(false);
    setEditName("");
    setEditStocks({});
  };

  const handleDelete = async (portfolioId: string) => {
    if (!confirm("确定要删除这个组合吗？")) return;

    try {
      await fetch(`${api['baseUrl']}/api/portfolio/${portfolioId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      await fetchPortfolios();
      if (selectedPortfolio?.id === portfolioId) {
        setSelectedPortfolio(null);
      }
    } catch (error) {
      console.error('Failed to delete portfolio:', error);
      alert("删除失败");
    }
  };

  const handleAddStock = () => {
    if (!newStockCode.trim()) return;
    if (editStocks[newStockCode]) {
      alert("该股票已存在");
      return;
    }

    const currentTotal = Object.values(editStocks).reduce((sum, w) => sum + w, 0);
    const remaining = 100 - currentTotal;
    const weight = Math.min(newStockWeight, remaining);

    if (weight <= 0) {
      alert("权重已满，无法添加");
      return;
    }

    setEditStocks({ ...editStocks, [newStockCode]: weight });
    setNewStockCode("");
    setNewStockWeight(10);
  };

  const handleRemoveStock = (code: string) => {
    const newStocks = { ...editStocks };
    delete newStocks[code];
    setEditStocks(newStocks);
  };

  const handleUpdateWeight = (code: string, weight: number) => {
    setEditStocks({ ...editStocks, [code]: Math.max(0, Math.min(100, weight)) });
  };

  const getStockName = (code: string) => {
    const names: Record<string, string> = {
      "600519.SH": "贵州茅台",
      "000858.SH": "五粮液",
      "601318.SH": "中国平安",
      "600036.SH": "招商银行",
      "600900.SH": "长江电力",
      "300750.SZ": "宁德时代",
      "002594.SZ": "比亚迪",
    };
    return names[code] || code;
  };

  const portfolio = selectedPortfolio;
  const totalValue = 1250000;
  const totalReturn = 12.8;
  const dailyReturn = 1.25;
  const positionsCount = Object.keys(portfolio?.stocks || {}).length;

  const performanceData = [
    { month: "8月", value: 1000000, benchmark: 1000000 },
    { month: "9月", value: 1050000, benchmark: 1020000 },
    { month: "10月", value: 1030000, benchmark: 1010000 },
    { month: "11月", value: 1100000, benchmark: 1040000 },
    { month: "12月", value: 1150000, benchmark: 1060000 },
    { month: "1月", value: 1200000, benchmark: 1080000 },
    { month: "2月", value: 1250000, benchmark: 1100000 },
  ];

  const holdings: Position[] = portfolio
    ? Object.entries(portfolio.stocks).map(([code, weight]) => ({
        code: code.replace('.SH', '').replace('.SZ', ''),
        name: getStockName(code),
        weight,
        return: Math.round((Math.random() - 0.3) * 30 * 100) / 100,
        value: (totalValue * weight) / 100,
        shares: Math.round((totalValue * weight) / 100 / 100),
      }))
    : [];

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
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-display font-bold">组合管理</h1>
          <p className="text-muted-foreground mt-1">投资组合监控与绩效分析</p>
        </div>
        <div className="flex items-center gap-3">
          {isEditing || isCreating ? (
            <>
              <Button variant="outline" onClick={handleCancel} disabled={saving}>
                <X className="h-4 w-4 mr-2" />
                取消
              </Button>
              <Button onClick={handleSave} disabled={saving}>
                <Save className={`h-4 w-4 mr-2 ${saving ? 'animate-spin' : ''}`} />
                {saving ? '保存中...' : '保存'}
              </Button>
            </>
          ) : (
            <>
              <Button variant="outline" onClick={handleEdit} disabled={!portfolio}>
                <Edit className="h-4 w-4 mr-2" />
                调仓
              </Button>
              <Button onClick={handleCreate}>
                <Plus className="h-4 w-4 mr-2" />
                新建组合
              </Button>
            </>
          )}
        </div>
      </div>

      {portfolios.length > 0 && (
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-4">
              <span className="text-sm text-muted-foreground">选择组合:</span>
              <select
                className="flex-1 h-10 px-3 rounded-md border border-white/10 bg-white/5 text-foreground"
                value={selectedPortfolio?.id || ""}
                onChange={(e) => {
                  const p = portfolios.find(p => p.id === e.target.value);
                  setSelectedPortfolio(p || null);
                }}
              >
                {portfolios.map(p => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>
              {portfolio && (
                <Button variant="ghost" size="sm" onClick={() => handleDelete(portfolio.id)}>
                  <Trash2 className="h-4 w-4 text-danger" />
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {isEditing || isCreating ? (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">
              {isCreating ? '创建新组合' : '编辑组合'}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">组合名称</label>
              <Input
                type="text"
                placeholder="输入组合名称"
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">持仓配置</label>
              <div className="space-y-3">
                {Object.entries(editStocks).map(([code, weight]) => (
                  <div key={code} className="flex items-center gap-3">
                    <Input
                      type="text"
                      value={code}
                      className="flex-1"
                      disabled
                    />
                    <Input
                      type="number"
                      min="0"
                      max="100"
                      step="1"
                      value={weight}
                      onChange={(e) => handleUpdateWeight(code, parseFloat(e.target.value) || 0)}
                      className="w-24"
                    />
                    <span className="text-sm text-muted-foreground">%</span>
                    <Button variant="ghost" size="sm" onClick={() => handleRemoveStock(code)}>
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                ))}

                <div className="flex items-center gap-3 pt-2 border-t border-white/5">
                  <Input
                    type="text"
                    placeholder="股票代码 (如: 600519.SH)"
                    value={newStockCode}
                    onChange={(e) => setNewStockCode(e.target.value)}
                    className="flex-1"
                  />
                  <Input
                    type="number"
                    min="1"
                    max="100"
                    step="1"
                    value={newStockWeight}
                    onChange={(e) => setNewStockWeight(parseFloat(e.target.value) || 10)}
                    className="w-24"
                  />
                  <span className="text-sm text-muted-foreground">%</span>
                  <Button variant="outline" size="sm" onClick={handleAddStock}>
                    <Plus className="h-4 w-4 mr-2" />
                    添加
                  </Button>
                </div>

                <div className="flex items-center justify-between pt-2">
                  <span className="text-sm text-muted-foreground">
                    当前权重: {Object.values(editStocks).reduce((sum, w) => sum + w, 0).toFixed(1)}%
                  </span>
                  <span className={`text-sm font-medium ${
                    Math.abs(Object.values(editStocks).reduce((sum, w) => sum + w, 0) - 100) < 0.1
                      ? 'text-success'
                      : 'text-warning'
                  }`}>
                    {Math.abs(Object.values(editStocks).reduce((sum, w) => sum + w, 0) - 100) < 0.1
                      ? '权重正常'
                      : '权重应为100%'}
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      ) : portfolio ? (

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="glow-effect">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">总资产</p>
                <p className="text-2xl font-display font-bold mt-1">
                  ¥{(totalValue / 10000).toFixed(1)}万
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
                  +{totalReturn}%
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
                  +{dailyReturn}%
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
                <p className="text-2xl font-display font-bold mt-1">{positionsCount}</p>
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
