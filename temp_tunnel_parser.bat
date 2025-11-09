@echo off 
setlocal enabledelayedexpansion 
:loop 
set /p line= 
if "!line!"=="" goto loop 
echo !line! 
echo !line! | findstr "trycloudflare.com" 
if !errorlevel! equ 0 ( 
  for /f "tokens=*" %%a in ('echo !line! | findstr /r "https://[a-zA-Z0-9-]*\.trycloudflare\.com"') do ( 
    for /f "tokens=*" %%b in ('echo %%a | findstr /r /c:"https://[a-zA-Z0-9-]*\.trycloudflare\.com"') do ( 
      set "TUNNEL_URL=%%b" 
      echo Found tunnel URL: !TUNNEL_URL! 
      echo Registering with Railway... 
      curl -H "Content-Type: application/json" -H "X-TUNNEL-SECRET: morphpas" -d "{\"url\":\"!TUNNEL_URL!\"}" "https://psl-morph-production.up.railway.app/register-tunnel" 
      echo Registration complete! 
    ) 
  ) 
) 
goto loop 
