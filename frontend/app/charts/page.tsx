"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  LineChart as ELineChart,
  BarChart as EBarChart,
  PieChart as EPieChart,
  ScatterChart as EScatterChart,
  CandlestickChart as ECandlestickChart,
  RadarChart as ERadarChart,
  HeatmapChart as EHeatmapChart,
} from "@/components/charts";
import {
  TrendingUp,
  TrendingDown,
  BarChart3,
  PieChart as PieChartIcon,
  Scatter,
  Activity,
} from "lucide-react";

export default function ChartsPage() {
  const [activeTab, setActiveTab] = useState<"line" | "bar" | "pie" | "scatter" | "candlestick" | "radar" | "heatmap">("line");

  const lineData = [
    { date: "2024-01", value: 100 },
    { date: "2024-02", value: 120 },
    { date: "2024-03", value: 110 },
    { date: "2024-04", value: 140 },
    { date: "2024-05", value: 130 },
    { date: "2024-06", value: 160 },
    { date: "2024-07", value: 150 },
    { date: "2024-08", value: 180 },
    { date: "2024-09", value: 170 },
    { date: "2024-10", value: 200 },
    { date: "2024-11", value: 190 },
    { date: "2024-12", value: 220 },
  ];

  const barData = [
    { name: "贵州茅台", value: 95.5 },
    { name: "宁德时代", value: 92.3 },
    { name: "比亚迪", value: 90.8 },
    { name: "五粮液", value: 89.5 },
    { name: "中国平安", value: 88.2 },
    { name: "招商银行", value: 87.5 },
    { name: "中芯国际", value: 86.8 },
    { name: "海康威视", value: 85.5 },
  ];

  const pieData = [
    { name: "白酒", value: 43 },
    { name: "金融", value: 27 },
    { name: "新能源", value: 15 },
    { name: "电力", value: 10 },
    { name: "现金", value: 5 },
  ];

  const scatterData = [
    { x: 10, y: 8.04 },
    { x: 8, y: 6.95 },
    { x: 13, y: 7.58 },
    { x: 9, y: 8.81 },
    { x: 11, y: 8.33 },
    { x: 14, y: 9.96 },
    { x: 6, y: 7.24 },
    { x: 4, y: 4.26 },
    { x: 12, y: 10.84 },
    { x: 7, y: 4.82 },
    { x: 5, y: 5.68 },
  ];

  const candlestickData = [
    { date: "2024-01-01", open: 100, close: 105, low: 98, high: 108 },
    { date: "2024-01-02", open: 105, close: 103, low: 100, high: 107 },
    { date: "2024-01-03", open: 103, close: 108, low: 102, high: 110 },
    { date: "2024-01-04", open: 108, close: 106, low: 104, high: 109 },
    { date: "2024-01-05", open: 106, close: 112, low: 105, high: 113 },
    { date: "2024-01-08", open: 112, close: 110, low: 108, high: 114 },
    { date: "2024-01-09", open: 110, close: 115, low: 109, high: 116 },
    { date: "2024-01-10", open: 115, close: 118, low: 113, high: 120 },
  ];

  const radarData = [
    {
      name: "贵州茅台",
      values: [95, 90, 88, 92, 85, 87],
    },
    {
      name: "宁德时代",
      values: [88, 95, 92, 85, 90, 88],
    },
    {
      name: "比亚迪",
      values: [82, 88, 95, 90, 85, 82],
    },
  ];

  const radarIndicators = [
    { name: "盈利能力", max: 100 },
    { name: "成长能力", max: 100 },
    { name: "运营能力", max: 100 },
    { name: "偿债能力", max: 100 },
    { name: "估值水平", max: 100 },
    { name: "技术面", max: 100 },
  ];

  const heatmapData = [
    [0, 0, 5],
    [0, 1, 3],
    [0, 2, 8],
    [1, 0, 2],
    [1, 1, 6],
    [1, 2, 4],
    [2, 0, 7],
    [2, 1, 9],
    [2, 2, 1],
  ];

  const heatmapXAxis = ["周一", "周二", "周三"];
  const heatmapYAxis = ["上午", "下午", "晚上"];

  const tabs = [
    { id: "line", label: "折线图", icon: Activity },
    { id: "bar", label: "柱状图", icon: BarChart3 },
    { id: "pie", label: "饼图", icon: PieChartIcon },
    { id: "scatter", label: "散点图", icon: Scatter },
    { id: "candlestick", label: "K线图", icon: TrendingUp },
    { id: "radar", label: "雷达图", icon: Activity },
    { id: "heatmap", label: "热力图", icon: BarChart3 },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-display font-bold">图表可视化</h1>
        <p className="text-muted-foreground mt-1">基于ECharts的交互式图表组件库</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>图表类型</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <Button
                  key={tab.id}
                  variant={activeTab === tab.id ? "default" : "outline"}
                  onClick={() => setActiveTab(tab.id as any)}
                  className="flex items-center gap-2"
                >
                  <Icon className="h-4 w-4" />
                  {tab.label}
                </Button>
              );
            })}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{tabs.find((t) => t.id === activeTab)?.label}</CardTitle>
        </CardHeader>
        <CardContent>
          {activeTab === "line" && (
            <ELineChart
              data={lineData}
              xAxisKey="date"
              yAxisKey="value"
              title="趋势分析"
              height={400}
            />
          )}

          {activeTab === "bar" && (
            <EBarChart
              data={barData}
              xAxisKey="name"
              yAxisKey="value"
              title="AI评分TOP8"
              height={400}
            />
          )}

          {activeTab === "pie" && (
            <EPieChart
              data={pieData}
              nameKey="name"
              valueKey="value"
              title="持仓分布"
              height={400}
            />
          )}

          {activeTab === "scatter" && (
            <EScatterChart
              data={scatterData}
              xKey="x"
              yKey="y"
              title="风险收益分布"
              height={400}
            />
          )}

          {activeTab === "candlestick" && (
            <ECandlestickChart
              data={candlestickData}
              title="股价走势"
              height={400}
            />
          )}

          {activeTab === "radar" && (
            <ERadarChart
              data={radarData}
              indicators={radarIndicators}
              title="股票综合评分"
              height={400}
            />
          )}

          {activeTab === "heatmap" && (
            <EHeatmapChart
              data={heatmapData}
              xAxisData={heatmapXAxis}
              yAxisData={heatmapYAxis}
              title="交易活跃度"
              height={400}
            />
          )}
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">使用说明</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 text-sm">
              <div>
                <p className="font-medium mb-1">折线图</p>
                <p className="text-muted-foreground">适用于展示数据随时间的变化趋势</p>
              </div>
              <div>
                <p className="font-medium mb-1">柱状图</p>
                <p className="text-muted-foreground">适用于比较不同类别的数据大小</p>
              </div>
              <div>
                <p className="font-medium mb-1">饼图</p>
                <p className="text-muted-foreground">适用于展示各部分占总体的比例</p>
              </div>
              <div>
                <p className="font-medium mb-1">散点图</p>
                <p className="text-muted-foreground">适用于展示两个变量之间的关系</p>
              </div>
              <div>
                <p className="font-medium mb-1">K线图</p>
                <p className="text-muted-foreground">适用于展示股票的开盘、收盘、最高、最低价</p>
              </div>
              <div>
                <p className="font-medium mb-1">雷达图</p>
                <p className="text-muted-foreground">适用于多维度数据的对比分析</p>
              </div>
              <div>
                <p className="font-medium mb-1">热力图</p>
                <p className="text-muted-foreground">适用于展示数据的密度或强度分布</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">特性</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 text-sm">
              <div className="flex items-start gap-2">
                <TrendingUp className="h-5 w-5 text-success mt-0.5" />
                <div>
                  <p className="font-medium">交互式图表</p>
                  <p className="text-muted-foreground">支持缩放、平移、提示框等交互功能</p>
                </div>
              </div>
              <div className="flex items-start gap-2">
                <TrendingUp className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <p className="font-medium">响应式设计</p>
                  <p className="text-muted-foreground">自动适应不同屏幕尺寸</p>
                </div>
              </div>
              <div className="flex items-start gap-2">
                <TrendingUp className="h-5 w-5 text-chart-2 mt-0.5" />
                <div>
                  <p className="font-medium">主题定制</p>
                  <p className="text-muted-foreground">支持自定义颜色和样式</p>
                </div>
              </div>
              <div className="flex items-start gap-2">
                <TrendingUp className="h-5 w-5 text-chart-3 mt-0.5" />
                <div>
                  <p className="font-medium">动画效果</p>
                  <p className="text-muted-foreground">流畅的过渡动画提升用户体验</p>
                </div>
              </div>
              <div className="flex items-start gap-2">
                <TrendingUp className="h-5 w-5 text-chart-4 mt-0.5" />
                <div>
                  <p className="font-medium">数据导出</p>
                  <p className="text-muted-foreground">支持图表数据导出为图片或数据文件</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
