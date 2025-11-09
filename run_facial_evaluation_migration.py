#!/usr/bin/env python3
"""
Run facial evaluation database migration immediately
This script can be run to fix the database schema issue
"""

import os
import sys

def main():
    """Run the facial evaluation migration"""
    
    print("Running facial evaluation database migration...")
    
    try:
        # Import and run the migration
        from fix_facial_evaluation_database_migration import migrate_facial_evaluation_table
        
        success = migrate_facial_evaluation_table()
        
        if success:
            print("✅ Migration completed successfully!")
            print("The admin dashboard and facial evaluation pages should now work.")
        else:
            print("❌ Migration failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Migration error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
