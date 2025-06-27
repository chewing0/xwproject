@echo off
echo 启动知识图谱模块...

echo.
echo 1. 启动后端服务...
cd /d "%~dp0backend"
start cmd /k "python manage.py runserver 8000"

echo.
echo 2. 等待后端启动...
timeout /t 3 /nobreak > nul

echo.
echo 3. 启动前端服务...
cd /d "%~dp0frontend"
start cmd /k "npm run serve"

echo.
echo 服务启动完成！
echo 前端地址: http://localhost:8080
echo 后端地址: http://localhost:8000
echo.
echo 请确保Neo4j数据库已启动(bolt://localhost:7687)
echo.
pause
