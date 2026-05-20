#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vue + FastAPI 应用启动脚本
"""

import os
import webbrowser
import time
import threading


def open_browser(host: str, port: int):
    """延迟打开浏览器"""
    time.sleep(2)
    webbrowser.open(f'http://{host}:{port}')


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    display_host = "localhost" if host == "0.0.0.0" else host

    print("🚀 启动Vue + FastAPI Nano-Banana AI应用...")
    print("📁 工作目录:", os.getcwd())

    # 在新线程中延迟打开浏览器
    browser_thread = threading.Thread(target=open_browser, args=(display_host, port))
    browser_thread.daemon = True
    browser_thread.start()

    # 启动FastAPI服务器
    import uvicorn
    from backend import app

    print(f"🌐 应用将在 http://{display_host}:{port} 启动")
    print("💡 按 Ctrl+C 停止服务器")

    uvicorn.run("backend:app", host=host, port=port, reload=True)
