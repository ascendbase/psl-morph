#!/usr/bin/env python3
"""
Fix email verification token expiration issue

The current verification logic incorrectly uses user.created_at to check token expiration,
but it should track when the verification token was generated, especially for resent tokens.

This script:
1. Adds verification_token_created_at column to User model
2. Updates existing users with current timestamp for their tokens
3. Fixes the verification logic in auth.py
"""

import os
import sys
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, User
from sqlalchemy import text

def add_verification_token_timestamp_column():
    """Add verification_token_created_at column to users table"""
    try:
        app = create_app()
        
        with app.app_context():
            # Check if column already exists
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'user' 
                AND column_name = 'verification_token_created_at'
            """))
            
            if result.fetchone():
                print("✅ verification_token_created_at column already exists")
                return True
            
            # Add the new column
            print("📝 Adding verification_token_created_at column...")
            db.session.execute(text("""
                ALTER TABLE "user" 
                ADD COLUMN verification_token_created_at TIMESTAMP
            """))
            
            # Update existing users who have verification tokens
            print("🔄 Updating existing users with verification tokens...")
            current_time = datetime.utcnow()
            
            db.session.execute(text("""
                UPDATE "user" 
                SET verification_token_created_at = :current_time 
                WHERE verification_token IS NOT NULL 
                AND verification_token != ''
            """), {'current_time': current_time})
            
            db.session.commit()
            print("✅ Successfully added verification_token_created_at column and updated existing users")
            return True
            
    except Exception as e:
        print(f"❌ Error adding verification_token_created_at column: {e}")
        return False

def update_models_file():
    """Update models.py to include the new field"""
    try:
        print("📝 Updating models.py...")
        
        # Read current models.py
        with open('models.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if already updated
        if 'verification_token_created_at' in content:
            print("✅ models.py already contains verification_token_created_at field")
            return True
        
        # Add the new field after verification_token
        old_line = "    verification_token = db.Column(db.String(100))"
        new_lines = """    verification_token = db.Column(db.String(100))
    verification_token_created_at = db.Column(db.DateTime)"""
        
        if old_line in content:
            content = content.replace(old_line, new_lines)
            
            # Write updated content
            with open('models.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Successfully updated models.py")
            return True
        else:
            print("❌ Could not find verification_token field in models.py")
            return False
            
    except Exception as e:
        print(f"❌ Error updating models.py: {e}")
        return False

def update_auth_file():
    """Update auth.py to fix the verification logic"""
    try:
        print("📝 Updating auth.py verification logic...")
        
        # Read current auth.py
        with open('auth.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if already updated
        if 'verification_token_created_at' in content:
            print("✅ auth.py already contains updated verification logic")
            return True
        
        # Fix the token expiration check
        old_logic = """    # Check if token is expired (24 hours)
    if user.created_at < datetime.utcnow() - timedelta(hours=24):
        flash('Verification link has expired. Please register again.', 'error')
        return redirect(url_for('auth.register'))"""
        
        new_logic = """    # Check if token is expired (24 hours)
    if user.verification_token_created_at and user.verification_token_created_at < datetime.utcnow() - timedelta(hours=24):
        flash('Verification link has expired. Please request a new verification email.', 'error')
        return redirect(url_for('auth.resend_verification'))
    elif not user.verification_token_created_at and user.created_at < datetime.utcnow() - timedelta(hours=24):
        # Fallback for old tokens without timestamp
        flash('Verification link has expired. Please request a new verification email.', 'error')
        return redirect(url_for('auth.resend_verification'))"""
        
        if old_logic in content:
            content = content.replace(old_logic, new_logic)
        else:
            print("⚠️ Could not find exact token expiration logic, trying alternative approach...")
            # Try to find and replace the specific line
            old_line = "    if user.created_at < datetime.utcnow() - timedelta(hours=24):"
            new_line = "    if user.verification_token_created_at and user.verification_token_created_at < datetime.utcnow() - timedelta(hours=24):"
            
            if old_line in content:
                content = content.replace(old_line, new_line)
                # Also update the error message redirect
                content = content.replace(
                    "return redirect(url_for('auth.register'))",
                    "return redirect(url_for('auth.resend_verification'))"
                )
            else:
                print("❌ Could not find token expiration logic in auth.py")
                return False
        
        # Update the resend verification logic to set timestamp
        old_resend = """    # Generate new verification token
    verification_token = generate_verification_token()
    user.verification_token = verification_token
    db.session.commit()"""
        
        new_resend = """    # Generate new verification token
    verification_token = generate_verification_token()
    user.verification_token = verification_token
    user.verification_token_created_at = datetime.utcnow()
    db.session.commit()"""
        
        if old_resend in content:
            content = content.replace(old_resend, new_resend)
        
        # Update the registration logic to set timestamp
        old_register = """        # Generate verification token
        verification_token = generate_verification_token()
        
        # Create new user (not verified initially)
        user = User(
            email=email,
            is_verified=False,
            verification_token=verification_token
        )"""
        
        new_register = """        # Generate verification token
        verification_token = generate_verification_token()
        
        # Create new user (not verified initially)
        user = User(
            email=email,
            is_verified=False,
            verification_token=verification_token,
            verification_token_created_at=datetime.utcnow()
        )"""
        
        if old_register in content:
            content = content.replace(old_register, new_register)
        
        # Write updated content
        with open('auth.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Successfully updated auth.py")
        return True
        
    except Exception as e:
        print(f"❌ Error updating auth.py: {e}")
        return False

def main():
    """Main function to fix email verification token expiration"""
    print("🔧 Fixing Email Verification Token Expiration Issue")
    print("=" * 60)
    
    # Step 1: Add database column
    if not add_verification_token_timestamp_column():
        print("❌ Failed to add database column")
        return False
    
    # Step 2: Update models.py
    if not update_models_file():
        print("❌ Failed to update models.py")
        return False
    
    # Step 3: Update auth.py
    if not update_auth_file():
        print("❌ Failed to update auth.py")
        return False
    
    print("\n" + "=" * 60)
    print("✅ Email verification token expiration fix completed successfully!")
    print("\nChanges made:")
    print("1. ✅ Added verification_token_created_at column to database")
    print("2. ✅ Updated models.py with new field")
    print("3. ✅ Fixed verification logic in auth.py")
    print("\nThe verification system now properly tracks token generation time")
    print("and will correctly handle token expiration for both new and resent tokens.")
    
    return True

if __name__ == "__main__":
    main()
