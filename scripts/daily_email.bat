@echo off
REM Creative Radar — 邮件测试脚本
REM 用法: daily_email.bat

cd /d %~dp0

echo ========================================
echo   创意雷达 · 邮件测试
echo ========================================
echo.

echo [1/4] 检查 Python 环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请安装 Python 3.10+
    pause
    exit /b 1
)
echo [OK] Python 已安装

echo [2/4] 安装依赖...
python -m pip install --user aiosmtplib 2>&1 | findstr "Collecting|Installing|Successfully"
if %errorlevel% neq 0 (
    echo [警告] 依赖安装可能失败，请检查网络
)

echo [3/4] 运行邮件测试...
echo.
python -m backend.app.services.email

echo.
echo [4/4] 测试完成
echo.
echo 注意事项:
echo   1. 确保 .env 文件已配置 SMTP 信息：
echo      SMTP_HOST=your.smtp.server
echo      SMTP_PORT=465
echo      SMTP_USER=your_email@domain.com
echo      SMTP_PASSWORD=xxx
echo      EMAIL_FROM=your_email@domain.com
echo      EMAIL_TO=recipient@domain.com
echo      EMAIL_ENABLED=true
echo.
echo 2. 如果未配置 .env，请先创建：
echo      copy .env.example .env
echo      notepad .env
echo.
pause
