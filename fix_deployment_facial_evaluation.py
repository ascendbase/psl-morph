#!/usr/bin/env python3
"""
Fix deployment files to ensure facial evaluation feature works properly
Updates all deployment configurations and creates missing directories
"""

import os
import shutil
from pathlib import Path

def fix_deployment_facial_evaluation():
    """Fix all deployment files for facial evaluation feature"""
    
    print("🚀 Fixing deployment files for facial evaluation feature...")
    
    # 1. Update Dockerfile to include facial evaluation templates
    dockerfile_content = """FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads outputs templates/admin templates/facial_evaluation

# Ensure all template directories exist
RUN mkdir -p templates/admin templates/facial_evaluation templates/auth templates/payments

# Set environment variables
ENV ENVIRONMENT=production
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:5000/health', timeout=10)"

# Run the application
CMD ["python", "app.py"]"""

    with open('deployment/Dockerfile', 'w') as f:
        f.write(dockerfile_content)
    print("✅ Updated deployment/Dockerfile")
    
    # 2. Update railway.toml to include database initialization
    railway_toml_content = """[build]
builder = "NIXPACKS"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
startCommand = "python -c 'from app import app, db; app.app_context().push(); db.create_all()' && python app.py"

[env]
ENVIRONMENT = "production"
PORT = "5000"
FLASK_ENV = "production"
"""

    with open('deployment/railway.toml', 'w') as f:
        f.write(railway_toml_content)
    print("✅ Updated deployment/railway.toml")
    
    # 3. Update Procfile to include database initialization
    procfile_content = """release: python -c "from app import app, db; app.app_context().push(); db.create_all()"
web: python app.py"""

    with open('deployment/Procfile', 'w') as f:
        f.write(procfile_content)
    print("✅ Updated deployment/Procfile")
    
    # 4. Create a deployment initialization script
    init_script_content = """#!/usr/bin/env python3
\"\"\"
Deployment initialization script
Ensures database tables are created and app is ready
\"\"\"

import os
import sys

def init_deployment():
    \"\"\"Initialize deployment with database setup\"\"\"
    
    try:
        # Import app and models
        from app import app, db
        from models import User, FacialEvaluation
        
        print("🔧 Initializing deployment...")
        
        with app.app_context():
            # Create all database tables
            db.create_all()
            print("✅ Database tables created")
            
            # Verify facial evaluation table exists
            try:
                FacialEvaluation.query.first()
                print("✅ FacialEvaluation table verified")
            except Exception as e:
                print(f"⚠️ FacialEvaluation table issue: {e}")
            
            print("🎉 Deployment initialization completed!")
            return True
            
    except Exception as e:
        print(f"❌ Deployment initialization failed: {e}")
        return False

if __name__ == "__main__":
    success = init_deployment()
    if not success:
        sys.exit(1)
"""

    with open('deployment/init_deployment.py', 'w') as f:
        f.write(init_script_content)
    print("✅ Created deployment/init_deployment.py")
    
    # 5. Create a deployment verification script
    verify_script_content = """#!/usr/bin/env python3
\"\"\"
Deployment verification script
Checks if all facial evaluation features are working
\"\"\"

import os
import sys
import requests
from pathlib import Path

def verify_deployment():
    \"\"\"Verify deployment is working correctly\"\"\"
    
    print("🔍 Verifying deployment...")
    
    # Check if templates exist
    template_files = [
        'templates/admin/facial_evaluations.html',
        'templates/admin/respond_facial_evaluation.html',
        'templates/facial_evaluation/dashboard.html',
        'templates/admin/dashboard.html'
    ]
    
    for template_file in template_files:
        if Path(template_file).exists():
            print(f"✅ Template exists: {template_file}")
        else:
            print(f"❌ Missing template: {template_file}")
            return False
    
    # Check if app can import models
    try:
        from app import app, db
        from models import User, FacialEvaluation
        print("✅ App and models import successfully")
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Check if database connection works
    try:
        with app.app_context():
            db.create_all()
            FacialEvaluation.query.first()
            print("✅ Database connection working")
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False
    
    print("🎉 Deployment verification passed!")
    return True

if __name__ == "__main__":
    success = verify_deployment()
    if not success:
        sys.exit(1)
"""

    with open('deployment/verify_deployment.py', 'w') as f:
        f.write(verify_script_content)
    print("✅ Created deployment/verify_deployment.py")
    
    # 6. Create a comprehensive deployment guide
    deployment_guide = """# Facial Evaluation Feature Deployment Guide

## Overview
This guide ensures the facial evaluation feature is properly deployed with all templates and database tables.

## Deployment Files Updated

### 1. deployment/Dockerfile
- Added template directory creation
- Ensures all facial evaluation templates are included
- Creates necessary upload/output directories

### 2. deployment/railway.toml
- Added database initialization to start command
- Ensures tables are created on deployment

### 3. deployment/Procfile
- Added release phase for database initialization
- Ensures Heroku/Railway creates tables before starting app

### 4. deployment/init_deployment.py
- Initialization script for deployment
- Creates database tables and verifies setup

### 5. deployment/verify_deployment.py
- Verification script to check deployment
- Validates templates and database connectivity

## Deployment Steps

### For Railway:
1. Push code to repository
2. Railway will automatically use railway.toml configuration
3. Database tables will be created automatically
4. Facial evaluation feature will be available

### For Heroku:
1. Push code to repository
2. Heroku will run the release phase from Procfile
3. Database tables will be created automatically
4. Facial evaluation feature will be available

### For Docker:
1. Build image: `docker build -f deployment/Dockerfile -t morph-app .`
2. Run container: `docker run -p 5000:5000 morph-app`
3. Database tables will be created automatically

## Verification

Run the verification script to ensure everything is working:
```bash
python deployment/verify_deployment.py
```

## Templates Included

The following facial evaluation templates are included:
- `templates/admin/facial_evaluations.html` - Admin view of all requests
- `templates/admin/respond_facial_evaluation.html` - Admin response form
- `templates/facial_evaluation/dashboard.html` - User facial evaluation dashboard
- `templates/admin/dashboard.html` - Updated admin dashboard

## Database Tables

The following tables will be created automatically:
- `users` - User accounts
- `facial_evaluation` - Facial evaluation requests and responses

## Environment Variables

Ensure these environment variables are set:
- `DATABASE_URL` - PostgreSQL connection string
- `ENVIRONMENT` - Set to "production"
- `PORT` - Port number (default: 5000)

## Troubleshooting

If facial evaluation pages show 404 errors:
1. Check if templates exist in the correct directories
2. Verify database tables are created
3. Run the verification script
4. Check application logs for import errors

## Success Indicators

✅ All templates load without 404 errors
✅ Admin can access facial evaluation management
✅ Users can request facial evaluations
✅ Database operations work correctly
✅ No import or template errors in logs
"""

    with open('deployment/FACIAL_EVALUATION_DEPLOYMENT_GUIDE.md', 'w') as f:
        f.write(deployment_guide)
    print("✅ Created deployment/FACIAL_EVALUATION_DEPLOYMENT_GUIDE.md")
    
    # 7. Ensure template directories exist
    template_dirs = [
        'templates/admin',
        'templates/facial_evaluation',
        'templates/auth',
        'templates/payments'
    ]
    
    for template_dir in template_dirs:
        Path(template_dir).mkdir(parents=True, exist_ok=True)
        print(f"✅ Ensured directory exists: {template_dir}")
    
    # 8. Create a deployment checklist
    checklist_content = """# Facial Evaluation Deployment Checklist

## Pre-Deployment Checklist

### Code Files
- [ ] `app.py` includes facial evaluation routes
- [ ] `models.py` includes FacialEvaluation model
- [ ] `forms.py` includes facial evaluation forms
- [ ] All template files exist in correct directories

### Template Files
- [ ] `templates/admin/facial_evaluations.html`
- [ ] `templates/admin/respond_facial_evaluation.html`
- [ ] `templates/facial_evaluation/dashboard.html`
- [ ] `templates/admin/dashboard.html`

### Deployment Files
- [ ] `deployment/Dockerfile` updated
- [ ] `deployment/railway.toml` updated
- [ ] `deployment/Procfile` updated
- [ ] `requirements.txt` includes all dependencies

### Database
- [ ] PostgreSQL database configured
- [ ] DATABASE_URL environment variable set
- [ ] Database initialization scripts ready

## Post-Deployment Checklist

### Functionality Tests
- [ ] App starts without errors
- [ ] Database tables created successfully
- [ ] Admin dashboard loads
- [ ] Facial evaluation pages load
- [ ] User can request facial evaluation
- [ ] Admin can respond to requests

### Error Checks
- [ ] No 404 errors on facial evaluation pages
- [ ] No import errors in logs
- [ ] No database connection errors
- [ ] No template rendering errors

### Feature Verification
- [ ] Facial evaluation request flow works
- [ ] Admin response flow works
- [ ] Credit deduction works (20 credits)
- [ ] Image upload works
- [ ] Status updates work (pending/completed)

## Deployment Commands

### Railway
```bash
# Push to repository - Railway deploys automatically
git push origin main
```

### Heroku
```bash
# Deploy to Heroku
git push heroku main
```

### Docker
```bash
# Build and run Docker container
docker build -f deployment/Dockerfile -t morph-app .
docker run -p 5000:5000 morph-app
```

### Manual Verification
```bash
# Run verification script
python deployment/verify_deployment.py
```
"""

    with open('deployment/DEPLOYMENT_CHECKLIST.md', 'w') as f:
        f.write(checklist_content)
    print("✅ Created deployment/DEPLOYMENT_CHECKLIST.md")
    
    print("\n🎉 Deployment fix completed successfully!")
    print("✅ All deployment files updated")
    print("✅ Template directories ensured")
    print("✅ Database initialization configured")
    print("✅ Verification scripts created")
    print("✅ Documentation created")
    
    print("\n📋 Next Steps:")
    print("1. Review the deployment guide: deployment/FACIAL_EVALUATION_DEPLOYMENT_GUIDE.md")
    print("2. Check the deployment checklist: deployment/DEPLOYMENT_CHECKLIST.md")
    print("3. Run verification: python deployment/verify_deployment.py")
    print("4. Deploy to your platform (Railway/Heroku/Docker)")
    
    return True

if __name__ == "__main__":
    fix_deployment_facial_evaluation()
