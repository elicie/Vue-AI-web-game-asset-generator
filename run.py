#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vue + FastAPI 应用启动脚本
"""

import os
import sys
import webbrowser
import time
import threading

def open_browser():
    """延迟打开浏览器"""
    time.sleep(2)
    webbrowser.open('http://localhost:8000')

if __name__ == "__main__":
    print("🚀 启动Vue + FastAPI Nano-Banana AI应用...")
    print("📁 工作目录:", os.getcwd())
    
    # 在新线程中延迟打开浏览器
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # 启动FastAPI服务器
    import uvicorn
    from backend import app
    
    print("🌐 应用将在 http://localhost:8000 启动")
    print("💡 按 Ctrl+C 停止服务器")
    
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)
