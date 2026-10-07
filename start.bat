@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ============================================
echo   航班预订系统 - 本地开发启动
echo ============================================
echo.

if not exist "backend\.venv\Scripts\python.exe" (
    echo [错误] 未找到 backend\.venv，请先创建虚拟环境并安装依赖。
    pause
    exit /b 1
)
if not exist "frontend\node_modules" (
    echo [错误] 未找到 frontend\node_modules，请先执行 npm install。
    pause
    exit /b 1
)

rem ---- 定位 npm：优先系统 PATH，其次 TRAE 自带 node ----
where npm >nul 2>&1
if not errorlevel 1 goto npm_ok

set "TRAE_NODE=%APPDATA%\TRAE SOLO CN\ModularData\ai-agent\vm\tools\node"
if not exist "%TRAE_NODE%\npm.cmd" goto npm_missing
set "PATH=%TRAE_NODE%;%PATH%"
echo [提示] 系统未安装 Node.js，已临时改用 TRAE 自带 node 运行前端。
echo.
goto npm_ok

:npm_missing
echo [错误] 未检测到 npm。
echo        请安装 Node.js LTS（https://nodejs.org）后重新运行本脚本。
echo.
pause
exit /b 1

:npm_ok
echo [1/2] 启动后端 FastAPI http://localhost:8080 ...
start "flight-backend" cmd /k "cd /d %~dp0backend && .venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8080"

echo [2/2] 启动前端 Vite http://localhost:5173 ...
start "flight-frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo 等待前端就绪后自动打开浏览器 ...
set /a _n=0
:wait_fe
ping -n 2 127.0.0.1 >nul
set /a _n+=1
netstat -ano | findstr ":5173 " | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 goto fe_ready
if !_n! lss 30 goto wait_fe

:fe_ready
start "" http://localhost:5173

echo.
echo 启动完成：
echo   客户前台   http://localhost:5173
echo   管理后台   http://localhost:5173/admin/login
echo   API 文档   http://localhost:8080/docs
echo.
echo 关闭服务请运行 stop.bat
echo.
pause
