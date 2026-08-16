@echo off
chcp 65001 >nul
title 国考刷题网站 - 一键启动
echo ============================================
echo   国考刷题网站（RuoYi + 2000-2022 行测真题）
echo ============================================
echo.

rem ---------- MySQL (3306) ----------
netstat -ano | findstr ":3306" | findstr "LISTENING" >nul
if %errorlevel%==0 (
  echo [OK] MySQL 已在运行
) else (
  echo [..] 启动 MySQL ...
  start "MySQL" /min "C:\Users\admin\DSH\tools\mysql57\bin\mysqld.exe" --defaults-file="C:\Users\admin\DSH\tools\mysql57\my.ini"
  timeout /t 6 /nobreak >nul
)

rem ---------- Redis (6379) ----------
netstat -ano | findstr ":6379" | findstr "LISTENING" >nul
if %errorlevel%==0 (
  echo [OK] Redis 已在运行
) else (
  echo [..] 启动 Redis ...
  start "Redis" /min "C:\Users\admin\DSH\tools\redis\redis-server.exe" --port 6379
  timeout /t 3 /nobreak >nul
)

rem ---------- 后端 (8080) ----------
netstat -ano | findstr ":8080" | findstr "LISTENING" >nul
if %errorlevel%==0 (
  echo [OK] 后端服务已在运行
) else (
  echo [..] 启动后端 (Spring Boot) ...
  start "RuoYi-Backend" /min "C:\Users\admin\DSH\tools\zulu8\bin\java.exe" -jar "C:\Users\admin\DSH\ruoyi-backend\ruoyi-admin\target\ruoyi-admin.jar"
  timeout /t 40 /nobreak >nul
)

rem ---------- 前端 (8090) ----------
netstat -ano | findstr ":8090" | findstr "LISTENING" >nul
if %errorlevel%==0 (
  echo [OK] 前端服务已在运行
) else (
  echo [..] 启动前端 ...
  start "RuoYi-Frontend" /min cmd /c "cd /d C:\Users\admin\DSH\ruoyi && node server.cjs"
  timeout /t 3 /nobreak >nul
)

echo.
echo ============================================
echo   刷题网站:  http://127.0.0.1:8090
echo   账号: admin    密码: admin123
echo   后端 API: http://127.0.0.1:8080
echo ============================================
start http://127.0.0.1:8090
pause
