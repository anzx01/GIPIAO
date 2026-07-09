"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import api from "@/lib/api";
import {
  Briefcase,
  TrendingUp,
  PieChart,
  BarChart3,
  Plus,
  ArrowUpRight,
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
  weight: number;
  price?: number | null;
}

interface PortfolioPerformance {
  total_return?: number;
  annual_return?: number;
  daily_returns?: Array<{ date: string; return: number }>;
  portfolio_values?: Array<{ date: string; value: number }>;
  sharpe_ratio?: number;
  max_drawdown?: number;
  volatility?: number;
  win_rate?: number;
}

export default function PortfolioPage() {
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [selectedPortfolio, setSelectedPortfolio] = useState<Portfolio | null>(null);
  const [portfolioDetail, setPortfolioDetail] = useState<{ positions?: Position[] } | null>(null);
  const [portfolioPerformance, setPortfolioPerformance] = useState<PortfolioPerformance | null>(null);
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

  useEffect(() => {
    if (!selectedPortfolio?.id) {
      setPortfolioDetail(null);
      setPortfolioPerformance(null);
      return;
    }
    fetchPortfolioData(selectedPortfolio.id);
  }, [selectedPortfolio?.id]);

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

  const fetchPortfolioData = async (portfolioId: string) => {
    try {
      const [detailRes, performanceRes] = await Promise.all([
        api.getPortfolioDetail(portfolioId).catch(() => null),
        api.getPortfolioPerformance(portfolioId).catch(() => null),
      ]);
      setPortfolioDetail(detailRes?.data ?? null);
      setPortfolioPerformance(performanceRes?.data ?? null);
    } catch (error) {
      console.error('Failed to fetch portfolio data:', error);
      setPortfolioDetail(null);
      setPortfolioPerformance(null);
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

  const handleCancel = () => {
    setIsEditing(false);
    setIsCreating(false);
    setEditName("");
    setEditStocks({});
  };

  const handleSave = async () => {
    if (!editName.trim()) {
      alert("请输入组合名称");
      return;
    }
    if (Object.keys(editStocks).length === 0) {
      alert("请至少添加一只股票");
      return;
    }
    
    const totalWeight = Object.values(editStocks).reduce((sum, w) => sum + w, 0);
    if (Math.abs(totalWeight - 100) > 0.1) {
      alert("权重总和应为100%");
      return;
    }
    
    setSaving(true);
    try {
      if (isCreating) {
        await api.createPortfolio(editName, editStocks);
      } else if (selectedPortfolio) {
        await api.updatePortfolio(selectedPortfolio.id, editStocks);
      }
      await fetchPortfolios();
      handleCancel();
    } catch (error) {
      console.error('Failed to save portfolio:', error);
      alert("保存失败");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (portfolioId: string) => {
    if (!confirm("确定要删除这个组合吗？")) return;
    try {
      await api.deletePortfolio(portfolioId);
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

  const portfolio = selectedPortfolio;
  const positionsCount = Object.keys(portfolio?.stocks || {}).length;
  const holdings: Position[] = portfolioDetail?.positions || (
    portfolio
      ? Object.entries(portfolio.stocks).map(([code, weight]) => ({ code, weight }))
      : []
  );
  const performanceData = portfolioPerformance?.portfolio_values || [];
  const dailyReturns = portfolioPerformance?.daily_returns || [];
  const dailyReturn = dailyReturns.length > 0 ? dailyReturns[dailyReturns.length - 1].return : undefined;
  const formatPercent = (value?: number, signed = false) => {
    if (typeof value !== "number") return "暂无";
    const prefix = signed && value > 0 ? "+" : "";
    return `${prefix}${value}%`;
  };
  const formatNumber = (value?: number) => (typeof value === "number" ? String(value) : "暂无");
  const riskMetrics = [
    { name: "年化收益率", value: formatPercent(portfolioPerformance?.annual_return, true), color: "text-green-500" },
    { name: "夏普比率", value: formatNumber(portfolioPerformance?.sharpe_ratio), color: "text-blue-500" },
    { name: "最大回撤", value: formatPercent(portfolioPerformance?.max_drawdown), color: "text-red-500" },
    { name: "波动率", value: formatPercent(portfolioPerformance?.volatility), color: "text-yellow-500" },
    { name: "胜率", value: formatPercent(portfolioPerformance?.win_rate), color: "text-cyan-500" },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">组合管理</h1>
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
                className="flex-1 h-10 px-3 rounded-md border bg-background"
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
                  <Trash2 className="h-4 w-4 text-red-500" />
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
                      value={weight}
                      onChange={(e) => handleUpdateWeight(code, Number(e.target.value))}
                      className="w-24"
                    />
                    <span className="text-sm">%</span>
                    <Button variant="ghost" size="sm" onClick={() => handleRemoveStock(code)}>
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex items-center gap-3">
              <Input
                type="text"
                placeholder="股票代码 (如: 600519)"
                value={newStockCode}
                onChange={(e) => setNewStockCode(e.target.value)}
                className="flex-1"
              />
              <Input
                type="number"
                placeholder="权重"
                value={newStockWeight}
                onChange={(e) => setNewStockWeight(Number(e.target.value))}
                className="w-24"
              />
              <Button onClick={handleAddStock}>
                <Plus className="h-4 w-4 mr-2" />
                添加
              </Button>
            </div>

            <div className="text-sm text-muted-foreground">
              总权重: {Math.round(Object.values(editStocks).reduce((sum, w) => sum + w, 0) * 10) / 10}%
              <span className={`ml-2 ${Math.abs(Object.values(editStocks).reduce((sum, w) => sum + w, 0) - 100) < 0.1 ? 'text-green-500' : 'text-yellow-500'}`}>
                {Math.abs(Object.values(editStocks).reduce((sum, w) => sum + w, 0) - 100) < 0.1 ? '✓ 权重正常' : '⚠ 权重应为100%'}
              </span>
            </div>
          </CardContent>
        </Card>
      ) : portfolio ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">总资产</p>
                  <p className="text-2xl font-bold mt-1 text-muted-foreground">暂无</p>
                </div>
                <div className="h-12 w-12 rounded-xl bg-primary/10 flex items-center justify-center">
                  <Briefcase className="h-6 w-6 text-primary" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">总收益率</p>
                  <p className="text-2xl font-bold mt-1 text-green-500">
                    {formatPercent(portfolioPerformance?.total_return, true)}
                  </p>
                </div>
                <div className="h-12 w-12 rounded-xl bg-green-500/10 flex items-center justify-center">
                  <TrendingUp className="h-6 w-6 text-green-500" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">日收益率</p>
                  <p className="text-2xl font-bold mt-1 text-green-500">
                    {formatPercent(typeof dailyReturn === "number" ? dailyReturn * 100 : undefined, true)}
                  </p>
                </div>
                <div className="h-12 w-12 rounded-xl bg-blue-500/10 flex items-center justify-center">
                  <ArrowUpRight className="h-6 w-6 text-blue-500" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">持仓数量</p>
                  <p className="text-2xl font-bold mt-1">{positionsCount}</p>
                </div>
                <div className="h-12 w-12 rounded-xl bg-purple-500/10 flex items-center justify-center">
                  <PieChart className="h-6 w-6 text-purple-500" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      ) : (
        <Card>
          <CardContent className="p-12 text-center">
            <p className="text-muted-foreground">暂无组合，请创建新组合</p>
            <Button onClick={handleCreate} className="mt-4">
              <Plus className="h-4 w-4 mr-2" />
              创建组合
            </Button>
          </CardContent>
        </Card>
      )}

      {portfolio && !isEditing && !isCreating && (
        <>
          <Card>
            <CardHeader>
              <CardTitle>收益走势</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                {performanceData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={performanceData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                      <XAxis dataKey="date" stroke="#888" />
                      <YAxis stroke="#888" />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'rgba(0,0,0,0.8)',
                          border: '1px solid rgba(255,255,255,0.1)',
                          borderRadius: '8px'
                        }}
                      />
                      <Area
                        type="monotone"
                        dataKey="value"
                        stroke="#4CAF50"
                        fill="rgba(76, 175, 80, 0.2)"
                        name="组合权益"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex h-full items-center justify-center text-muted-foreground">暂无收益走势</div>
                )}
              </div>
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>持仓明细</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {holdings.map((position) => (
                    <div key={position.code} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                      <div>
                        <p className="font-medium">{position.code}</p>
                        <p className="text-sm text-muted-foreground">权重 {position.weight}%</p>
                      </div>
                      <div className="text-right">
                        <p className="font-medium">
                          {typeof position.price === "number" ? `¥${position.price.toFixed(2)}` : "暂无价格"}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>行业分布</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-[250px]">
                  <div className="flex h-full items-center justify-center text-muted-foreground">暂无行业分布数据</div>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>风险指标</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                {riskMetrics.map((metric) => (
                  <div key={metric.name} className="p-4 rounded-xl bg-muted/50">
                    <p className="text-sm text-muted-foreground">{metric.name}</p>
                    <p className={`text-2xl font-bold mt-1 ${metric.color}`}>{metric.value}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
