#!/usr/bin/env python3
"""
Fix production database schema for facial evaluation status column
This script will alter the existing table to support full status words
"""

import os
import sys
import psycopg2
from urllib.parse import urlparse

def get_database_connection():
    """Get database connection from environment"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL environment variable not found")
        return None
    
    try:
        # Parse the database URL
        parsed = urlparse(database_url)
        
        # Create connection
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            database=parsed.path[1:],  # Remove leading slash
            user=parsed.username,
            password=parsed.password,
            sslmode='require'
        )
        
        print(f"✅ Connected to database: {parsed.hostname}")
        return conn
        
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return None

def fix_facial_evaluation_schema(conn):
    """Fix the facial evaluation table schema"""
    try:
        cursor = conn.cursor()
        
        print("🔍 Checking current facial_evaluation table schema...")
        
        # Check if table exists and get current schema
        cursor.execute("""
            SELECT column_name, data_type, character_maximum_length 
            FROM information_schema.columns 
            WHERE table_name = 'facial_evaluation' 
            AND column_name = 'status'
        """)
        
        result = cursor.fetchone()
        if not result:
            print("❌ facial_evaluation table or status column not found")
            return False
        
        column_name, data_type, max_length = result
        print(f"📊 Current status column: {data_type}({max_length})")
        
        if data_type == 'character' and max_length == 1:
            print("🔧 Status column needs to be fixed (currently CHAR(1))")
            
            # Step 1: Add a temporary column
            print("1️⃣ Adding temporary status column...")
            cursor.execute("""
                ALTER TABLE facial_evaluation 
                ADD COLUMN status_temp VARCHAR(20) DEFAULT 'Pending'
            """)
            
            # Step 2: Update existing data
            print("2️⃣ Migrating existing status data...")
            cursor.execute("""
                UPDATE facial_evaluation 
                SET status_temp = CASE 
                    WHEN status = 'P' THEN 'Pending'
                    WHEN status = 'C' THEN 'Completed'
                    ELSE 'Pending'
                END
            """)
            
            # Step 3: Drop old column
            print("3️⃣ Dropping old status column...")
            cursor.execute("ALTER TABLE facial_evaluation DROP COLUMN status")
            
            # Step 4: Rename new column
            print("4️⃣ Renaming new column to status...")
            cursor.execute("ALTER TABLE facial_evaluation RENAME COLUMN status_temp TO status")
            
            # Step 5: Add constraint
            print("5️⃣ Adding status constraint...")
            cursor.execute("""
                ALTER TABLE facial_evaluation 
                ADD CONSTRAINT facial_evaluation_status_check 
                CHECK (status IN ('Pending', 'Completed'))
            """)
            
            conn.commit()
            print("✅ Status column successfully updated to VARCHAR(20)")
            
        elif data_type in ['character varying', 'varchar'] and max_length >= 20:
            print("✅ Status column is already properly configured")
            
        else:
            print(f"⚠️ Unexpected status column configuration: {data_type}({max_length})")
            
            # Still try to fix it
            print("🔧 Attempting to fix unexpected configuration...")
            cursor.execute("ALTER TABLE facial_evaluation ALTER COLUMN status TYPE VARCHAR(20)")
            conn.commit()
            print("✅ Status column updated to VARCHAR(20)")
        
        # Verify the fix
        print("🔍 Verifying schema fix...")
        cursor.execute("""
            SELECT column_name, data_type, character_maximum_length 
            FROM information_schema.columns 
            WHERE table_name = 'facial_evaluation' 
            AND column_name = 'status'
        """)
        
        result = cursor.fetchone()
        if result:
            column_name, data_type, max_length = result
            print(f"✅ Final status column: {data_type}({max_length})")
        
        cursor.close()
        return True
        
    except Exception as e:
        print(f"❌ Error fixing schema: {e}")
        conn.rollback()
        return False

def test_facial_evaluation_insert(conn):
    """Test that we can now insert facial evaluations with full status words"""
    try:
        cursor = conn.cursor()
        
        print("🧪 Testing facial evaluation insertion...")
        
        # Try to insert a test record (we'll roll it back)
        test_id = 'test-facial-eval-schema-fix'
        cursor.execute("""
            INSERT INTO facial_evaluation 
            (id, user_id, status, credits_used, created_at)
            VALUES (%s, (SELECT id FROM "user" WHERE is_admin = true LIMIT 1), 'Pending', 20, NOW())
        """, (test_id,))
        
        print("✅ Successfully inserted test record with 'Pending' status")
        
        # Update to 'Completed' status
        cursor.execute("""
            UPDATE facial_evaluation 
            SET status = 'Completed', completed_at = NOW()
            WHERE id = %s
        """, (test_id,))
        
        print("✅ Successfully updated test record to 'Completed' status")
        
        # Clean up test record
        cursor.execute("DELETE FROM facial_evaluation WHERE id = %s", (test_id,))
        
        conn.commit()
        cursor.close()
        
        print("✅ Schema fix test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Schema test failed: {e}")
        conn.rollback()
        return False

def main():
    """Main function to fix the production database schema"""
    print("🚀 FACIAL EVALUATION DATABASE SCHEMA FIX")
    print("=" * 50)
    
    # Get database connection
    conn = get_database_connection()
    if not conn:
        print("❌ Cannot proceed without database connection")
        return False
    
    try:
        # Fix the schema
        if not fix_facial_evaluation_schema(conn):
            print("❌ Failed to fix facial evaluation schema")
            return False
        
        # Test the fix
        if not test_facial_evaluation_insert(conn):
            print("❌ Schema fix test failed")
            return False
        
        print("\n🎉 DATABASE SCHEMA FIX COMPLETED SUCCESSFULLY!")
        print("✅ The facial evaluation feature should now work in production")
        print("✅ Status column can store 'Pending' and 'Completed' values")
        
        return True
        
    finally:
        conn.close()
        print("🔌 Database connection closed")

if __name__ == '__main__':
    success = main()
    if success:
        print("\n🚀 Ready to test facial evaluation feature in production!")
    else:
        print("\n❌ Schema fix failed - please check the errors above")
    
    sys.exit(0 if success else 1)
