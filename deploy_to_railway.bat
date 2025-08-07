@echo off
echo 🚀 Railway Deployment with PostgreSQL
echo =====================================

echo.
echo 📋 Pre-deployment checklist:
echo ✓ PostgreSQL service added to Railway project
echo ✓ Database configuration updated in config.py
echo ✓ psycopg2-binary in requirements.txt
echo.

echo 🔄 Committing changes...
git add .
git commit -m "Fix: Database persistence + ComfyUI parameters"

echo.
echo 🚀 Pushing to Railway...
git push origin main

echo.
echo ⏳ Deployment in progress...
echo 📝 Check Railway dashboard for deployment status
echo 🔗 Your app will be available at your Railway domain

echo.
echo 🎯 After deployment:
echo 1. Test user registration/login
echo 2. Create test data
echo 3. Deploy a small change to verify data persists
echo.

pause
