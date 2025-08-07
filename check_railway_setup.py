#!/usr/bin/env python3
"""
Railway PostgreSQL Setup Helper
Run this after adding PostgreSQL service to your Railway project
"""

import os
import sys

def check_railway_environment():
    """Check if running on Railway with PostgreSQL"""
    print("🔍 Checking Railway environment...")
    
    railway_env = os.getenv('RAILWAY_ENVIRONMENT')
    database_url = os.getenv('DATABASE_URL')
    
    if railway_env:
        print(f"✅ Railway environment detected: {railway_env}")
    else:
        print("⚠️ Not running on Railway (RAILWAY_ENVIRONMENT not set)")
    
    if database_url:
        if database_url.startswith('postgres'):
            print("✅ PostgreSQL database URL detected")
            print(f"   Database URL: {database_url[:50]}...")
        else:
            print(f"⚠️ Non-PostgreSQL database URL: {database_url[:50]}...")
    else:
        print("❌ No DATABASE_URL environment variable found")
        print("   Make sure you've added a PostgreSQL service to your Railway project")
    
    return railway_env and database_url and database_url.startswith('postgres')

def test_database_connection():
    """Test database connection"""
    print("\n🔍 Testing database connection...")
    
    try:
        from sqlalchemy import create_engine, text
        from config import DATABASE_URL
        
        print(f"Using database URL: {DATABASE_URL[:50]}...")
        
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Railway PostgreSQL Setup Check")
    print("=" * 40)
    
    env_ok = check_railway_environment()
    
    if env_ok:
        db_ok = test_database_connection()
        
        if db_ok:
            print("\n🎉 Railway PostgreSQL setup is working correctly!")
            print("\n📝 Your database will now persist across deployments")
        else:
            print("\n❌ Database connection issues - check your Railway PostgreSQL service")
    else:
        print("\n📋 Next steps:")
        print("1. Go to your Railway dashboard")
        print("2. Click 'New Service' → 'Database' → 'Add PostgreSQL'")
        print("3. Deploy your app again")
        print("4. Run this script again to verify")
