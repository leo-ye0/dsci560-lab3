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

**Command Line Interface:**
```bash
# Create user
python3 portfolio_manager.py create-user john

# Create portfolio for user
python3 portfolio_manager.py create-portfolio john "My Portfolio"

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
4. **Add Stock to Portfolio** - Add a validated stock symbol to a user's portfolio
5. **Remove Stock from Portfolio** - Remove a stock from a user's portfolio
6. **Display User Portfolios** - Show all portfolios for a specific user
7. **Fetch Portfolio Data** - Download historical data for all stocks in a user's portfolio
8. **Exit** - Close the application

## Features

- **User Management** - Create users with unique IDs and usernames
- **Multi-User Support** - Each user can have multiple portfolios
- **Portfolio Management** - Create and manage portfolios per user
- **Stock Operations** - Add/remove stocks with validation
- **Data Fetching** - Fetch historical stock data for user portfolios
- **Portfolio Display** - Show user-specific portfolios with creation dates and stock lists
- **Stock Validation** - Validate stock symbols using yfinance API

## Database Schema

- `users`: Store user information with unique IDs and usernames
- `portfolios`: Store portfolio information linked to users
- `portfolio_stocks`: Link stocks to portfolios
- `stock_data`: Store historical stock price data
