import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from database_config import DatabaseConfig

class StockDataFetcher:
    def __init__(self):
        self.db_config = DatabaseConfig()
    
    def validate_stock(self, symbol):
        """Validate if stock symbol exists in yfinance"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return 'symbol' in info or 'shortName' in info
        except:
            return False
    
    def fetch_stock_data(self, symbols, start_date, end_date):
        """Fetch stock data for given symbols and date range"""
        connection = self.db_config.get_connection()
        if not connection:
            return False
        
        cursor = connection.cursor()
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(start=start_date, end=end_date)
                
                for date, row in data.iterrows():
                    insert_query = """
                    INSERT IGNORE INTO stock_data 
                    (stock_symbol, date, open_price, high_price, low_price, close_price, volume)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (
                        symbol,
                        date.date(),
                        float(row['Open']),
                        float(row['High']),
                        float(row['Low']),
                        float(row['Close']),
                        int(row['Volume'])
                    ))
                
                print(f"Data fetched for {symbol}")
                
            except Exception as e:
                print(f"Error fetching data for {symbol}: {e}")
        
        connection.commit()
        cursor.close()
        connection.close()
        return True
    
    def populate_sample_data(self):
        """Populate database with sample stock data"""
        # Sample tech stocks (change as needed)
        symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        return self.fetch_stock_data(symbols, start_date, end_date)

if __name__ == "__main__":
    fetcher = StockDataFetcher()
    print("Populating sample stock data...")
    if fetcher.populate_sample_data():
        print("Sample data populated successfully!")
    else:
        print("Failed to populate sample data.")