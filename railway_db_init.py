#!/usr/bin/env python3
"""
Railway Database Initialization Script
Handles database setup for Railway deployment with PostgreSQL
"""

import os
import sys
from flask import Flask
from models import db, User, Generation, Transaction, ApiKey

def create_app():
    """Create Flask app for database initialization"""
    app = Flask(__name__)
    
    # Database configuration
    database_url = os.getenv('DATABASE_URL', 'sqlite:///face_morph.db')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'railway-init-key')
    
    return app

def init_railway_database():
    """Initialize database for Railway deployment"""
    app = create_app()
    db.init_app(app)
    
    with app.app_context():
        try:
            print("🚀 Initializing Railway database...")
            
            # Drop all tables first (clean slate)
            print("📋 Dropping existing tables...")
            db.drop_all()
            
            # Create all tables fresh
            print("🏗️ Creating database tables...")
            db.create_all()
            
            # Verify tables were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"✅ Created tables: {', '.join(tables)}")
            
            # Create admin user
            print("👤 Creating admin user...")
            admin = User(
                email='ascendbase@gmail.com',
                is_admin=True,
                credits=1000
            )
            admin.set_password('morphpas')
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created: ascendbase@gmail.com / morphpas")
            
            print("🎉 Railway database initialization completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    success = init_railway_database()
    sys.exit(0 if success else 1)