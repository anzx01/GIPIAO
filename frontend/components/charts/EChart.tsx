"use client";

import { useEffect, useRef } from "react";
import * as echarts from "echarts/core";
import {
  LineChart,
  BarChart,
  PieChart,
  ScatterChart,
  EffectScatterChart,
  LinesChart,
  HeatmapChart,
  GraphChart,
  TreeChart,
  TreemapChart,
  SunburstChart,
  BoxplotChart,
  CandlestickChart,
  RadarChart,
  ParallelChart,
  SankeyChart,
  FunnelChart,
  GaugeChart,
  WordCloudChart,
  Chart,
} from "echarts/charts";
import {
  GridComponent,
  TooltipComponent,
  TitleComponent,
  LegendComponent,
  DataZoomComponent,
  ToolboxComponent,
  MarkPointComponent,
  MarkLineComponent,
  DatasetComponent,
  TransformComponent,
} from "echarts/components";
import { LabelLayout, UniversalTransition } from "echarts/features";
import { CanvasRenderer } from "echarts/renderers";

echarts.use([
  LineChart,
  BarChart,
  PieChart,
  ScatterChart,
  EffectScatterChart,
  LinesChart,
  HeatmapChart,
  GraphChart,
  TreeChart,
  TreemapChart,
  SunburstChart,
  BoxplotChart,
  CandlestickChart,
  RadarChart,
  ParallelChart,
  SankeyChart,
  FunnelChart,
  GaugeChart,
  WordCloudChart,
  GridComponent,
  TooltipComponent,
  TitleComponent,
  LegendComponent,
  DataZoomComponent,
  ToolboxComponent,
  MarkPointComponent,
  MarkLineComponent,
  DatasetComponent,
  TransformComponent,
  LabelLayout,
  UniversalTransition,
  CanvasRenderer,
]);

interface ChartProps {
  option: any;
  style?: React.CSSProperties;
  className?: string;
  theme?: string | object;
  loading?: boolean;
}

export default function EChart({
  option,
  style,
  className,
  theme,
  loading = false,
}: ChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (chartRef.current) {
      chartInstance.current = echarts.init(chartRef.current, theme);
    }

    const handleResize = () => {
      chartInstance.current?.resize();
    };

    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chartInstance.current?.dispose();
    };
  }, [theme]);

  useEffect(() => {
    if (chartInstance.current) {
      if (loading) {
        chartInstance.current.showLoading();
      } else {
        chartInstance.current.hideLoading();
      }
    }
  }, [loading]);

  useEffect(() => {
    if (chartInstance.current && option) {
      chartInstance.current.setOption(option, true);
    }
  }, [option]);

  return <div ref={chartRef} style={style} className={className} />;
}

export function createLineChartOption(
  data: any[],
  xAxisKey: string,
  yAxisKey: string,
  title?: string,
  color?: string
) {
  return {
    title: {
      text: title,
      left: "center",
    },
    tooltip: {
      trigger: "axis",
    },
    xAxis: {
      type: "category",
      data: data.map((item) => item[xAxisKey]),
    },
    yAxis: {
      type: "value",
    },
    series: [
      {
        data: data.map((item) => item[yAxisKey]),
        type: "line",
        smooth: true,
        itemStyle: {
          color: color || "#1a73e8",
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "rgba(26, 115, 232, 0.3)" },
            { offset: 1, color: "rgba(26, 115, 232, 0.05)" },
          ]),
        },
      },
    ],
  };
}

export function createBarChartOption(
  data: any[],
  xAxisKey: string,
  yAxisKey: string,
  title?: string,
  color?: string
) {
  return {
    title: {
      text: title,
      left: "center",
    },
    tooltip: {
      trigger: "axis",
    },
    xAxis: {
      type: "category",
      data: data.map((item) => item[xAxisKey]),
    },
    yAxis: {
      type: "value",
    },
    series: [
      {
        data: data.map((item) => item[yAxisKey]),
        type: "bar",
        itemStyle: {
          color: color || "#1a73e8",
        },
      },
    ],
  };
}

export function createPieChartOption(
  data: any[],
  nameKey: string,
  valueKey: string,
  title?: string
) {
  return {
    title: {
      text: title,
      left: "center",
    },
    tooltip: {
      trigger: "item",
    },
    legend: {
      orient: "vertical",
      left: "left",
    },
    series: [
      {
        name: title,
        type: "pie",
        radius: "50%",
        data: data.map((item) => ({
          name: item[nameKey],
          value: item[valueKey],
        })),
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: "rgba(0, 0, 0, 0.5)",
          },
        },
      },
    ],
  };
}

export function createScatterChartOption(
  data: any[],
  xKey: string,
  yKey: string,
  title?: string
) {
  return {
    title: {
      text: title,
      left: "center",
    },
    tooltip: {
      trigger: "item",
    },
    xAxis: {
      type: "value",
      name: xKey,
    },
    yAxis: {
      type: "value",
      name: yKey,
    },
    series: [
      {
        symbolSize: 10,
        data: data.map((item) => [item[xKey], item[yKey]]),
        type: "scatter",
      },
    ],
  };
}

export function createCandlestickChartOption(
  data: any[],
  title?: string
) {
  return {
    title: {
      text: title,
      left: "center",
    },
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "cross",
      },
    },
    xAxis: {
      data: data.map((item) => item.date),
    },
    yAxis: {
      scale: true,
      splitArea: {
        show: true,
      },
    },
    series: [
      {
        type: "candlestick",
        data: data.map((item) => [
          item.open,
          item.close,
          item.low,
          item.high,
        ]),
      },
    ],
  };
}

export function createRadarChartOption(
  data: any[],
  indicators: any[],
  title?: string
) {
  return {
    title: {
      text: title,
      left: "center",
    },
    tooltip: {
      trigger: "item",
    },
    legend: {
      data: data.map((item) => item.name),
    },
    radar: {
      indicator: indicators,
    },
    series: [
      {
        name: title,
        type: "radar",
        data: data.map((item) => ({
          value: item.values,
          name: item.name,
        })),
      },
    ],
  };
}

export function createHeatmapChartOption(
  data: any[],
  xAxisData: any[],
  yAxisData: any[],
  title?: string
) {
  return {
    title: {
      text: title,
      left: "center",
    },
    tooltip: {
      position: "top",
    },
    xAxis: {
      type: "category",
      data: xAxisData,
      splitArea: {
        show: true,
      },
    },
    yAxis: {
      type: "category",
      data: yAxisData,
      splitArea: {
        show: true,
      },
    },
    visualMap: {
      min: 0,
      max: 10,
      calculable: true,
      orient: "horizontal",
      left: "center",
      bottom: "15%",
    },
    series: [
      {
        name: title,
        type: "heatmap",
        data: data,
        label: {
          show: true,
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: "rgba(0, 0, 0, 0.5)",
          },
        },
      },
    ],
  };
}
