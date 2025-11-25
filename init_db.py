import pymysql
from app import app, db

def create_database():
    # Connect to MySQL without specifying a database
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='thulasi',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    try:
        with connection.cursor() as cursor:
            # Create the database if it doesn't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS weddingbudget CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print("Database 'weddingbudget' created successfully or already exists.")
        
        # Close the connection
        connection.close()
        
        # Now create all tables
        with app.app_context():
            db.create_all()
            print("All tables created successfully.")
            
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if connection.open:
            connection.close()

if __name__ == "__main__":
    create_database()
