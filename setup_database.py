import mysql.connector

def setup_database():
    try:
        # Connect without specifying database first
        connection = mysql.connector.connect(
            host='localhost',
            user='admin',
            password='password'
        )
        
        cursor = connection.cursor()
        
        # Read and execute SQL file
        with open('database_setup.sql', 'r') as f:
            sql_content = f.read()
        
        # Split by semicolon and execute each command
        commands = sql_content.split(';')
        for command in commands:
            command = command.strip()
            if command:
                cursor.execute(command)
        
        connection.commit()
        print("Database setup completed successfully!")
        
    except Exception as e:
        print(f"Error setting up database: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    setup_database()