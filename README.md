# Stock Portfolio Management System

A Python-based stock portfolio management system using MySQL and yfinance API.

## Setup

1. **Install dependencies:**
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Setup MySQL database:**
   - Update database credentials in `database_config.py`
   - Run: `python setup_database.py`

3. **Populate sample data:**
   ```bash
   python stock_data_fetcher.py
   ```

## Running the Code

### Stock Data Fetcher

Run `python stock_data_fetcher.py` and choose between two options:

**Option 1: Sample Data**
- Uses predefined tech stocks: AAPL, GOOGL, MSFT, TSLA, AMZN
- Fetches last 30 days of data
- Quick setup for testing

**Option 2: Custom Data**
- Enter your own stock symbols (comma-separated, e.g., "AAPL,MSFT,NVDA")
- Specify custom date range (YYYY-MM-DD format)
- Example: Start date: 2024-01-01, End date: 2024-12-31

### Portfolio Manager

Run the portfolio manager:
```bash
python portfolio_manager.py
```

### Menu Options:
1. **Create Portfolio** - Create a new portfolio with a custom name
2. **Add Stock to Portfolio** - Add a validated stock symbol to an existing portfolio
3. **Remove Stock from Portfolio** - Remove a stock from an existing portfolio
4. **Display All Portfolios** - Show all portfolios with creation dates and stock lists
5. **Fetch Portfolio Data** - Download historical data for all stocks in a portfolio
6. **Exit** - Close the application

## Features

- Create and manage multiple portfolios
- Add/remove stocks with validation
- Fetch historical stock data for portfolios
- Display all portfolios with creation dates and stock lists
- Validate stock symbols using yfinance API

## Database Schema

- `portfolios`: Store portfolio information
- `portfolio_stocks`: Link stocks to portfolios
- `stock_data`: Store historical stock price data