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
   python3 stock_data_fetcher.py sample
   ```

## Running the Code

### Stock Data Fetcher

**Command Line Interface:**
```bash
# Fetch sample data (AAPL, GOOGL, MSFT, TSLA, AMZN - last 30 days)
python3 stock_data_fetcher.py sample

# Fetch custom stocks with date range
python3 stock_data_fetcher.py fetch AAPL,MSFT,GOOGL 2024-01-01 2024-12-01
```

**Interactive Menu:**
```bash
python3 stock_data_fetcher.py
```

**Options:**
1. **Sample Data** - Predefined tech stocks (AAPL, GOOGL, MSFT, TSLA, AMZN) for last 30 days
2. **Custom Data** - User-specified symbols and date ranges (YYYY-MM-DD format)

### Portfolio Manager

**Command Line Interface:**
```bash
# Create user
python3 portfolio_manager.py create-user john

# List all users
python3 portfolio_manager.py list-users

# Create portfolio for user
python3 portfolio_manager.py create-portfolio john "My Portfolio"

# Remove portfolio from user
python3 portfolio_manager.py remove-portfolio john "My Portfolio"

# Add stock to user's portfolio
python3 portfolio_manager.py add john "My Portfolio" AAPL

# Remove stock from user's portfolio
python3 portfolio_manager.py remove john "My Portfolio" AAPL

# Display user's portfolios
python3 portfolio_manager.py display john

# Fetch portfolio data for user
python3 portfolio_manager.py fetch john "My Portfolio" 2024-01-01 2024-12-31
```

**Interactive Menu:**
```bash
python3 portfolio_manager.py
```

### Menu Options:
1. **Create User** - Create a new user with unique ID
2. **List Users** - Display all registered users
3. **Create Portfolio** - Create a new portfolio for a user
4. **Remove Portfolio** - Remove a portfolio from a user
5. **Add Stock to Portfolio** - Add a validated stock symbol to a user's portfolio
6. **Remove Stock from Portfolio** - Remove a stock from a user's portfolio
7. **Display User Portfolios** - Show all portfolios for a specific user
8. **Fetch Portfolio Data** - Download historical data for all stocks in a user's portfolio
9. **Exit** - Close the application

## Features

- **User Management** - Create users with unique IDs and usernames
- **Multi-User Support** - Each user can have multiple portfolios
- **Portfolio Management** - Create and manage portfolios per user
- **Stock Operations** - Add/remove stocks with validation
- **Data Fetching** - Fetch historical stock data for user portfolios
- **Portfolio Display** - Show user-specific portfolios with creation dates and stock lists
- **Stock Validation** - Only allow stocks with fetched data in database
- **Stock Symbol Validation** - Validate stock symbols using yfinance API
- **Data Integrity** - Users can only add stocks that have historical data available

## Database Schema

- `users`: Store user information with unique IDs and usernames
- `portfolios`: Store portfolio information linked to users
- `portfolio_stocks`: Link stocks to portfolios
- `stock_data`: Store historical stock price data
