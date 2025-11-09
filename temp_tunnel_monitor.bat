@echo off 
set "WEBHOOK=https://psl-morph-production.up.railway.app/register-tunnel" 
set "SECRET=morphpas" 
set "PY_CMD=python" 
set "REPO_DIR=D:\Morph-app\" 
 
echo Starting cloudflared tunnel... 
cloudflared tunnel --url http://localhost:8188 | "D:\Morph-app\temp_tunnel_parser.bat" 
