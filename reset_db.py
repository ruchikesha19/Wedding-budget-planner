from app import app, db
import os

def reset_database():
    with app.app_context():
        # Drop all tables
        print("Dropping all tables...")
        db.drop_all()
        
        # Create all tables
        print("Creating all tables...")
        db.create_all()
        
        print("Database has been reset successfully!")

if __name__ == '__main__':
    # Confirm before proceeding
    confirm = input("This will delete ALL data in the database. Are you sure? (y/n): ")
    if confirm.lower() == 'y':
        reset_database()
    else:
        print("Database reset cancelled.")
