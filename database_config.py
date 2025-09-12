import mysql.connector
from mysql.connector import Error

class DatabaseConfig:
    def __init__(self):
        self.host = 'localhost'
        self.database = 'stock_portfolio'
        self.user = 'root'  # Change as needed
        self.password = 'Johnnyware@123'  # Change as needed
    
    def get_connection(self):
        try:
            connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            return connection
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None