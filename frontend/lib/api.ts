const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('token');
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      (headers as Record<string, string>)['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  setToken(token: string) {
    this.token = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('token', token);
    }
  }

  clearToken() {
    this.token = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
    }
  }

  async login(username: string, password: string) {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await fetch(`${this.baseUrl}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Login failed');
    }

    const data = await response.json();
    this.setToken(data.access_token);
    return data;
  }

  async logout() {
    this.clearToken();
  }

  async getStockList(params?: { page?: number; page_size?: number; keyword?: string }) {
    const query = new URLSearchParams();
    if (params?.page) query.set('page', params.page.toString());
    if (params?.page_size) query.set('page_size', params.page_size.toString());
    if (params?.keyword) query.set('keyword', params.keyword);
    
    return this.request<any>(`/api/stocks/list?${query.toString()}`);
  }

  async getStockScores(topN: number = 10) {
    return this.request<any>(`/api/stocks/scores?top_n=${topN}`);
  }

  async getStockDetail(code: string, days: number = 60) {
    return this.request<any>(`/api/stocks/${code}?days=${days}`);
  }

  async getStockPrice(code: string, days: number = 30) {
    return this.request<any>(`/api/stocks/${code}/price?days=${days}`);
  }

  async getTechnicalIndicators(code: string, days: number = 60) {
    return this.request<any>(`/api/stocks/${code}/indicators?days=${days}`);
  }

  async getMarketSummary() {
    return this.request<any>('/api/market/summary');
  }

  async getMarketIndices() {
    return this.request<any>('/api/market/indices');
  }

  async getIndustryHeat() {
    return this.request<any>('/api/market/industry/heat');
  }

  async getSectorPerformance(days: number = 5) {
    return this.request<any>(`/api/market/sector/performance?days=${days}`);
  }

  async getPortfolioList() {
    return this.request<any>('/api/portfolio/list');
  }

  async getPortfolioDetail(portfolioId: string) {
    return this.request<any>(`/api/portfolio/${portfolioId}`);
  }

  async createPortfolio(name: string, stocks: Record<string, number>) {
    return this.request<any>('/api/portfolio/', {
      method: 'POST',
      body: JSON.stringify({ name, stocks }),
    });
  }

  async updatePortfolio(portfolioId: string, stocks: Record<string, number>) {
    return this.request<any>(`/api/portfolio/${portfolioId}`, {
      method: 'PUT',
      body: JSON.stringify({ stocks }),
    });
  }

  async runBacktest(
    portfolio: Record<string, number>,
    startDate?: string,
    endDate?: string,
    initialCapital?: number
  ) {
    return this.request<any>('/api/backtest/run', {
      method: 'POST',
      body: JSON.stringify({ portfolio, start_date: startDate, end_date: endDate, initial_capital: initialCapital }),
    });
  }

  async getBacktestHistory() {
    return this.request<any>('/api/backtest/history');
  }

  async compareStrategies(portfolios: Record<string, number>[], startDate?: string, endDate?: string) {
    return this.request<any>('/api/backtest/compare', {
      method: 'POST',
      body: JSON.stringify({ portfolios, start_date: startDate, end_date: endDate }),
    });
  }

  async getReportList(params?: { report_type?: string; page?: number; page_size?: number }) {
    const query = new URLSearchParams();
    if (params?.report_type) query.set('report_type', params.report_type);
    if (params?.page) query.set('page', params.page.toString());
    if (params?.page_size) query.set('page_size', params.page_size.toString());
    
    return this.request<any>(`/api/reports/list?${query.toString()}`);
  }

  async generateDailyReport() {
    return this.request<any>('/api/reports/generate/daily', {
      method: 'POST',
    });
  }

  async generateWeeklyReport() {
    return this.request<any>('/api/reports/generate/weekly', {
      method: 'POST',
    });
  }
}

export const api = new ApiClient();
export default api;
