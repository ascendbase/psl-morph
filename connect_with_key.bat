@echo off
echo ========================================
echo   Connect RunPod GPU using SSH Key
echo ========================================
echo.

echo Step 1: Checking if SSH key exists...
if exist "C:\Users\yvngt\.ssh\id_ed25519" (
    echo ✅ SSH key found at C:\Users\yvngt\.ssh\id_ed25519
) else (
    echo ❌ SSH key not found!
    echo.
    echo Please download your SSH key from RunPod dashboard:
    echo 1. Go to your RunPod dashboard
    echo 2. Look for "SSH Keys" or "Download Key"
    echo 3. Save the key as: C:\Users\yvngt\.ssh\id_ed25519
    echo.
    pause
    exit
)

echo.
echo Step 2: Creating SSH tunnel with key authentication...
echo Command: ssh root@149.36.1.79 -p 33805 -i "C:\Users\yvngt\.ssh\id_ed25519" -L 8188:localhost:8188 -N
echo.
echo This should connect without asking for password!
echo Keep this window open after connecting.
echo.

pause
echo Starting SSH tunnel...
ssh root@149.36.1.79 -p 33805 -i "C:\Users\yvngt\.ssh\id_ed25519" -L 8188:localhost:8188 -N -o StrictHostKeyChecking=no

echo.
echo If you see this message, the tunnel was closed.
echo Check if it worked by opening: http://localhost:8188
pause