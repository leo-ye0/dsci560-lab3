import pandas as pd 
import mysql.connector
from mysql.connector import Error
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

def fill_data(method, interpolation_method):
    """Setup the database and tables"""
    try:
        # Connect to MySQL server (specifying the database)
        connection = mysql.connector.connect(
            host='localhost',
            user='root',  # Change as needed
            password='Johnnyware@123',   # Change as needed
            database='stock_portfolio' # Database name
        )
        
        if connection.is_connected():
            df = pd.read_sql('SELECT * FROM stock_data;', connection)
            
            print('\nColumns with missing values:')
            print(df.isnull().sum())

            if method == 1: # Interpolation
                df = df.interpolate(method=i_dict[interpolation_method])
            elif method == 2: # Backward filling
                df = df.bfill()
            else: # Forward filling
                df = df.ffill()
        
        cursor = connection.cursor()

        print('\nUpdating data...')
        
        cursor.execute('TRUNCATE TABLE stock_data')

        for _, row in df.iterrows():
                cursor.execute('''
                    INSERT INTO stock_data 
                    (id, stock_symbol, date, open_price, high_price, low_price, close_price, volume)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ''', tuple(row))

        connection.commit()
        print('Database updated successfully!')

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
    
    choice1 = int(input('Choose option (1, 2, or 3): ').strip())
    
    if choice1 not in [1, 2, 3]:
        print('\nInvalid input!')
        quit()

    choice2 = 0

    # If user chooses 1
    if choice1 == 1:
        print('\nType of interpolation:')
        print('1. Linear')
        print('2. Time')
        print('3. Values')
        print('4. Barycentric')
        print('5. Akima')
        choice2 = int(input('Choose option (1, 2, 3, 4, or 5):').strip())

        if choice2 not in [1, 2, 3, 4, 5]:
            print('\nInvalid input!')
            quit()

        i_dict = {1:'linear', 2:'time', 3:'values', 4:'barycentric', 5:'akima'}

    df = fill_data(choice1, choice2)