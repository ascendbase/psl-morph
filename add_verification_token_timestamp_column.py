#!/usr/bin/env python3
"""
Add verification_token_created_at column to Railway PostgreSQL database

This script adds the missing verification_token_created_at column to the production database
and updates existing users with verification tokens to have a current timestamp.
"""

import os
import sys
from datetime import datetime
import psycopg2
from urllib.parse import urlparse

def add_verification_token_timestamp_column():
    """Add verification_token_created_at column to users table"""
    try:
        # Get database URL from environment
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL environment variable not found")
            print("💡 Please set DATABASE_URL to your Railway PostgreSQL connection string")
            return False
        
        # Parse the database URL
        parsed = urlparse(database_url)
        
        # Connect to PostgreSQL database
        print("🔗 Connecting to Railway PostgreSQL database...")
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            database=parsed.path[1:],  # Remove leading slash
            user=parsed.username,
            password=parsed.password
        )
        
        cursor = conn.cursor()
        
        # Check if column already exists
        print("🔍 Checking if verification_token_created_at column exists...")
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'user' 
            AND column_name = 'verification_token_created_at'
        """)
        
        if cursor.fetchone():
            print("✅ verification_token_created_at column already exists")
            cursor.close()
            conn.close()
            return True
        
        # Add the new column
        print("📝 Adding verification_token_created_at column...")
        cursor.execute("""
            ALTER TABLE "user" 
            ADD COLUMN verification_token_created_at TIMESTAMP
        """)
        
        # Update existing users who have verification tokens
        print("🔄 Updating existing users with verification tokens...")
        current_time = datetime.utcnow()
        
        cursor.execute("""
            UPDATE "user" 
            SET verification_token_created_at = %s 
            WHERE verification_token IS NOT NULL 
            AND verification_token != ''
        """, (current_time,))
        
        updated_rows = cursor.rowcount
        print(f"📊 Updated {updated_rows} existing users with verification tokens")
        
        # Commit the changes
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Successfully added verification_token_created_at column and updated existing users")
        return True
        
    except Exception as e:
        print(f"❌ Error adding verification_token_created_at column: {e}")
        return False

def main():
    """Main function to add verification token timestamp column"""
    print("🔧 Adding verification_token_created_at Column to Railway Database")
    print("=" * 70)
    
    if add_verification_token_timestamp_column():
        print("\n" + "=" * 70)
        print("✅ Database migration completed successfully!")
        print("\nChanges made:")
        print("1. ✅ Added verification_token_created_at column to user table")
        print("2. ✅ Updated existing users with verification tokens")
        print("\nThe email verification system now properly tracks token generation time")
        print("and will correctly handle token expiration for both new and resent tokens.")
        print("\nNext steps:")
        print("1. Deploy the updated models.py and auth.py to Railway")
        print("2. Test the email verification flow")
        return True
    else:
        print("\n" + "=" * 70)
        print("❌ Database migration failed!")
        print("Please check the error messages above and try again.")
        return False

if __name__ == "__main__":
    main()
