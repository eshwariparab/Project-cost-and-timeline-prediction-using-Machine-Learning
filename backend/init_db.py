"""
Database initialization script
Run this once to initialize the database
"""
from app import app, db
from database import User, Prediction

def init_database():
    """Initialize the database and create tables"""
    with app.app_context():
        # Drop all tables (use with caution in production!)
        # db.drop_all()
        
        # Create all tables
        db.create_all()
        print("Database initialized successfully!")
        print(f"Tables created: {db.engine.table_names()}")

if __name__ == "__main__":
    init_database()
