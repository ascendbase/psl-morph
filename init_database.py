#!/usr/bin/env python3
"""
Initialize database tables for Railway deployment
"""

import os
import sys
from sqlalchemy import create_engine, text
from models import db, User, Generation, Transaction
from werkzeug.security import generate_password_hash

def init_database():
    """Initialize database with tables and admin user"""
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not found!")
        return False
    
    # Fix postgres:// to postgresql:// for newer SQLAlchemy
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    print(f"Connecting to database...")
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"Connected to PostgreSQL: {version}")
        
        # Create all tables
        print("Creating database tables...")
        
        # Import app to get the db instance configured
        from app import app
        with app.app_context():
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Create admin user
            admin_email = "ascendbase@gmail.com"
            admin_password = "morphpas"
            
            # Check if admin user already exists
            existing_admin = User.query.filter_by(email=admin_email).first()
            if not existing_admin:
                admin_user = User(
                    email=admin_email,
                    password_hash=generate_password_hash(admin_password),
                    is_admin=True,
                    credits=1000  # Give admin 1000 credits
                )
                db.session.add(admin_user)
                db.session.commit()
                print(f"✅ Admin user created: {admin_email} / {admin_password}")
            else:
                print(f"✅ Admin user already exists: {admin_email}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    success = init_database()
    if success:
        print("\n🎉 Database initialization completed successfully!")
        print("Your app should now work properly.")
    else:
        print("\n💥 Database initialization failed!")
        sys.exit(1)
