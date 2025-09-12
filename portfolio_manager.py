from database_config import DatabaseConfig
from stock_data_fetcher import StockDataFetcher
from datetime import datetime
import sys
import secrets

class PortfolioManager:
    def __init__(self):
        self.db_config = DatabaseConfig()
        self.stock_fetcher = StockDataFetcher()
    
    def create_portfolio(self, name):
        """Create a new portfolio with ObjectId-style ID"""
        connection = self.db_config.get_connection()
        if not connection:
            return False
        
        cursor = connection.cursor()
        try:
            portfolio_id = secrets.token_hex(12)  # Generate 24-char hex ID
            cursor.execute("INSERT INTO portfolios (id, name) VALUES (%s, %s)", (portfolio_id, name))
            connection.commit()
            print(f"Portfolio '{name}' created with ID: {portfolio_id}")
            return portfolio_id
        except Exception as e:
            print(f"Error creating portfolio: {e}")
            return False
        finally:
            cursor.close()
            connection.close()
    
    def add_stock_to_portfolio(self, portfolio_name, stock_symbol):
        """Add stock to portfolio with validation"""
        # Validate stock first
        if not self.stock_fetcher.validate_stock(stock_symbol):
            print(f"Invalid stock symbol: {stock_symbol}")
            return False
        
        connection = self.db_config.get_connection()
        if not connection:
            return False
        
        cursor = connection.cursor()
        try:
            # Get portfolio ID
            cursor.execute("SELECT id FROM portfolios WHERE name = %s", (portfolio_name,))
            result = cursor.fetchone()
            if not result:
                print(f"Portfolio '{portfolio_name}' not found!")
                return False
            
            portfolio_id = result[0]
            
            # Add stock to portfolio
            cursor.execute(
                "INSERT INTO portfolio_stocks (portfolio_id, stock_symbol) VALUES (%s, %s)",
                (portfolio_id, stock_symbol.upper())
            )
            connection.commit()
            print(f"Stock {stock_symbol.upper()} added successfully to portfolio '{portfolio_name}'!")
            return True
            
        except Exception as e:
            if "Duplicate entry" in str(e):
                print(f"Stock {stock_symbol.upper()} already exists in portfolio '{portfolio_name}'!")
            else:
                print(f"Error adding stock: {e}")
            return False
        finally:
            cursor.close()
            connection.close()
    
    def remove_stock_from_portfolio(self, portfolio_name, stock_symbol):
        """Remove stock from portfolio"""
        connection = self.db_config.get_connection()
        if not connection:
            return False
        
        cursor = connection.cursor()
        try:
            cursor.execute("""
                DELETE ps FROM portfolio_stocks ps
                JOIN portfolios p ON ps.portfolio_id = p.id
                WHERE p.name = %s AND ps.stock_symbol = %s
            """, (portfolio_name, stock_symbol.upper()))
            
            if cursor.rowcount > 0:
                connection.commit()
                print(f"Stock {stock_symbol.upper()} removed successfully from portfolio '{portfolio_name}'!")
                return True
            else:
                print(f"Stock {stock_symbol.upper()} not found in portfolio '{portfolio_name}'!")
                return False
                
        except Exception as e:
            print(f"Error removing stock: {e}")
            return False
        finally:
            cursor.close()
            connection.close()
    
    def display_portfolios(self):
        """Display all portfolios with their stocks"""
        connection = self.db_config.get_connection()
        if not connection:
            return
        
        cursor = connection.cursor()
        try:
            cursor.execute("""
                SELECT p.name, p.created_date, GROUP_CONCAT(ps.stock_symbol) as stocks
                FROM portfolios p
                LEFT JOIN portfolio_stocks ps ON p.id = ps.portfolio_id
                GROUP BY p.id, p.name, p.created_date
                ORDER BY p.created_date DESC
            """)
            
            results = cursor.fetchall()
            if not results:
                print("No portfolios found!")
                return
            
            print("\n=== YOUR PORTFOLIOS ===")
            for name, created_date, stocks in results:
                print(f"\nPortfolio: {name}")
                print(f"Created: {created_date}")
                print(f"Stocks: {stocks if stocks else 'No stocks added'}")
                
        except Exception as e:
            print(f"Error displaying portfolios: {e}")
        finally:
            cursor.close()
            connection.close()
    
    def fetch_portfolio_data(self, portfolio_name, start_date, end_date):
        """Fetch stock data for all stocks in a portfolio"""
        connection = self.db_config.get_connection()
        if not connection:
            return
        
        cursor = connection.cursor()
        try:
            # Get stocks in portfolio
            cursor.execute("""
                SELECT ps.stock_symbol
                FROM portfolio_stocks ps
                JOIN portfolios p ON ps.portfolio_id = p.id
                WHERE p.name = %s
            """, (portfolio_name,))
            
            stocks = [row[0] for row in cursor.fetchall()]
            if not stocks:
                print(f"No stocks found in portfolio '{portfolio_name}'!")
                return
            
            print(f"Fetching data for portfolio '{portfolio_name}' stocks: {', '.join(stocks)}")
            
            # Fetch stock data
            if self.stock_fetcher.fetch_stock_data(stocks, start_date, end_date):
                print("Portfolio data fetched successfully!")
            else:
                print("Failed to fetch portfolio data!")
                
        except Exception as e:
            print(f"Error fetching portfolio data: {e}")
        finally:
            cursor.close()
            connection.close()

def main():
    manager = PortfolioManager()
    
    # Command line interface
    if len(sys.argv) > 1:
        action = sys.argv[1]
        
        if action == "create" and len(sys.argv) == 3:
            manager.create_portfolio(sys.argv[2])
        elif action == "add" and len(sys.argv) == 4:
            manager.add_stock_to_portfolio(sys.argv[2], sys.argv[3])
        elif action == "remove" and len(sys.argv) == 4:
            manager.remove_stock_from_portfolio(sys.argv[2], sys.argv[3])
        elif action == "display":
            manager.display_portfolios()
        elif action == "fetch" and len(sys.argv) == 5:
            manager.fetch_portfolio_data(sys.argv[2], sys.argv[3], sys.argv[4])
        else:
            print("Usage:")
            print("  python portfolio_manager.py create <name>")
            print("  python portfolio_manager.py add <portfolio_name> <stock>")
            print("  python portfolio_manager.py remove <portfolio_name> <stock>")
            print("  python portfolio_manager.py display")
            print("  python portfolio_manager.py fetch <portfolio_name> <start_date> <end_date>")
        return
    
    # Interactive menu
    while True:
        print("\n=== PORTFOLIO MANAGER ===")
        print("1. Create Portfolio")
        print("2. Add Stock to Portfolio")
        print("3. Remove Stock from Portfolio")
        print("4. Display All Portfolios")
        print("5. Fetch Portfolio Data")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            name = input("Enter portfolio name: ").strip()
            if name:
                manager.create_portfolio(name)
        
        elif choice == '2':
            portfolio = input("Enter portfolio name: ").strip()
            stock = input("Enter stock symbol: ").strip()
            if portfolio and stock:
                manager.add_stock_to_portfolio(portfolio, stock)
        
        elif choice == '3':
            portfolio = input("Enter portfolio name: ").strip()
            stock = input("Enter stock symbol: ").strip()
            if portfolio and stock:
                manager.remove_stock_from_portfolio(portfolio, stock)
        
        elif choice == '4':
            manager.display_portfolios()
        
        elif choice == '5':
            portfolio = input("Enter portfolio name: ").strip()
            start = input("Enter start date (YYYY-MM-DD): ").strip()
            end = input("Enter end date (YYYY-MM-DD): ").strip()
            if portfolio and start and end:
                manager.fetch_portfolio_data(portfolio, start, end)
        
        elif choice == '6':
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main()