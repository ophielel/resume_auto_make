#!/usr/bin/env python3
"""
AI简历智能优化助手启动脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import flask
        import flask_cors
        import flask_sqlalchemy
        import langchain_openai
        import dotenv
        print("✓ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"✗ 缺少依赖: {e}")
        return False

def install_dependencies():
    """安装依赖"""
    print("正在安装依赖...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ 依赖安装完成")
        return True
    except subprocess.CalledProcessError:
        print("✗ 依赖安装失败")
        return False

def check_env_file():
    """检查环境变量文件"""
    env_file = Path(".env")
    if not env_file.exists():
        print("创建 .env 文件...")
        with open(".env", "w", encoding="utf-8") as f:
            f.write("# 阿里云百炼平台API密钥\n")
            f.write("DASHSCOPE_API_KEY=sk-1d878ae8655d43aa9b1b65ec100f6aa7\n")
        print("✓ .env 文件已创建")
    else:
        print("✓ .env 文件已存在")

def create_templates_dir():
    """创建templates目录"""
    templates_dir = Path("templates")
    if not templates_dir.exists():
        templates_dir.mkdir()
        print("✓ templates目录已创建")
    
    # 移动HTML文件到templates目录
    index_html = Path("index.html")
    if index_html.exists():
        import shutil
        shutil.move("index.html", "templates/index.html")
        print("✓ index.html已移动到templates目录")

def main():
    """主函数"""
    print("=== AI简历智能优化助手 ===")
    print("正在检查环境...")
    
    # 检查依赖
    if not check_dependencies():
        print("是否要自动安装依赖? (y/n): ", end="")
        if input().lower() == 'y':
            if not install_dependencies():
                print("请手动安装依赖: pip install -r requirements.txt")
                return
        else:
            print("请手动安装依赖: pip install -r requirements.txt")
            return
    
    # 检查环境变量文件
    check_env_file()
    
    # 创建必要目录
    create_templates_dir()
    
    # 初始化数据库
    init_database()
    
    print("\n启动服务...")
    print("访问地址: http://localhost:5000")
    print("按 Ctrl+C 停止服务")
    print("-" * 50)
    
    # 启动Flask应用
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n服务已停止")
    except Exception as e:
        print(f"启动失败: {e}")

def init_database():
    """初始化数据库"""
    try:
        print("正在初始化数据库...")
        subprocess.check_call([sys.executable, "init_db.py", "init"])
        print("✓ 数据库初始化完成")
    except subprocess.CalledProcessError:
        print("✗ 数据库初始化失败")
    except Exception as e:
        print(f"数据库初始化错误: {e}")

if __name__ == "__main__":
    main()
