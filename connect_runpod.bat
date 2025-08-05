@echo off
echo RunPod Connection Setup
echo ======================

echo Step 1: Download your SSH key
echo Go to your RunPod dashboard and download the SSH key file (id_ed25519)
echo Save it to: C:\Users\%USERNAME%\.ssh\id_ed25519
echo.

echo Step 2: Set correct permissions (run this in PowerShell as Admin):
echo icacls C:\Users\%USERNAME%\.ssh\id_ed25519 /inheritance:r
echo icacls C:\Users\%USERNAME%\.ssh\id_ed25519 /grant:r %USERNAME%:R
echo.

echo Step 3: Connect with SSH tunnel
echo ssh root@149.36.1.79 -p 33805 -i ~/.ssh/id_ed25519 -L 8188:localhost:8188 -N
echo.

echo Alternative: Use the exact command from your RunPod dashboard:
echo ssh root@149.36.1.79 -p 33805 -i ~/.ssh/id_ed25519
echo.

pause