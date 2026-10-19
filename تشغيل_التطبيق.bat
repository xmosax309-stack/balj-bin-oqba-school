@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo تشغيل تطبيق قاعدة بيانات مدرسة بلج بن عقبة...
echo.
python -m streamlit run app.py --server.port 3001
pause
