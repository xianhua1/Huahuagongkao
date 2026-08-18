@echo off
chcp 65001 >nul
setlocal
title 花花公考刷题 - 一键启动
echo ============================================
echo   花花公考刷题 - 一键启动
echo ============================================
echo.

rem 脚本所在目录（项目根，兼容任意路径部署）
set "ROOT=%~dp0"
cd /d "%ROOT%"

rem ---------- MySQL (3306) ----------
netstat -ano | findstr ":3306" | findstr "LISTENING" >nul
if %errorlevel%==0 (
  echo [OK] MySQL 已在运行
) else (
  echo [..] 启动 MySQL ...
  rem 优先用项目自带 tools\mysql57，否则尝试系统 MySQL
  if exist "%ROOT%tools\mysql57\bin\mysqld.exe" (
    start "MySQL" /min "%ROOT%tools\mysql57\bin\mysqld.exe" --defaults-file="%ROOT%tools\mysql57\my.ini"
  ) else (
    rem 尝试 Windows 服务
    net start MySQL >nul 2>nul
    if %errorlevel% neq 0 (
      echo [X] 未找到 MySQL！请安装 MySQL 5.7+ 并启动服务，或放到 tools\mysql57\
    )
  )
  timeout /t 8 /nobreak >nul
)

rem ---------- Redis (6379) ----------
netstat -ano | findstr ":6379" | findstr "LISTENING" >nul
if %errorlevel%==0 (
  echo [OK] Redis 已在运行
) else (
  echo [..] 启动 Redis ...
  if exist "%ROOT%tools\redis\redis-server.exe" (
    start "Redis" /min "%ROOT%tools\redis\redis-server.exe" --port 6379
  ) else (
    where redis-server >nul 2>nul
    if %errorlevel%==0 (
      start "Redis" /min redis-server --port 6379
    ) else (
      echo [X] 未找到 Redis！请安装 Redis 并启动，或放到 tools\redis\
    )
  )
  timeout /t 3 /nobreak >nul
)

rem ---------- 后端 (8080) ----------
set "JAR=%ROOT%ruoyi-backend\ruoyi-admin\target\ruoyi-admin.jar"
netstat -ano | findstr ":8080" | findstr "LISTENING" >nul
if %errorlevel%==0 (
  echo [OK] 后端服务已在运行
) else (
  if not exist "%JAR%" (
    echo [X] 未找到后端 jar！请先运行 install.bat 构建后端
  ) else (
    echo [..] 启动后端 (Spring Boot) ...
    rem 工作目录设为项目根，保证图片相对路径 ./data/images/ 生效
    set "JAVA_CMD="
    if defined JAVA_HOME (
      if exist "%JAVA_HOME%\bin\java.exe" set "JAVA_CMD=%JAVA_HOME%\bin\java.exe"
    )
    if not defined JAVA_CMD (
      where java >nul 2>nul && set "JAVA_CMD=java"
    )
    if defined JAVA_CMD (
      rem 脚本开头已 cd 到项目根，start 子进程继承该工作目录，图片相对路径自动生效
      start "RuoYi-Backend" /min "%JAVA_CMD%" -jar "%JAR%"
    ) else (
      echo [X] 未找到 JDK！请安装 JDK8+ 或设置 JAVA_HOME
    )
    timeout /t 45 /nobreak >nul
  )
)

rem ---------- 前端 (8090) ----------
netstat -ano | findstr ":8090" | findstr "LISTENING" >nul
if %errorlevel%==0 (
  echo [OK] 前端服务已在运行
) else (
  if not exist "%ROOT%ruoyi\dist\index.html" (
    echo [X] 未找到前端构建产物 dist！请先运行 install.bat
  ) else (
    echo [..] 启动前端 ...
    start "RuoYi-Frontend" /min cmd /c "cd /d ""%ROOT%ruoyi"" && node server.cjs"
    timeout /t 3 /nobreak >nul
  )
)

echo.
echo ============================================
echo   刷题网站:  http://127.0.0.1:8090
echo   账号: admin    密码: admin123
echo   后端 API: http://127.0.0.1:8080
echo ============================================
start http://127.0.0.1:8090
pause
