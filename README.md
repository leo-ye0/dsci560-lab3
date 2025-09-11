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

## Usage

Run the portfolio manager:
```bash
python portfolio_manager.py
```

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