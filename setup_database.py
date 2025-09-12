import mysql.connector
from mysql.connector import Error

def setup_database():
    """Setup the database and tables"""
    try:
        # Connect to MySQL server (without specifying database)
        connection = mysql.connector.connect(
            host='localhost',
            user='root',  # Change as needed
            password='Johnnyware@123'   # Change as needed
        )
        
        cursor = connection.cursor()
        
        # Read and execute SQL setup file
        with open('database_setup.sql', 'r') as file:
            sql_commands = file.read().split(';')
            
        for command in sql_commands:
            command = command.strip()
            if command:
                cursor.execute(command)
        
        connection.commit()
        print("Database and tables created successfully!")
        
    except Error as e:
        print(f"Error setting up database: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    setup_database()