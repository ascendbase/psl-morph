#!/usr/bin/env python3
"""
Fix admin privileges for ascendbase@gmail.com
"""

import os
import sys
from models import db, User, init_db
from flask import Flask

def fix_admin_privileges():
    """Fix admin privileges for the user"""
    print("🔧 Fixing Admin Privileges")
    print("=" * 40)
    
    # Create Flask app context
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///face_morph.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    init_db(app)
    
    with app.app_context():
        # Find the user
        user = User.query.filter_by(email='ascendbase@gmail.com').first()
        
        if user:
            print(f"✅ Found user: {user.email}")
            print(f"   Current admin status: {user.is_admin}")
            print(f"   Current credits: {user.credits}")
            
            # Update admin privileges
            user.is_admin = True
            user.credits = 1000  # Give admin credits
            
            db.session.commit()
            
            print("✅ Updated user privileges:")
            print(f"   Admin status: {user.is_admin}")
            print(f"   Credits: {user.credits}")
            
        else:
            print("❌ User not found. Creating new admin user...")
            
            # Create new admin user
            admin = User(
                email='ascendbase@gmail.com',
                is_admin=True,
                credits=1000
            )
            admin.set_password('morphpas')
            
            db.session.add(admin)
            db.session.commit()
            
            print("✅ Created new admin user:")
            print(f"   Email: {admin.email}")
            print(f"   Admin status: {admin.is_admin}")
            print(f"   Credits: {admin.credits}")
        
        # Remove old admin if exists
        old_admin = User.query.filter_by(email='admin@example.com').first()
        if old_admin:
            db.session.delete(old_admin)
            db.session.commit()
            print("✅ Removed old admin user")
        
        print()
        print("🎉 Admin privileges fixed!")
        print("   You can now access the admin panel.")
        print("   Restart the app and login again.")

if __name__ == "__main__":
    fix_admin_privileges()