#!/usr/bin/env python3
"""
Direct fix for Railway database column length issue
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError

def get_railway_database_url():
    """Get Railway database URL from environment"""
    # Railway provides DATABASE_URL
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        return database_url
    
    # Try other common environment variables
    postgres_url = os.getenv('POSTGRES_URL')
    if postgres_url:
        return postgres_url
    
    # Try Railway specific variables
    railway_db_url = os.getenv('RAILWAY_DATABASE_URL')
    if railway_db_url:
        return railway_db_url
    
    print("❌ No database URL found in environment variables")
    print("Available environment variables:")
    for key in os.environ:
        if 'DATABASE' in key.upper() or 'POSTGRES' in key.upper():
            print(f"  • {key}: {os.environ[key][:50]}...")
    
    return None

def fix_database_schema():
    """Fix the database schema column length issues"""
    database_url = get_railway_database_url()
    
    if not database_url:
        return False
    
    print(f"🔧 FIXING RAILWAY DATABASE SCHEMA COLUMN LENGTH ISSUES")
    print("=" * 60)
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        print(f"✅ Connected to Railway database")
        
        # Check current schema
        inspector = inspect(engine)
        
        if 'facial_evaluation' not in inspector.get_table_names():
            print("❌ facial_evaluation table does not exist")
            return False
        
        # Get current columns
        columns = inspector.get_columns('facial_evaluation')
        print("\n📋 Current facial_evaluation table schema:")
        
        problematic_columns = []
        for col in columns:
            col_type = str(col['type'])
            print(f"  • {col['name']}: {col_type}")
            
            # Check for problematic columns
            if col['name'] in ['original_image_filename', 'morphed_image_filename', 'secondary_image_filename']:
                if 'CHARACTER(1)' in col_type.upper() or 'CHAR(1)' in col_type.upper():
                    problematic_columns.append(col['name'])
                    print(f"    ⚠️ PROBLEMATIC: {col['name']} is {col_type} (should be VARCHAR)")
        
        if not problematic_columns:
            print("\n✅ No problematic columns found. Schema looks correct.")
            return True
        
        print(f"\n🔧 Found {len(problematic_columns)} problematic columns to fix:")
        for col in problematic_columns:
            print(f"  • {col}")
        
        # Fix the columns
        with engine.connect() as conn:
            with conn.begin():
                for col_name in problematic_columns:
                    print(f"\n🔧 Fixing column: {col_name}")
                    
                    # Alter column type
                    alter_sql = f"""
                    ALTER TABLE facial_evaluation 
                    ALTER COLUMN {col_name} TYPE VARCHAR(255)
                    """
                    
                    try:
                        conn.execute(text(alter_sql))
                        print(f"✅ Fixed {col_name}: changed to VARCHAR(255)")
                    except Exception as e:
                        print(f"❌ Error fixing {col_name}: {e}")
                        return False
        
        print("\n🎉 RAILWAY DATABASE SCHEMA FIX COMPLETE!")
        print("\n📋 Summary:")
        print(f"• Fixed {len(problematic_columns)} columns")
        print("• All filename columns now support 255 characters")
        print("• 2-image upload should work correctly now")
        
        return True
        
    except SQLAlchemyError as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def verify_fix():
    """Verify the fix worked"""
    database_url = get_railway_database_url()
    
    if not database_url:
        return False
    
    try:
        engine = create_engine(database_url)
        inspector = inspect(engine)
        
        print("\n🔍 VERIFYING FIX")
        print("=" * 30)
        
        columns = inspector.get_columns('facial_evaluation')
        filename_columns = [col for col in columns if 'filename' in col['name']]
        
        all_good = True
        for col in filename_columns:
            col_type = str(col['type'])
            if 'VARCHAR' in col_type.upper() or 'TEXT' in col_type.upper():
                print(f"✅ {col['name']}: {col_type}")
            else:
                print(f"❌ {col['name']}: {col_type} (still problematic)")
                all_good = False
        
        if all_good:
            print("\n🎉 VERIFICATION PASSED!")
            print("All filename columns are now properly sized.")
        else:
            print("\n❌ VERIFICATION FAILED!")
            print("Some columns still have issues.")
        
        return all_good
        
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

def main():
    """Main function"""
    print("🚀 RAILWAY DATABASE COLUMN LENGTH FIX UTILITY")
    print("=" * 50)
    
    # Fix the schema
    if fix_database_schema():
        # Verify the fix
        if verify_fix():
            print("\n✅ SUCCESS: Railway database schema fixed and verified!")
            print("\n🎯 Next steps:")
            print("1. Restart your Railway application")
            print("2. Test the 2-image upload feature")
            print("3. Check that facial evaluation requests work")
            return 0
        else:
            print("\n❌ FAILED: Fix verification failed")
            return 1
    else:
        print("\n❌ FAILED: Could not fix database schema")
        return 1

if __name__ == "__main__":
    sys.exit(main())
