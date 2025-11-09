#!/usr/bin/env python3
"""
Execute database schema fix directly on deployed database
This script connects to the database and runs the SQL fix
"""

import os
import sys
import psycopg2
from urllib.parse import urlparse

def execute_database_fix():
    """Execute the database schema fix"""
    
    try:
        # Get database URL from environment
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL environment variable not found")
            print("Make sure you're running this on the deployed environment")
            return False
        
        print("🔧 Connecting to database...")
        
        # Parse database URL
        parsed = urlparse(database_url)
        
        # Connect to database
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            database=parsed.path[1:],  # Remove leading slash
            user=parsed.username,
            password=parsed.password
        )
        
        cursor = conn.cursor()
        
        print("✅ Connected to database")
        print("🔧 Executing schema fixes...")
        
        # Execute the schema fixes
        sql_commands = [
            "ALTER TABLE facial_evaluation ADD COLUMN IF NOT EXISTS second_image_filename VARCHAR(255);",
            "ALTER TABLE facial_evaluation ADD COLUMN IF NOT EXISTS morphed_image_filename VARCHAR(255);",
            "ALTER TABLE facial_evaluation ADD COLUMN IF NOT EXISTS generation_id VARCHAR(36);",
            "ALTER TABLE facial_evaluation ADD COLUMN IF NOT EXISTS admin_response TEXT;",
            "ALTER TABLE facial_evaluation ADD COLUMN IF NOT EXISTS admin_id VARCHAR(36);",
            "ALTER TABLE facial_evaluation ADD COLUMN IF NOT EXISTS credits_used INTEGER DEFAULT 20;"
        ]
        
        for sql in sql_commands:
            try:
                cursor.execute(sql)
                print(f"✅ Executed: {sql}")
            except Exception as e:
                print(f"⚠️  Warning for {sql}: {e}")
        
        # Try to add foreign key constraints
        try:
            cursor.execute("""
                DO $$
                BEGIN
                    BEGIN
                        ALTER TABLE facial_evaluation 
                        ADD CONSTRAINT fk_facial_evaluation_generation 
                        FOREIGN KEY (generation_id) REFERENCES generation(id);
                    EXCEPTION
                        WHEN duplicate_object THEN
                            NULL;
                    END;
                    
                    BEGIN
                        ALTER TABLE facial_evaluation 
                        ADD CONSTRAINT fk_facial_evaluation_admin 
                        FOREIGN KEY (admin_id) REFERENCES "user"(id);
                    EXCEPTION
                        WHEN duplicate_object THEN
                            NULL;
                    END;
                END $$;
            """)
            print("✅ Foreign key constraints added")
        except Exception as e:
            print(f"⚠️  Warning for foreign keys: {e}")
        
        # Commit changes
        conn.commit()
        
        # Verify the table structure
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'facial_evaluation' 
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print("\n📋 Current facial_evaluation table structure:")
        for col in columns:
            print(f"  - {col[0]} ({col[1]}) {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Database schema fix completed successfully!")
        print("🎉 Admin dashboard and facial evaluation pages should now work!")
        
        return True
        
    except Exception as e:
        print(f"❌ Database fix failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = execute_database_fix()
    if not success:
        sys.exit(1)
    print("\n🚀 You can now access the admin dashboard and facial evaluation features!")
