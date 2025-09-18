import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

def fetch_stock_data(tickers):
    """Fetch stock data for multiple tickers"""
    all_data = []
    
    print(f"Fetching {len(tickers)} tickers for last 10 years...")
    
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period="10y", auto_adjust=False)
            
            if not data.empty:
                data = data.reset_index()
                data['ticker'] = ticker
                
                data = data.rename(columns={
                    'Date': 'date',
                    'Open': 'open_price',
                    'High': 'high_price', 
                    'Low': 'low_price',
                    'Close': 'close_price',
                    'Adj Close': 'adj_close_price',
                    'Volume': 'volume'
                })
                data = data[['ticker', 'date', 'open_price', 'high_price', 'low_price', 'close_price', 'adj_close_price', 'volume']]
                all_data.append(data)
            else:
                print(f"✗ {ticker}: No data found")
                
        except Exception as e:
            print(f"✗ {ticker}: Error - {e}")
    
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

def fill_missing_data(df, method='interpolation'):
    """Fill missing data using different methods"""
    print(f"Filling missing data...")
    
    filled_data = []
    
    for ticker in df['ticker'].unique():
        ticker_data = df[df['ticker'] == ticker].copy()
        
        # Create full business date range (excludes weekends)
        full_range = pd.bdate_range(start=ticker_data['date'].min(),
                                  end=ticker_data['date'].max())
        
        # Find missing dates
        missing_dates = full_range.difference(ticker_data['date'])
        
        if len(missing_dates) > 0:
            
            # Create missing rows
            missing_rows = pd.DataFrame({
                'ticker': ticker,
                'date': missing_dates,
                'open_price': np.nan,
                'high_price': np.nan,
                'low_price': np.nan,
                'close_price': np.nan,
                'volume': np.nan
            })
            
            # Combine and sort
            ticker_data = pd.concat([ticker_data, missing_rows], ignore_index=True)
            ticker_data = ticker_data.sort_values('date').reset_index(drop=True)
            
            # Fill missing values
            if method == 'interpolation':
                ticker_data = ticker_data.interpolate()
            elif method == 'backward':
                ticker_data = ticker_data.bfill()
            elif method == 'forward':
                ticker_data = ticker_data.ffill()
        
        filled_data.append(ticker_data)
    
    return pd.concat(filled_data, ignore_index=True)

def calculate_metrics(df):
    """Calculate basic stock metrics for each ticker"""
    print("Calculating metrics...")
    
    metrics_data = []
    
    for ticker in df['ticker'].unique():
        ticker_data = df[df['ticker'] == ticker].copy().sort_values('date')
        
        # Daily returns
        ticker_data['daily_return'] = ticker_data['close_price'].pct_change()
        
        # Cumulative returns
        ticker_data['cumulative_return'] = (1 + ticker_data['daily_return']).cumprod() - 1
        
        # Rolling volatility (30-day)
        ticker_data['volatility'] = ticker_data['daily_return'].rolling(window=30).std()
        
        metrics_data.append(ticker_data)
    
    return pd.concat(metrics_data, ignore_index=True)

def generate_training_csv():
    """Generate comprehensive training dataset"""
    tickers = [
        "AAPL","MSFT","GOOG","META","AMZN","NFLX","TSLA",
        "NVDA","AMD","INTC","QCOM","AVGO","MU","TXN","AMAT","LRCX",
        "CRM","ORCL","ADBE","NOW","SNOW","DDOG","SHOP","MDB",
        "CSCO","IBM","HPE","DELL","HPQ","ANET",
        "PYPL","V","MA"
    ]
    
    # Step 1: Fetch raw data (using 10y period)
    df = fetch_stock_data(tickers)
    
    if df.empty:
        print("No data fetched!")
        return
    
    # Step 2: Fill missing data
    df_filled = fill_missing_data(df, method='interpolation')
    
    # Step 3: Calculate metrics
    df_final = calculate_metrics(df_filled)
    
    # Step 4: Clean and sort
    df_final = df_final.sort_values(['ticker', 'date']).reset_index(drop=True)
    
    # Step 5: Save to CSV
    filename = 'data/processed_tech_stock_data.csv'
    df_final.to_csv(filename, index=False)
    
    print(f"\n✓ Dataset saved to {filename}")
    print(f"Records: {len(df_final)}, Tickers: {df_final['ticker'].nunique()}, Columns: {len(df_final.columns)}")
    print(f"Date range: {df_final['date'].min()} to {df_final['date'].max()}")
    
    
    return filename

if __name__ == "__main__":
    generate_training_csv()