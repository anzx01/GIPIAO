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
  ArrowUpRight,
  ArrowDownRight,
  Filter,
  RefreshCw,
  ExternalLink,
} from "lucide-react";

interface Stock {
  code: string;
  name: string;
  score?: number;
  pe_score?: number;
  pb_score?: number;
  roe_score?: number;
  momentum_score?: number;
}

export default function StockListPage() {
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [filteredStocks, setFilteredStocks] = useState<Stock[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchKeyword, setSearchKeyword] = useState("");
  const [sortBy, setSortBy] = useState<"score" | "code" | "name">("score");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

  useEffect(() => {
    fetchStocks();
  }, []);

  useEffect(() => {
    filterAndSortStocks();
  }, [stocks, searchKeyword, sortBy, sortOrder]);

  const fetchStocks = async () => {
    try {
      const res = await api.getStockList(1, 100);
      if (res?.data?.items) {
        setStocks(res.data.items);
      }
    } catch (error) {
      console.error('Failed to fetch stocks:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchScores = async () => {
    try {
      const res = await api.getStockScores(50);
      if (res?.data?.items) {
        const scoreMap = new Map(res.data.items.map((s: any) => [s.code, s]));
        setStocks(prev => prev.map(stock => ({
          ...stock,
          ...scoreMap.get(stock.code)
        })));
      }
    } catch (error) {
      console.error('Failed to fetch scores:', error);
    }
  };

  const filterAndSortStocks = () => {
    let result = [...stocks];

    if (searchKeyword) {
      const keyword = searchKeyword.toLowerCase();
      result = result.filter(
        stock =>
          stock.code.toLowerCase().includes(keyword) ||
          (stock.name && stock.name.toLowerCase().includes(keyword))
      );
    }

    result.sort((a, b) => {
      let aValue, bValue;

      switch (sortBy) {
        case "score":
          aValue = a.score || 0;
          bValue = b.score || 0;
          break;
        case "code":
          aValue = a.code;
          bValue = b.code;
          break;
        case "name":
          aValue = a.name || "";
          bValue = b.name || "";
          break;
      }

      if (sortOrder === "asc") {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    setFilteredStocks(result);
  };

  const handleSort = (column: "score" | "code" | "name") => {
    if (sortBy === column) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy(column);
      setSortOrder("desc");
    }
  };

  const getScoreColor = (score?: number) => {
    if (!score) return "text-muted-foreground";
    if (score >= 80) return "text-success";
    if (score >= 60) return "text-warning";
    return "text-danger";
  };

  const getScoreBg = (score?: number) => {
    if (!score) return "bg-white/5";
    if (score >= 80) return "bg-success/10";
    if (score >= 60) return "bg-warning/10";
    return "bg-danger/10";
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-display font-bold">股票列表</h1>
          <p className="text-muted-foreground mt-1">浏览和筛选所有股票</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" onClick={fetchScores} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            刷新评分
          </Button>
        </div>
      </div>

      <Card>
        <CardContent className="p-6">
          <div className="flex items-center gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                type="search"
                placeholder="搜索股票代码或名称..."
                className="pl-10"
                value={searchKeyword}
                onChange={(e) => setSearchKeyword(e.target.value)}
              />
            </div>
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-muted-foreground" />
              <select
                className="h-10 px-3 rounded-md border border-white/10 bg-white/5 text-foreground"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
              >
                <option value="score">按评分</option>
                <option value="code">按代码</option>
                <option value="name">按名称</option>
              </select>
              <Button
                variant="outline"
                size="icon"
                onClick={() => setSortOrder(sortOrder === "asc" ? "desc" : "asc")}
              >
                {sortOrder === "asc" ? (
                  <ArrowUpRight className="h-4 w-4" />
                ) : (
                  <ArrowDownRight className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg">
            股票列表 ({filteredStocks.length} 只)
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : filteredStocks.length === 0 ? (
            <div className="text-center py-12">
              <Search className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <p className="text-muted-foreground">未找到匹配的股票</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/5">
                    <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">
                      <button
                        className="flex items-center gap-1 hover:text-foreground"
                        onClick={() => handleSort("code")}
                      >
                        股票代码
                        {sortBy === "code" && (
                          <span className="text-xs">
                            {sortOrder === "asc" ? "↑" : "↓"}
                          </span>
                        )}
                      </button>
                    </th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">
                      <button
                        className="flex items-center gap-1 hover:text-foreground"
                        onClick={() => handleSort("name")}
                      >
                        名称
                        {sortBy === "name" && (
                          <span className="text-xs">
                            {sortOrder === "asc" ? "↑" : "↓"}
                          </span>
                        )}
                      </button>
                    </th>
                    <th className="text-center py-3 px-4 text-sm font-medium text-muted-foreground">
                      <button
                        className="flex items-center gap-1 hover:text-foreground"
                        onClick={() => handleSort("score")}
                      >
                        AI 评分
                        {sortBy === "score" && (
                          <span className="text-xs">
                            {sortOrder === "asc" ? "↑" : "↓"}
                          </span>
                        )}
                      </button>
                    </th>
                    <th className="text-center py-3 px-4 text-sm font-medium text-muted-foreground">估值</th>
                    <th className="text-center py-3 px-4 text-sm font-medium text-muted-foreground">动量</th>
                    <th className="text-center py-3 px-4 text-sm font-medium text-muted-foreground">质量</th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground">操作</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredStocks.map((stock, index) => (
                    <tr
                      key={stock.code}
                      className="border-b border-white/5 hover:bg-white/5 transition-colors"
                    >
                      <td className="py-3 px-4">
                        <span className="font-mono text-sm">{stock.code}</span>
                      </td>
                      <td className="py-3 px-4">
                        <span className="font-medium">{stock.name}</span>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center justify-center gap-2">
                          {stock.score !== undefined ? (
                            <>
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
                              <span
                                className={`text-sm font-medium ${getScoreColor(stock.score)}`}
                              >
                                {stock.score}
                              </span>
                            </>
                          ) : (
                            <span className="text-sm text-muted-foreground">-</span>
                          )}
                        </div>
                      </td>
                      <td className="py-3 px-4 text-center">
                        {stock.pe_score !== undefined ? (
                          <span className={`text-sm px-2 py-1 rounded-full ${getScoreBg(stock.pe_score)}`}>
                            {stock.pe_score}
                          </span>
                        ) : (
                          <span className="text-sm text-muted-foreground">-</span>
                        )}
                      </td>
                      <td className="py-3 px-4 text-center">
                        {stock.momentum_score !== undefined ? (
                          <span className={`text-sm px-2 py-1 rounded-full ${getScoreBg(stock.momentum_score)}`}>
                            {stock.momentum_score}
                          </span>
                        ) : (
                          <span className="text-sm text-muted-foreground">-</span>
                        )}
                      </td>
                      <td className="py-3 px-4 text-center">
                        {stock.roe_score !== undefined ? (
                          <span className={`text-sm px-2 py-1 rounded-full ${getScoreBg(stock.roe_score)}`}>
                            {stock.roe_score}
                          </span>
                        ) : (
                          <span className="text-sm text-muted-foreground">-</span>
                        )}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => window.location.href = `/stocks?code=${stock.code}`}
                        >
                          <ExternalLink className="h-4 w-4" />
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
