# Facial Evaluation Feature Deployment Guide

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

- All templates load without 404 errors
- Admin can access facial evaluation management
- Users can request facial evaluations
- Database operations work correctly
- No import or template errors in logs
