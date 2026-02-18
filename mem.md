
# Project Memory

## Project Overview
AI Quant Research Hub (AIQRH) is an AI-driven stock quantitative research platform providing analysis, scoring, backtesting, and reporting.

## Frameworks and Technologies
- **Backend:** Python 3.10+, FastAPI, Uvicorn
- **Frontend:** Next.js 14, React 18, TypeScript, Tailwind CSS
- **Database:** MongoDB
- **Data Sources:** AkShare (default), Tushare (optional)
- **AI/ML:** Pandas, NumPy, Scikit-learn, LLM integration for sentiment

## Key Architecture
- **Core Engine:** `core/engine.py` manages the overall flow.
- **Skills System:** Modular components for different tasks:
  - `skill_data`: Data fetching and storage.
  - `skill_ai`: Analysis, scoring, and factor modeling.
  - `skill_risk`: Backtesting and risk metrics.
  - `skill_report`: Report generation.
  - `skill_ops`: Scheduling and logging.
- **API:** FastAPI routes in `api/routes/`.

## Conventions
- **Stock Codes:** A-share codes usually follow `600519.SH` or `000858.SZ` format.
- **Environment:** Backend runs on port 8001 (or 8002/8003 if occupied), Frontend on 3000.
- **Configuration:** `config.yaml` for business logic settings, `.env` for infrastructure/secrets.

## Implementation Details (Reusable)
- **Stock Scoring:** `StockScorer` in `skills/skill_ai/scorer.py` uses a weighted composite of financial (PE, PB, ROE, revenue growth), price (momentum, volatility), technical (MACD, RSI, KDJ), and sentiment factors.
- **Data Fetching:** `StockDataFetcher` in `skills/skill_data/fetcher.py` uses AkShare. It includes methods for fetching price data, financial indicators (PE, PB, ROE, Revenue Growth), and mapping stock codes to names.
- **Technical Indicators:** Standard indicators (MA, MACD, RSI, KDJ, Bollinger Bands) are calculated in `StockDataFetcher.calculate_technical_indicators`.
- **Security:** JWT authentication with secret key validation; mandatory strong password policy for users.
- **Error Handling:** Centralized API error handling with descriptive types (`network`, `auth`, `validation`, `server`).
- **Stock Code Handling:** A-share codes are typically handled as `600519.SH` or `000858.SZ`. The system automatically maps these to AkShare's expected format (e.g., `600519`).
- **News and Sentiment:** `NewsFetcher` in `skills/skill_data/news.py` fetches news from East Money (via AkShare) and performs keyword-based sentiment analysis for A-shares, returning scores between -1 and 1.
- **Storage Strategy:** `QuantEngine` supports both file-based (`DataStorage`) and MongoDB-based (`MongoDBStorage`) persistence. It defaults to file-based but switches to MongoDB if `database.mongodb_connection` is provided in `config.yaml`.
- **Report Generation:** Reports are generated using `PDFGenerator`. The data flow starts from `QuantEngine.run_daily_analysis`, which prepares a `report_payload` that is then consumed by the API routes to produce PDF/HTML reports.
