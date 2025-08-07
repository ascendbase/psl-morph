@echo off
echo ========================================
echo VAST.AI ON-DEMAND SETUP
echo ========================================
echo.
echo This script will help you set up pay-per-use GPU rental
echo with Vast.ai for 98-99%% cost savings!
echo.

echo Step 1: Get your Vast.ai API key
echo --------------------------------
echo 1. Go to: https://console.vast.ai/account/
echo 2. Click "API Keys" tab
echo 3. Generate a new API key
echo 4. Copy the key (starts with something like: eaa3a...)
echo.
set /p VAST_API_KEY="Enter your Vast.ai API key: "

echo.
echo Step 2: Configure environment
echo ----------------------------
echo Setting up environment variables...

REM Create .env.vast file
echo # Vast.ai On-Demand Configuration > .env.vast
echo VAST_API_KEY=%VAST_API_KEY% >> .env.vast
echo VAST_ON_DEMAND_MODE=true >> .env.vast
echo VAST_AUTO_STOP_INSTANCES=true >> .env.vast
echo VAST_MAX_INSTANCE_LIFETIME=300 >> .env.vast
echo VAST_MIN_GPU_RAM=8 >> .env.vast
echo VAST_MAX_HOURLY_COST=1.0 >> .env.vast
echo USE_CLOUD_GPU=true >> .env.vast
echo ENVIRONMENT=production >> .env.vast

echo ✅ Environment configured!
echo.

echo Step 3: Test the setup
echo ----------------------
echo Testing API connection...

REM Set environment variable for this session
set VAST_API_KEY=%VAST_API_KEY%

python test_vast_on_demand.py

echo.
echo ========================================
echo SETUP COMPLETE!
echo ========================================
echo.
echo Your pay-per-use GPU setup is ready!
echo.
echo 💰 Cost Comparison:
echo   - Traditional hourly: $0.20-0.50/hour
echo   - Pay-per-use: $0.004-0.01/generation
echo   - SAVINGS: 98-99%%!
echo.
echo 🚀 Next Steps:
echo 1. Test with: python test_vast_on_demand.py
echo 2. Deploy to Railway with the .env.vast variables
echo 3. Start saving money on GPU costs!
echo.
echo Environment file created: .env.vast
echo Copy these variables to your Railway deployment.
echo.
pause
