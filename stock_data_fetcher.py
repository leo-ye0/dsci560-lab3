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

def main():
    import sys
    fetcher = StockDataFetcher()
    
    # Command line interface
    if len(sys.argv) > 1:
        action = sys.argv[1]
        
        if action == "sample":
            print("Populating sample stock data...")
            if fetcher.populate_sample_data():
                print("Sample data populated successfully!")
            else:
                print("Failed to populate sample data.")
        
        elif action == "fetch" and len(sys.argv) == 5:
            symbols = [s.strip().upper() for s in sys.argv[2].split(',')]
            start_date_str = sys.argv[3]
            end_date_str = sys.argv[4]
            
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                
                print(f"Fetching data for {symbols} from {start_date_str} to {end_date_str}...")
                if fetcher.fetch_stock_data(symbols, start_date, end_date):
                    print("Data populated successfully!")
                else:
                    print("Failed to populate data.")
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD.")
        
        else:
            print("Usage:")
            print("  python3 stock_data_fetcher.py sample")
            print("  python3 stock_data_fetcher.py fetch <symbols> <start_date> <end_date>")
            print("  Example: python3 stock_data_fetcher.py fetch AAPL,MSFT 2024-01-01 2024-12-01")
        return
    
    # Interactive menu
    print("Stock Data Fetcher")
    print("1. Use sample data (AAPL, GOOGL, MSFT, TSLA, AMZN - last 30 days)")
    print("2. Enter custom symbols and date range")
    
    choice = input("Choose option (1 or 2): ").strip()
    
    if choice == '1':
        print("Populating sample stock data...")
        if fetcher.populate_sample_data():
            print("Sample data populated successfully!")
        else:
            print("Failed to populate sample data.")
    
    elif choice == '2':
        symbols_input = input("Enter stock symbols (comma-separated, e.g., AAPL,MSFT,GOOGL): ").strip()
        symbols = [s.strip().upper() for s in symbols_input.split(',') if s.strip()]
        
        start_date_str = input("Enter start date (YYYY-MM-DD): ").strip()
        end_date_str = input("Enter end date (YYYY-MM-DD): ").strip()
        
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            
            print(f"Fetching data for {symbols} from {start_date_str} to {end_date_str}...")
            if fetcher.fetch_stock_data(symbols, start_date, end_date):
                print("Data populated successfully!")
            else:
                print("Failed to populate data.")
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
    
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()