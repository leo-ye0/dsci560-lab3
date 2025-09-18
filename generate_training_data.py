import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

def fetch_stock_data(tickers, start_date, end_date):
    """Fetch stock data for multiple tickers"""
    all_data = []
    
    print(f"Fetching data for {len(tickers)} tickers from {start_date} to {end_date}...")
    
    for ticker in tickers:
        try:
            print(f"Fetching {ticker}...")
            stock = yf.Ticker(ticker)
            data = stock.history(start=start_date, end=end_date)
            
            if not data.empty:
                data = data.reset_index()
                data['ticker'] = ticker
                data = data.rename(columns={
                    'Date': 'date',
                    'Open': 'open_price',
                    'High': 'high_price', 
                    'Low': 'low_price',
                    'Close': 'close_price',
                    'Volume': 'volume'
                })
                data = data[['ticker', 'date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume']]
                all_data.append(data)
                print(f"✓ {ticker}: {len(data)} records")
            else:
                print(f"✗ {ticker}: No data found")
                
        except Exception as e:
            print(f"✗ {ticker}: Error - {e}")
    
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

def fill_missing_data(df, method='interpolation'):
    """Fill missing data using different methods"""
    print(f"\nFilling missing data using {method}...")
    
    filled_data = []
    
    for ticker in df['ticker'].unique():
        ticker_data = df[df['ticker'] == ticker].copy()
        
        # Create full date range
        full_range = pd.date_range(start=ticker_data['date'].min(),
                                 end=ticker_data['date'].max(),
                                 freq='D')
        
        # Find missing dates
        missing_dates = full_range.difference(ticker_data['date'])
        
        if len(missing_dates) > 0:
            print(f"Filling {len(missing_dates)} missing dates for {ticker}")
            
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
    """Calculate stock metrics for each ticker"""
    print("\nCalculating stock metrics...")
    
    metrics_data = []
    
    for ticker in df['ticker'].unique():
        ticker_data = df[df['ticker'] == ticker].copy().sort_values('date')
        
        # Daily returns
        ticker_data['daily_return'] = ticker_data['close_price'].pct_change()
        
        # Cumulative returns
        ticker_data['cumulative_return'] = (1 + ticker_data['daily_return']).cumprod() - 1
        
        # Rolling volatility (30-day)
        ticker_data['volatility_30d'] = ticker_data['daily_return'].rolling(window=30).std()
        
        # Price change from previous day
        ticker_data['price_change'] = ticker_data['close_price'].diff()
        ticker_data['price_change_pct'] = ticker_data['price_change'] / ticker_data['close_price'].shift(1) * 100
        
        # Moving averages
        ticker_data['ma_7'] = ticker_data['close_price'].rolling(window=7).mean()
        ticker_data['ma_30'] = ticker_data['close_price'].rolling(window=30).mean()
        ticker_data['ma_90'] = ticker_data['close_price'].rolling(window=90).mean()
        
        # Volume metrics
        ticker_data['volume_ma_30'] = ticker_data['volume'].rolling(window=30).mean()
        ticker_data['volume_ratio'] = ticker_data['volume'] / ticker_data['volume_ma_30']
        
        # High-Low spread
        ticker_data['hl_spread'] = ticker_data['high_price'] - ticker_data['low_price']
        ticker_data['hl_spread_pct'] = ticker_data['hl_spread'] / ticker_data['close_price'] * 100
        
        # Day of week feature (0=Monday, 6=Sunday)
        ticker_data['day_of_week'] = pd.to_datetime(ticker_data['date']).dt.dayofweek
        
        metrics_data.append(ticker_data)
        print(f"✓ Calculated metrics for {ticker}")
    
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
    
    start_date = "2020-09-17"
    end_date = "2025-09-17"
    
    # Step 1: Fetch raw data
    df = fetch_stock_data(tickers, start_date, end_date)
    
    if df.empty:
        print("No data fetched!")
        return
    
    print(f"\nRaw data: {len(df)} records")
    
    # Step 2: Fill missing data
    df_filled = fill_missing_data(df, method='interpolation')
    print(f"After filling: {len(df_filled)} records")
    
    # Step 3: Calculate metrics
    df_final = calculate_metrics(df_filled)
    
    # Step 4: Clean and sort
    df_final = df_final.sort_values(['ticker', 'date']).reset_index(drop=True)
    
    # Step 5: Save to CSV
    filename = 'training_stock_data_complete.csv'
    df_final.to_csv(filename, index=False)
    
    print(f"\n✓ Complete training data saved to {filename}")
    print(f"Total records: {len(df_final)}")
    print(f"Columns: {list(df_final.columns)}")
    print(f"Date range: {df_final['date'].min()} to {df_final['date'].max()}")
    print(f"Tickers: {df_final['ticker'].nunique()}")
    
    # Show sample
    print(f"\nSample data:")
    print(df_final[['ticker', 'date', 'close_price', 'daily_return', 'volatility_30d']].head(10))
    
    return filename

if __name__ == "__main__":
    generate_training_csv()