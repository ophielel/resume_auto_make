@echo off
echo ========================================
echo    AI简历智能优化助手
echo ========================================
echo.

echo 正在检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

echo 正在检查依赖...
python -c "import flask, flask_cors, langchain_openai" >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo 错误: 依赖安装失败
        pause
        exit /b 1
    )
)

echo.
echo 启动服务...
echo 访问地址: http://localhost:5000
echo 按 Ctrl+C 停止服务
echo.

python app.py

pause
