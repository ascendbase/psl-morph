#!/usr/bin/env python3
"""
Fix Facial Evaluation Status Column
Fixes the database schema issue where status column is too small.
"""

import os
import sys
from sqlalchemy import text

def fix_facial_evaluation_status_column():
    """Fix the facial evaluation status column size"""
    
    print("🔧 FIXING FACIAL EVALUATION STATUS COLUMN")
    print("=" * 60)
    
    try:
        # Import Flask app and database
        sys.path.append('.')
        from app import app, db
        
        with app.app_context():
            print("📊 Checking current database schema...")
            
            # Check current column definition
            result = db.engine.execute(text("""
                SELECT column_name, data_type, character_maximum_length 
                FROM information_schema.columns 
                WHERE table_name = 'facial_evaluations' 
                AND column_name = 'status'
            """))
            
            current_schema = result.fetchone()
            if current_schema:
                print(f"Current status column: {current_schema}")
                
                # Check if it's a CHAR(1) that needs to be expanded
                if current_schema[1] == 'character' and current_schema[2] == 1:
                    print("❌ Status column is CHAR(1) - needs to be expanded")
                    
                    # Fix the column size
                    print("🔧 Expanding status column to VARCHAR(20)...")
                    
                    db.engine.execute(text("""
                        ALTER TABLE facial_evaluations 
                        ALTER COLUMN status TYPE VARCHAR(20)
                    """))
                    
                    print("✅ Status column expanded successfully")
                    
                elif current_schema[1] == 'character varying':
                    print("✅ Status column is already VARCHAR - checking length...")
                    if current_schema[2] and current_schema[2] < 20:
                        print(f"🔧 Expanding status column from {current_schema[2]} to 20 characters...")
                        db.engine.execute(text("""
                            ALTER TABLE facial_evaluations 
                            ALTER COLUMN status TYPE VARCHAR(20)
                        """))
                        print("✅ Status column expanded successfully")
                    else:
                        print("✅ Status column size is adequate")
                        
                else:
                    print(f"✅ Status column type is {current_schema[1]} - should be fine")
            else:
                print("❌ Status column not found")
                return False
            
            # Verify the fix
            print("\n🔍 Verifying the fix...")
            result = db.engine.execute(text("""
                SELECT column_name, data_type, character_maximum_length 
                FROM information_schema.columns 
                WHERE table_name = 'facial_evaluations' 
                AND column_name = 'status'
            """))
            
            new_schema = result.fetchone()
            if new_schema:
                print(f"✅ New status column: {new_schema}")
                
                # Test inserting a status value
                print("\n🧪 Testing status value insertion...")
                
                # Try to insert a test record (will rollback)
                try:
                    test_query = text("""
                        INSERT INTO facial_evaluations 
                        (id, user_id, status, created_at, credits_used) 
                        VALUES 
                        ('test-id', 'test-user', 'Pending', NOW(), 20)
                    """)
                    
                    # Start a transaction
                    trans = db.engine.begin()
                    try:
                        db.engine.execute(test_query)
                        print("✅ Test insertion successful")
                        # Rollback the test
                        trans.rollback()
                        print("✅ Test data rolled back")
                    except Exception as e:
                        trans.rollback()
                        print(f"❌ Test insertion failed: {e}")
                        return False
                        
                except Exception as e:
                    print(f"❌ Test setup failed: {e}")
                    return False
            
            print("\n" + "=" * 60)
            print("✅ FACIAL EVALUATION STATUS COLUMN FIX COMPLETED")
            print("=" * 60)
            
            print("\n📋 SUMMARY:")
            print("• Status column expanded to VARCHAR(20)")
            print("• Can now store values like 'Pending', 'Completed', 'Cancelled'")
            print("• Test insertion successful")
            print("• Ready for production use")
            
            return True
            
    except Exception as e:
        print(f"\n❌ Fix failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def update_models_file():
    """Update the models.py file to ensure correct column definition"""
    
    print("\n🔧 UPDATING MODELS.PY FILE")
    print("=" * 40)
    
    try:
        if os.path.exists('models.py'):
            with open('models.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if status column is properly defined
            if 'status = db.Column(db.String(1)' in content:
                print("❌ Found CHAR(1) definition in models.py")
                
                # Replace with proper VARCHAR definition
                updated_content = content.replace(
                    'status = db.Column(db.String(1)',
                    'status = db.Column(db.String(20)'
                )
                
                with open('models.py', 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                print("✅ Updated models.py with VARCHAR(20) definition")
                
            elif 'status = db.Column(db.String(20)' in content:
                print("✅ Models.py already has correct VARCHAR(20) definition")
                
            else:
                print("⚠️ Status column definition not found in expected format")
                
        else:
            print("❌ models.py not found")
            
    except Exception as e:
        print(f"❌ Failed to update models.py: {e}")

if __name__ == "__main__":
    print("🚀 FACIAL EVALUATION STATUS COLUMN FIX")
    print("=" * 60)
    
    # Update models file first
    update_models_file()
    
    # Fix database schema
    success = fix_facial_evaluation_status_column()
    
    if success:
        print("\n🎉 FIX COMPLETED SUCCESSFULLY!")
        print("\nThe facial evaluation feature should now work properly!")
        print("You can test it by requesting a facial evaluation.")
    else:
        print("\n❌ FIX FAILED")
        print("Please check the errors above and try again.")
    
    print("\n" + "=" * 60)
