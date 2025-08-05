@echo off
echo Fixing SSH Key Path for Windows
echo ===============================

echo Step 1: Check if key file exists
if exist "C:\Users\yvngt\.ssh\id_ed25519" (
    echo ✅ SSH key found at C:\Users\yvngt\.ssh\id_ed25519
) else (
    echo ❌ SSH key NOT found. Please download it from RunPod dashboard first.
    pause
    exit
)

echo.
echo Step 2: Try connection with full Windows path
echo Command: ssh root@149.36.1.79 -p 33805 -i "C:\Users\yvngt\.ssh\id_ed25519" -L 8188:localhost:8188 -N
echo.

ssh root@149.36.1.79 -p 33805 -i "C:\Users\yvngt\.ssh\id_ed25519" -L 8188:localhost:8188 -N

echo.
echo If it still asks for password, the key might be wrong or corrupted.
echo Try re-downloading from RunPod dashboard.
pause