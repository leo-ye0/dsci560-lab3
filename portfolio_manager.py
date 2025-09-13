from database_config import DatabaseConfig
from stock_data_fetcher import StockDataFetcher
from user_manager import UserManager
from datetime import datetime
import sys
import secrets

class PortfolioManager:
    def __init__(self):
        self.db_config = DatabaseConfig()
        self.stock_fetcher = StockDataFetcher()
        self.user_manager = UserManager()
    
    def create_portfolio(self, username, name):
        """Create a new portfolio for a user"""
        user_id = self.user_manager.get_user_by_username(username)
        if not user_id:
            print(f"User '{username}' not found!")
            return False
        
        connection = self.db_config.get_connection()
        if not connection:
            return False
        
        cursor = connection.cursor()
        try:
            portfolio_id = secrets.token_hex(12)
            cursor.execute("INSERT INTO portfolios (id, user_id, name) VALUES (%s, %s, %s)", 
                         (portfolio_id, user_id, name))
            connection.commit()
            print(f"Portfolio '{name}' created for user '{username}' with ID: {portfolio_id}")
            return portfolio_id
        except Exception as e:
            if "Duplicate entry" in str(e):
                print(f"Portfolio '{name}' already exists for user '{username}'!")
            else:
                print(f"Error creating portfolio: {e}")
            return False
        finally:
            cursor.close()
            connection.close()
    
    def remove_portfolio(self, username, portfolio_name):
        """Remove a portfolio for a user"""
        user_id = self.user_manager.get_user_by_username(username)
        if not user_id:
            print(f"User '{username}' not found!")
            return False
        
        connection = self.db_config.get_connection()
        if not connection:
            return False
        
        cursor = connection.cursor()
        try:
            cursor.execute("DELETE FROM portfolios WHERE user_id = %s AND name = %s", 
                         (user_id, portfolio_name))
            
            if cursor.rowcount > 0:
                connection.commit()
                print(f"Portfolio '{portfolio_name}' removed for user '{username}'!")
                return True
            else:
                print(f"Portfolio '{portfolio_name}' not found for user '{username}'!")
                return False
                
        except Exception as e:
            print(f"Error removing portfolio: {e}")
            return False
        finally:
            cursor.close()
            connection.close()
    
    def add_stock_to_portfolio(self, username, portfolio_name, stock_symbol):
        """Add stock to portfolio with validation"""
        # Check for comma-separated symbols
        if ',' in stock_symbol:
            print(f"Error: Only one stock symbol allowed. Use separate commands for multiple stocks.")
            print(f"Example: python3 portfolio_manager.py add {username} \"{portfolio_name}\" TSLA")
            return False
            
        if not self.stock_fetcher.validate_stock(stock_symbol):
            print(f"Invalid stock symbol: {stock_symbol}")
            return False
        
        user_id = self.user_manager.get_user_by_username(username)
        if not user_id:
            print(f"User '{username}' not found!")
            return False
        
        connection = self.db_config.get_connection()
        if not connection:
            return False
        
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT id FROM portfolios WHERE user_id = %s AND name = %s", 
                         (user_id, portfolio_name))
            result = cursor.fetchone()
            if not result:
                print(f"Portfolio '{portfolio_name}' not found for user '{username}'!")
                return False
            
            portfolio_id = result[0]
            cursor.execute(
                "INSERT INTO portfolio_stocks (portfolio_id, stock_symbol) VALUES (%s, %s)",
                (portfolio_id, stock_symbol.upper())
            )
            connection.commit()
            print(f"Stock {stock_symbol.upper()} added to '{portfolio_name}' for user '{username}'!")
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
    
    def remove_stock_from_portfolio(self, username, portfolio_name, stock_symbol):
        """Remove stock from portfolio"""
        user_id = self.user_manager.get_user_by_username(username)
        if not user_id:
            print(f"User '{username}' not found!")
            return False
        
        connection = self.db_config.get_connection()
        if not connection:
            return False
        
        cursor = connection.cursor()
        try:
            cursor.execute("""
                DELETE ps FROM portfolio_stocks ps
                JOIN portfolios p ON ps.portfolio_id = p.id
                WHERE p.user_id = %s AND p.name = %s AND ps.stock_symbol = %s
            """, (user_id, portfolio_name, stock_symbol.upper()))
            
            if cursor.rowcount > 0:
                connection.commit()
                print(f"Stock {stock_symbol.upper()} removed from '{portfolio_name}' for user '{username}'!")
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
    
    def display_user_portfolios(self, username):
        """Display all portfolios for a specific user"""
        user_id = self.user_manager.get_user_by_username(username)
        if not user_id:
            print(f"User '{username}' not found!")
            return
        
        connection = self.db_config.get_connection()
        if not connection:
            return
        
        cursor = connection.cursor()
        try:
            cursor.execute("""
                SELECT p.name, p.created_date, GROUP_CONCAT(ps.stock_symbol) as stocks
                FROM portfolios p
                LEFT JOIN portfolio_stocks ps ON p.id = ps.portfolio_id
                WHERE p.user_id = %s
                GROUP BY p.id, p.name, p.created_date
                ORDER BY p.created_date DESC
            """, (user_id,))
            
            results = cursor.fetchall()
            if not results:
                print(f"No portfolios found for user '{username}'!")
                return
            
            print(f"\n=== PORTFOLIOS FOR {username.upper()} ===")
            for name, created_date, stocks in results:
                print(f"\nPortfolio: {name}")
                print(f"Created: {created_date}")
                print(f"Stocks: {stocks if stocks else 'No stocks added'}")
                
        except Exception as e:
            print(f"Error displaying portfolios: {e}")
        finally:
            cursor.close()
            connection.close()
    
    def fetch_portfolio_data(self, username, portfolio_name, start_date, end_date):
        """Fetch stock data for all stocks in a portfolio"""
        user_id = self.user_manager.get_user_by_username(username)
        if not user_id:
            print(f"User '{username}' not found!")
            return
        
        connection = self.db_config.get_connection()
        if not connection:
            return
        
        cursor = connection.cursor()
        try:
            cursor.execute("""
                SELECT ps.stock_symbol
                FROM portfolio_stocks ps
                JOIN portfolios p ON ps.portfolio_id = p.id
                WHERE p.user_id = %s AND p.name = %s
            """, (user_id, portfolio_name))
            
            stocks = [row[0] for row in cursor.fetchall()]
            if not stocks:
                print(f"No stocks found in portfolio '{portfolio_name}' for user '{username}'!")
                return
            
            print(f"Fetching data for '{username}' portfolio '{portfolio_name}' stocks: {', '.join(stocks)}")
            
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
        
        if action == "create-user" and len(sys.argv) == 3:
            manager.user_manager.create_user(sys.argv[2])
        elif action == "list-users" and len(sys.argv) == 2:
            manager.user_manager.list_users()
        elif action == "create-portfolio" and len(sys.argv) == 4:
            manager.create_portfolio(sys.argv[2], sys.argv[3])
        elif action == "remove-portfolio" and len(sys.argv) == 4:
            manager.remove_portfolio(sys.argv[2], sys.argv[3])
        elif action == "add" and len(sys.argv) == 5:
            manager.add_stock_to_portfolio(sys.argv[2], sys.argv[3], sys.argv[4])
        elif action == "remove" and len(sys.argv) == 5:
            manager.remove_stock_from_portfolio(sys.argv[2], sys.argv[3], sys.argv[4])
        elif action == "display" and len(sys.argv) == 3:
            manager.display_user_portfolios(sys.argv[2])
        elif action == "fetch" and len(sys.argv) == 6:
            manager.fetch_portfolio_data(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
        else:
            print("Usage:")
            print("  python3 portfolio_manager.py create-user <username>")
            print("  python3 portfolio_manager.py list-users")
            print("  python3 portfolio_manager.py create-portfolio <username> <portfolio_name>")
            print("  python3 portfolio_manager.py remove-portfolio <username> <portfolio_name>")
            print("  python3 portfolio_manager.py add <username> <portfolio_name> <stock>")
            print("  python3 portfolio_manager.py remove <username> <portfolio_name> <stock>")
            print("  python3 portfolio_manager.py display <username>")
            print("  python3 portfolio_manager.py fetch <username> <portfolio_name> <start_date> <end_date>")
        return
    
    # Interactive menu
    while True:
        print("\n=== PORTFOLIO MANAGER ===")
        print("1. Create User")
        print("2. List Users")
        print("3. Create Portfolio")
        print("4. Remove Portfolio")
        print("5. Add Stock to Portfolio")
        print("6. Remove Stock from Portfolio")
        print("7. Display User Portfolios")
        print("8. Fetch Portfolio Data")
        print("9. Exit")
        
        choice = input("\nEnter your choice (1-9): ").strip()
        
        if choice == '1':
            username = input("Enter username: ").strip()
            if username:
                manager.user_manager.create_user(username)
        
        elif choice == '2':
            manager.user_manager.list_users()
        
        elif choice == '3':
            username = input("Enter username: ").strip()
            name = input("Enter portfolio name: ").strip()
            if username and name:
                manager.create_portfolio(username, name)
        
        elif choice == '4':
            username = input("Enter username: ").strip()
            portfolio = input("Enter portfolio name: ").strip()
            if username and portfolio:
                manager.remove_portfolio(username, portfolio)
        
        elif choice == '5':
            username = input("Enter username: ").strip()
            portfolio = input("Enter portfolio name: ").strip()
            stock = input("Enter stock symbol: ").strip()
            if username and portfolio and stock:
                manager.add_stock_to_portfolio(username, portfolio, stock)
        
        elif choice == '6':
            username = input("Enter username: ").strip()
            portfolio = input("Enter portfolio name: ").strip()
            stock = input("Enter stock symbol: ").strip()
            if username and portfolio and stock:
                manager.remove_stock_from_portfolio(username, portfolio, stock)
        
        elif choice == '7':
            username = input("Enter username: ").strip()
            if username:
                manager.display_user_portfolios(username)
        
        elif choice == '8':
            username = input("Enter username: ").strip()
            portfolio = input("Enter portfolio name: ").strip()
            start = input("Enter start date (YYYY-MM-DD): ").strip()
            end = input("Enter end date (YYYY-MM-DD): ").strip()
            if username and portfolio and start and end:
                manager.fetch_portfolio_data(username, portfolio, start, end)
        
        elif choice == '9':
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main()