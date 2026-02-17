"use client";

import EChart, {
  createLineChartOption,
  createBarChartOption,
  createPieChartOption,
  createScatterChartOption,
  createCandlestickChartOption,
  createRadarChartOption,
  createHeatmapChartOption,
} from "./EChart";

interface LineChartProps {
  data: any[];
  xAxisKey: string;
  yAxisKey: string;
  title?: string;
  color?: string;
  height?: number;
}

export function LineChart({
  data,
  xAxisKey,
  yAxisKey,
  title,
  color,
  height = 400,
}: LineChartProps) {
  const option = createLineChartOption(data, xAxisKey, yAxisKey, title, color);

  return (
    <EChart
      option={option}
      style={{ height: `${height}px` }}
      className="w-full"
    />
  );
}

interface BarChartProps {
  data: any[];
  xAxisKey: string;
  yAxisKey: string;
  title?: string;
  color?: string;
  height?: number;
}

export function BarChart({
  data,
  xAxisKey,
  yAxisKey,
  title,
  color,
  height = 400,
}: BarChartProps) {
  const option = createBarChartOption(data, xAxisKey, yAxisKey, title, color);

  return (
    <EChart
      option={option}
      style={{ height: `${height}px` }}
      className="w-full"
    />
  );
}

interface PieChartProps {
  data: any[];
  nameKey: string;
  valueKey: string;
  title?: string;
  height?: number;
}

export function PieChart({
  data,
  nameKey,
  valueKey,
  title,
  height = 400,
}: PieChartProps) {
  const option = createPieChartOption(data, nameKey, valueKey, title);

  return (
    <EChart
      option={option}
      style={{ height: `${height}px` }}
      className="w-full"
    />
  );
}

interface ScatterChartProps {
  data: any[];
  xKey: string;
  yKey: string;
  title?: string;
  height?: number;
}

export function ScatterChart({
  data,
  xKey,
  yKey,
  title,
  height = 400,
}: ScatterChartProps) {
  const option = createScatterChartOption(data, xKey, yKey, title);

  return (
    <EChart
      option={option}
      style={{ height: `${height}px` }}
      className="w-full"
    />
  );
}

interface CandlestickChartProps {
  data: any[];
  title?: string;
  height?: number;
}

export function CandlestickChart({
  data,
  title,
  height = 400,
}: CandlestickChartProps) {
  const option = createCandlestickChartOption(data, title);

  return (
    <EChart
      option={option}
      style={{ height: `${height}px` }}
      className="w-full"
    />
  );
}

interface RadarChartProps {
  data: any[];
  indicators: any[];
  title?: string;
  height?: number;
}

export function RadarChart({
  data,
  indicators,
  title,
  height = 400,
}: RadarChartProps) {
  const option = createRadarChartOption(data, indicators, title);

  return (
    <EChart
      option={option}
      style={{ height: `${height}px` }}
      className="w-full"
    />
  );
}

interface HeatmapChartProps {
  data: any[];
  xAxisData: any[];
  yAxisData: any[];
  title?: string;
  height?: number;
}

export function HeatmapChart({
  data,
  xAxisData,
  yAxisData,
  title,
  height = 400,
}: HeatmapChartProps) {
  const option = createHeatmapChartOption(data, xAxisData, yAxisData, title);

  return (
    <EChart
      option={option}
      style={{ height: `${height}px` }}
      className="w-full"
    />
  );
}
