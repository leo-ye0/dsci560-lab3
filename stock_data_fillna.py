import pandas as pd 
import mysql.connector
from mysql.connector import Error
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

def fill_data(method):
    '''Setup the database and tables'''
    try:
        # Connect to MySQL server (specifying the database)
        connection = mysql.connector.connect(
            host='localhost',
            user='admin',  # Change as needed
            password='password',   # Change as needed
            database='stock_portfolio' # Database name
        )
        
        if connection.is_connected():
            df = pd.read_sql('SELECT * FROM stock_data;', connection)
            size = df.shape[0]
            print()

            missing = []

            for stock_symbol, group in df.groupby('stock_symbol'):
                full_range = pd.date_range(start=group['date'].min(),
                                        end=group['date'].max(),
                                        freq='D')
                missing_dates = full_range.difference(group['date'])
                missing_dates = [date.date() for date in missing_dates]

                print(f'Missing dates for {stock_symbol}: {[d.strftime('%Y-%m-%d') for d in missing_dates]}')
                
                for date in missing_dates:
                    missing.append({
                        'stock_symbol': stock_symbol, 
                        'date': date,
                        'open_price': None,
                        'high_price': None,
                        'low_price': None,
                        'close_price': None,
                        'volume': None
                    })

            missing_df = pd.DataFrame(missing)

            df = pd.concat([df, missing_df], ignore_index=True)
            df = df.sort_values(['stock_symbol', 'date']).reset_index(drop=True)
            df.drop(columns=['id'], inplace=True)

            if method == 1: # Interpolation
                df = df.interpolate()
            elif method == 2: # Backward filling
                df = df.bfill()
            else: # Forward filling
                df = df.ffill()
        
        cursor = connection.cursor()

        print('\nUpdating data...')
        
        cursor.execute('DROP TABLE IF EXISTS stock_data')
        cursor.execute('''
        CREATE TABLE stock_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            stock_symbol VARCHAR(10) NOT NULL,
            date DATE NOT NULL,
            open_price DECIMAL(10,2),
            high_price DECIMAL(10,2),
            low_price DECIMAL(10,2),
            close_price DECIMAL(10,2),
            volume BIGINT,
            UNIQUE KEY unique_stock_date (stock_symbol, date)
        );
        ''')

        # cursor.execute('TRUNCATE TABLE stock_data')

        for _, row in df.iterrows():
                cursor.execute('''
                    INSERT INTO stock_data 
                    (stock_symbol, date, open_price, high_price, low_price, close_price, volume)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''', tuple(row))

        connection.commit()
        connection.commit()

        print('Database updated successfully!')
        print(f'\nNumber of rows before {choice_dict[choice]}: {size}')
        print(f'Number of rows after {choice_dict[choice]}: {df.shape[0]}')

    except Error as e:
        print(f'Error: {e}')
        return None
    finally:
        if connection.is_connected():
            connection.close()

if __name__ == "__main__":
    print('Filling missing data using:')
    print('1. Interpolation')
    print('2. Backward filling')
    print('3. Forward filling')
    
    choice = int(input('Choose option (1, 2, or 3): ').strip())

    choice_dict = {1:'interpolation', 2:'backward filling', 3:'forward filling'}
    
    if choice not in [1, 2, 3]:
        print('\nInvalid input!')
        quit()
    
    df = fill_data(choice)