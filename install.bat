@echo off
setlocal
title 花花公考刷题 - 一键安装
echo ============================================
echo   花花公考刷题 - 一键安装脚本
echo   本脚本将安装前端依赖并构建前后端
echo ============================================
echo.

rem 脚本所在目录（项目根）
set "ROOT=%~dp0"
cd /d "%ROOT%"

rem ---------- 检查 Node.js ----------
where node >nul 2>nul
if %errorlevel%==0 (
  for /f "delims=" %%v in ('node -v') do set "NODE_V=%%v"
  echo [OK] Node.js: %NODE_V%
) else (
  echo [X] 未检测到 Node.js，请先安装 Node.js 18+：https://nodejs.org/
  echo     安装后重新运行本脚本
  pause
  exit /b 1
)

rem ---------- 安装前端依赖 ----------
echo.
echo [1/4] 安装前端依赖 (npm install) ...
cd /d "%ROOT%ruoyi"
call npm install
if %errorlevel% neq 0 (
  echo [X] npm install 失败，请检查网络后重试
  pause
  exit /b 1
)
echo [OK] 前端依赖安装完成

rem ---------- 构建前端 ----------
echo.
echo [2/4] 构建前端 (npm run build:prod) ...
call npm run build:prod
if %errorlevel% neq 0 (
  echo [X] 前端构建失败
  pause
  exit /b 1
)
echo [OK] 前端构建完成 (dist/)

rem ---------- 检查 JDK ----------
echo.
set "JAVA_OK="
if defined JAVA_HOME (
  if exist "%JAVA_HOME%\bin\java.exe" set "JAVA_OK=1"
)
if not defined JAVA_OK (
  where java >nul 2>nul && set "JAVA_OK=1"
)

if defined JAVA_OK goto build_ok
echo [..] 未检测到 JDK，跳过后端构建
echo      请安装 JDK8+ 后执行: cd ruoyi-backend ^&^& mvn package -DskipTests
goto build_done
:build_ok
echo [3/4] 构建后端 (mvn package) ...
cd /d "%ROOT%ruoyi-backend"
call mvn package -DskipTests -q
if errorlevel 1 goto build_fail
echo [OK] 后端构建完成 (ruoyi-admin.jar)
goto build_done
:build_fail
echo [X] 后端构建失败（请确认已安装 JDK8+ 与 Maven）
pause
exit /b 1
:build_done

rem ---------- 数据库说明 ----------
echo.
echo [4/4] 数据库初始化说明
echo ------------------------------------------------------------
echo   需要导入以下 SQL（按顺序，在 MySQL 中执行）:
echo     1. ruoyi-backend\sql\ry_20240629.sql        (若依基础表+菜单)
echo     2. data\sql\exam_schema.sql                 (刷题表结构+菜单)
echo     3. data\sql\shenlun_schema.sql              (申论表结构+菜单)
echo     4. data\sql\exam_data_full.sql              (行测题库 167套 19621题)
echo     5. data\sql\shenlun_data_full.sql           (申论题库 700套)
echo ------------------------------------------------------------
echo   说明: 数据库名为 ruoyi，账号 root / 密码 123456
echo         图片目录为 data\images\（若缺失，题目图片不显示，不影响文字）
echo.
echo ============================================
echo   安装完成！
echo   运行 start-all.bat 即可启动项目
echo ============================================
pause
