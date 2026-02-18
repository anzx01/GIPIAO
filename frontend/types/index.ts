// 通用类型定义

export interface StockInfo {
  code: string;
  name: string;
  close?: number;
  open?: number;
  high?: number;
  low?: number;
  volume?: number;
  pct_change?: number;
}

export interface StockScore {
  code: string;
  name?: string;
  total_score: number;
  pe_score?: number;
  pb_score?: number;
  roe_score?: number;
  momentum_score?: number;
  volatility_score?: number;
  liquidity_score?: number;
  sentiment_score?: number;
  pe?: number;
  pb?: number;
  roe?: number;
  rank?: number;
  change?: number;
  industry?: string;
}

export interface NewsItem {
  title: string;
  time: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  content?: string;
  source?: string;
  url?: string;
}

export interface TechnicalIndicator {
  name: string;
  value: number;
  signal: string;
}

export interface PriceData {
  date: string;
  close: number;
  open?: number;
  high?: number;
  low?: number;
  volume?: number;
}

export interface FactorData {
  factor: string;
  value: number;
  fullMark: number;
}

export interface StockDetail {
  code: string;
  name: string;
  price: number;
  change: number;
  volume: number;
  amount: number;
  pe: number;
  pb: number;
  marketCap: number;
}

export interface Portfolio {
  id: string;
  name: string;
  stocks: Record<string, number>;
  created_at: string;
  updated_at: string;
}

export interface BacktestResult {
  id: string;
  portfolio_id?: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  final_value: number;
  total_return: number;
  annual_return: number;
  max_drawdown: number;
  sharpe_ratio: number;
  volatility: number;
  win_rate: number;
  trading_days: number;
}

export interface MarketSummary {
  total_stocks: number;
  up_count: number;
  down_count: number;
  up_rate: number;
  total_volume?: number;
  total_amount?: number;
}

export interface RiskMetric {
  name: string;
  value: number;
  status: string;
}

export interface ApiResponse<T> {
  code: number;
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}
