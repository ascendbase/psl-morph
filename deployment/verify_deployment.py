#!/usr/bin/env python3
"""
Deployment verification script
Checks if all facial evaluation features are working
"""

import os
import sys
from pathlib import Path

def verify_deployment():
    """Verify deployment is working correctly"""
    
    print("Verifying deployment...")
    
    # Check if templates exist
    template_files = [
        'templates/admin/facial_evaluations.html',
        'templates/admin/respond_facial_evaluation.html',
        'templates/facial_evaluation/dashboard.html',
        'templates/admin/dashboard.html'
    ]
    
    for template_file in template_files:
        if Path(template_file).exists():
            print(f"Template exists: {template_file}")
        else:
            print(f"Missing template: {template_file}")
            return False
    
    # Check if app can import models
    try:
        from app import app, db
        from models import User, FacialEvaluation
        print("App and models import successfully")
    except Exception as e:
        print(f"Import error: {e}")
        return False
    
    # Check if database connection works
    try:
        with app.app_context():
            db.create_all()
            FacialEvaluation.query.first()
            print("Database connection working")
    except Exception as e:
        print(f"Database error: {e}")
        return False
    
    print("Deployment verification passed!")
    return True

if __name__ == "__main__":
    success = verify_deployment()
    if not success:
        sys.exit(1)
