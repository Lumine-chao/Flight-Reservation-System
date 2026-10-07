@echo off
setlocal

echo ============================================
echo   航班预订系统 - 停止服务
echo ============================================
echo.

echo [1/2] 关闭后端 / 前端命令行窗口 ...
taskkill /F /T /FI "WINDOWTITLE eq flight-backend*" >nul 2>&1
taskkill /F /T /FI "WINDOWTITLE eq flight-frontend*" >nul 2>&1

echo [2/2] 兜底清理占用 8080 / 5173 端口的进程 ...
for %%P in (8080 5173) do (
    for /f "tokens=5" %%A in ('netstat -ano ^| findstr ":%%P " ^| findstr "LISTENING"') do (
        taskkill /F /T /PID %%A >nul 2>&1
    )
)

echo.
echo 已停止后端 8080 与前端 5173。
echo.
pause
