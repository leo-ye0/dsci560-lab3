import pandas as pd
import mysql.connector
from mysql.connector import Error
import warnings

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

def format_metrics():
    """Calculate metrics and store them into stock_metrics table"""
    try:
        # connect sql
        connection = mysql.connector.connect(
            host='localhost',
            user='admin',
            password='password',
            database='stock_portfolio'
        )

        if connection.is_connected():
            print("Connected to MySQL.")

            # read stock_data
            df = pd.read_sql("SELECT stock_symbol, date, close_price FROM stock_data;", connection)
            size = df.shape[0]

            # date
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values(['stock_symbol', 'date']).reset_index(drop=True)

            metrics = []

            # metrics
            for stock_symbol, group in df.groupby('stock_symbol'):
                group = group.sort_values('date').copy()

                group['daily_return'] = group['close_price'].pct_change()
                group['cumulative_return'] = (1 + group['daily_return']).cumprod() - 1
                group['volatility'] = group['daily_return'].rolling(window=30).std()

                metrics.append(group)

            df_metrics = pd.concat(metrics, ignore_index=True)

        cursor = connection.cursor()

        print('\nUpdating metrics table...')

        # sql
        cursor.execute('DROP TABLE IF EXISTS stock_metrics')
        cursor.execute('''
        CREATE TABLE stock_metrics (
            id INT AUTO_INCREMENT PRIMARY KEY,
            stock_symbol VARCHAR(10) NOT NULL,
            date DATE NOT NULL,
            close_price DECIMAL(10,2),
            daily_return DECIMAL(10,6),
            cumulative_return DECIMAL(10,6),
            volatility DECIMAL(10,6),
            UNIQUE KEY unique_stock_date (stock_symbol, date)
        );
        ''')

        # write data
        for _, row in df_metrics.iterrows():
            cursor.execute('''
                INSERT INTO stock_metrics 
                (stock_symbol, date, close_price, daily_return, cumulative_return, volatility)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (
                row['stock_symbol'],
                row['date'].date(),
                None if pd.isna(row['close_price']) else float(row['close_price']),
                None if pd.isna(row['daily_return']) else float(row['daily_return']),
                None if pd.isna(row['cumulative_return']) else float(row['cumulative_return']),
                None if pd.isna(row['volatility']) else float(row['volatility'])
            ))

        connection.commit()

        print('Metrics table updated successfully!')
        print(f'\nNumber of rows processed: {size}')
        print(f'Number of rows inserted: {df_metrics.shape[0]}')
        print("Preview of metrics (first 5 rows):")
        print(df_metrics.head(5))
    except Error as e:
        print(f'Error: {e}')
        return None
    finally:
        if connection.is_connected():
            connection.close()


def query_metrics():
    """Ask user for stock, time slot, and metric; compute values instead of listing raw rows"""
    connection = None
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='admin',
            password='password',
            database='stock_portfolio'
        )

        # input
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)

            print("\nMetrics Query")
            symbol = input("Enter stock symbol (e.g., AAPL): ").strip().upper()
            start = input("Enter start date (YYYY-MM-DD): ").strip()
            end = input("Enter end date (YYYY-MM-DD): ").strip()

            # menu with numbers
            print("\nAvailable metrics:")
            print("1. close_price")
            print("2. daily_return")
            print("3. cumulative_return")
            print("4. volatility")

            choice = input("Which metric do you want to calculate? (input a number) ").strip()

            metric_map = {
                "1": "close_price",
                "2": "daily_return",
                "3": "cumulative_return",
                "4": "volatility"
            }

            if choice not in metric_map:
                print("Invalid metric choice.")
                return

            metric = metric_map[choice]

            cursor.execute(f"""
                SELECT date, close_price, daily_return, cumulative_return, volatility
                FROM stock_metrics
                WHERE stock_symbol = %s AND date BETWEEN %s AND %s
                ORDER BY date ASC
            """, (symbol, start, end))
            rows = cursor.fetchall()

            if not rows:
                print("No data found for this query.")
                return

            df = pd.DataFrame(rows)

            # select
            result = None
            if metric == "close_price":
                result = df['close_price'].iloc[-1] - df['close_price'].iloc[0]
                print(f"\n{symbol} price change from {start} to {end}: {result:.2f}")

            elif metric == "daily_return":
                result = df['daily_return'].mean()
                print(f"\n{symbol} average daily return from {start} to {end}: {result:.6f}")

            elif metric == "cumulative_return":
                result = df['cumulative_return'].iloc[-1] - df['cumulative_return'].iloc[0]
                print(f"\n{symbol} cumulative return change from {start} to {end}: {result:.6f}")

            elif metric == "volatility":
                daily_returns = df['daily_return'].astype(float)
                result = daily_returns.std()
                print(f"\n{symbol} volatility (std of daily returns) from {start} to {end}: {result:.6f}")

    except Error as e:
        print(f"Query error: {e}")

    finally:
        if connection and connection.is_connected():
            connection.close()

if __name__ == "__main__":
    format_metrics()
    query_metrics()
