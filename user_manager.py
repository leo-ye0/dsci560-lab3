from database_config import DatabaseConfig
import secrets

class UserManager:
    def __init__(self):
        self.db_config = DatabaseConfig()
    
    def create_user(self, username):
        """Create a new user with unique ID"""
        connection = self.db_config.get_connection()
        if not connection:
            return False
        
        cursor = connection.cursor()
        try:
            user_id = secrets.token_hex(12)
            cursor.execute("INSERT INTO users (id, username) VALUES (%s, %s)", (user_id, username))
            connection.commit()
            print(f"User '{username}' created with ID: {user_id}")
            return user_id
        except Exception as e:
            if "Duplicate entry" in str(e):
                print(f"Username '{username}' already exists!")
            else:
                print(f"Error creating user: {e}")
            return False
        finally:
            cursor.close()
            connection.close()
    
    def get_user_by_username(self, username):
        """Get user ID by username"""
        connection = self.db_config.get_connection()
        if not connection:
            return None
        
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
    
    def list_users(self):
        """List all users"""
        connection = self.db_config.get_connection()
        if not connection:
            return
        
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT username, created_date FROM users ORDER BY created_date DESC")
            results = cursor.fetchall()
            if not results:
                print("No users found!")
                return
            
            print("\n=== ALL USERS ===")
            for username, created_date in results:
                print(f"Username: {username}, Created: {created_date}")
        except Exception as e:
            print(f"Error listing users: {e}")
        finally:
            cursor.close()
            connection.close()