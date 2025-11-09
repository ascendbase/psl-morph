#!/usr/bin/env python3
"""
EMERGENCY DATABASE FIX - Admin Dashboard Critical Issue
This script will diagnose and fix the database schema issue immediately
"""

import os
import sys
import psycopg2
from urllib.parse import urlparse
import traceback

def get_database_connection():
    """Get database connection from environment"""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL environment variable not found")
        print("Trying to load from .env file...")
        
        # Try to load from .env file
        try:
            with open('.env', 'r') as f:
                for line in f:
                    if line.startswith('DATABASE_URL='):
                        database_url = line.split('=', 1)[1].strip()
                        break
        except:
            pass
    
    if not database_url:
        print("❌ Could not find DATABASE_URL")
        return None
    
    try:
        parsed = urlparse(database_url)
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            database=parsed.path[1:],  # Remove leading slash
            user=parsed.username,
            password=parsed.password
        )
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def check_table_structure(cursor, table_name):
    """Check if table exists and get its structure"""
    try:
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = %s 
            ORDER BY ordinal_position;
        """, (table_name,))
        
        columns = cursor.fetchall()
        if not columns:
            print(f"❌ Table '{table_name}' does not exist!")
            return None
        
        print(f"✅ Table '{table_name}' exists with {len(columns)} columns:")
        for col in columns:
            print(f"  - {col[0]} ({col[1]}) {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
        
        return {col[0]: col[1] for col in columns}
    except Exception as e:
        print(f"❌ Error checking table {table_name}: {e}")
        return None

def fix_facial_evaluation_table(cursor):
    """Fix the facial_evaluation table schema"""
    print("\n🔧 Fixing facial_evaluation table...")
    
    required_columns = {
        'second_image_filename': 'VARCHAR(255)',
        'morphed_image_filename': 'VARCHAR(255)', 
        'generation_id': 'VARCHAR(36)',
        'admin_response': 'TEXT',
        'admin_id': 'VARCHAR(36)',
        'credits_used': 'INTEGER'
    }
    
    # Get current columns
    current_columns = check_table_structure(cursor, 'facial_evaluation')
    if current_columns is None:
        print("❌ facial_evaluation table does not exist!")
        return False
    
    # Add missing columns
    for col_name, col_type in required_columns.items():
        if col_name not in current_columns:
            try:
                if col_name == 'credits_used':
                    sql = f"ALTER TABLE facial_evaluation ADD COLUMN {col_name} {col_type} DEFAULT 20;"
                else:
                    sql = f"ALTER TABLE facial_evaluation ADD COLUMN {col_name} {col_type};"
                
                cursor.execute(sql)
                print(f"✅ Added column: {col_name}")
            except Exception as e:
                print(f"⚠️  Warning adding {col_name}: {e}")
        else:
            print(f"✅ Column {col_name} already exists")
    
    return True

def add_foreign_keys(cursor):
    """Add foreign key constraints"""
    print("\n🔧 Adding foreign key constraints...")
    
    constraints = [
        {
            'name': 'fk_facial_evaluation_generation',
            'sql': 'ALTER TABLE facial_evaluation ADD CONSTRAINT fk_facial_evaluation_generation FOREIGN KEY (generation_id) REFERENCES generation(id);'
        },
        {
            'name': 'fk_facial_evaluation_admin', 
            'sql': 'ALTER TABLE facial_evaluation ADD CONSTRAINT fk_facial_evaluation_admin FOREIGN KEY (admin_id) REFERENCES "user"(id);'
        }
    ]
    
    for constraint in constraints:
        try:
            cursor.execute(constraint['sql'])
            print(f"✅ Added constraint: {constraint['name']}")
        except Exception as e:
            if 'already exists' in str(e).lower():
                print(f"✅ Constraint {constraint['name']} already exists")
            else:
                print(f"⚠️  Warning adding {constraint['name']}: {e}")

def test_facial_evaluation_query(cursor):
    """Test the exact query that's failing"""
    print("\n🧪 Testing facial evaluation query...")
    
    try:
        # This is the exact query from the error
        cursor.execute("""
            SELECT facial_evaluation.id AS facial_evaluation_id, 
                   facial_evaluation.user_id AS facial_evaluation_user_id, 
                   facial_evaluation.original_image_filename AS facial_evaluation_original_image_filename, 
                   facial_evaluation.second_image_filename AS facial_evaluation_second_image_filename, 
                   facial_evaluation.morphed_image_filename AS facial_evaluation_morphed_image_filename, 
                   facial_evaluation.generation_id AS facial_evaluation_generation_id, 
                   facial_evaluation.status AS facial_evaluation_status, 
                   facial_evaluation.created_at AS facial_evaluation_created_at, 
                   facial_evaluation.completed_at AS facial_evaluation_completed_at, 
                   facial_evaluation.admin_response AS facial_evaluation_admin_response, 
                   facial_evaluation.admin_id AS facial_evaluation_admin_id, 
                   facial_evaluation.credits_used AS facial_evaluation_credits_used 
            FROM facial_evaluation 
            LIMIT 1;
        """)
        
        result = cursor.fetchone()
        print("✅ Facial evaluation query test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Facial evaluation query test FAILED: {e}")
        return False

def main():
    """Main emergency fix function"""
    print("🚨 EMERGENCY DATABASE FIX - Admin Dashboard Critical Issue")
    print("=" * 60)
    
    # Get database connection
    conn = get_database_connection()
    if not conn:
        print("❌ Could not connect to database!")
        sys.exit(1)
    
    cursor = conn.cursor()
    
    try:
        print("\n📋 Checking current database structure...")
        
        # Check all tables exist
        tables_to_check = ['user', 'generation', 'facial_evaluation', 'transaction']
        for table in tables_to_check:
            check_table_structure(cursor, table)
        
        # Fix facial_evaluation table
        if not fix_facial_evaluation_table(cursor):
            print("❌ Failed to fix facial_evaluation table!")
            sys.exit(1)
        
        # Add foreign keys
        add_foreign_keys(cursor)
        
        # Commit all changes
        conn.commit()
        print("\n✅ All database changes committed!")
        
        # Test the query that was failing
        if test_facial_evaluation_query(cursor):
            print("\n🎉 SUCCESS! Admin dashboard should now work!")
            print("🚀 You can now access /admin to get your GPU URL!")
        else:
            print("\n❌ Query test still failing - there may be other issues")
            
    except Exception as e:
        print(f"\n❌ Emergency fix failed: {e}")
        traceback.print_exc()
        conn.rollback()
        sys.exit(1)
    
    finally:
        cursor.close()
        conn.close()
    
    print("\n" + "=" * 60)
    print("🎯 NEXT STEPS:")
    print("1. Try accessing /admin in your browser")
    print("2. Login with: ascendbase@gmail.com / morphpas")
    print("3. Get your GPU URL from the admin dashboard")
    print("4. The facial evaluation feature should also work now")

if __name__ == "__main__":
    main()
