@echo off
echo ==========================================
echo   Bat dau khoi dong Sentify Dashboard...
echo ==========================================

cd /d "%~dp0"

echo [1/3] Kiem tra du lieu moi nhat (export_dashboard_data.py)...
python export_dashboard_data.py

echo [2/3] Khoi dong API Backend (FastAPI - Port 8000)...
start cmd /k "python -m uvicorn api:app --host 127.0.0.1 --port 8000"

echo [3/3] Khoi dong Web Frontend (Local Server - Port 8080)...
start cmd /k "python -m http.server 8080"

echo Dang mo trinh duyet...
timeout /t 3 /nobreak
start http://localhost:8080/dashboard/index.html

echo Da khoi dong xong tat ca 2 Server! (Chi thu nho cac cua so CMD den, KHONG DONG)
pause
