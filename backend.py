#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI后端 - Nano-Banana AI对话应用
支持Vue前端 + WebSocket实时通信
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles  # 单文件应用暂不需要
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Tuple
from contextlib import asynccontextmanager
import json
import uuid
import asyncio
from datetime import datetime
import os
import sys
import tempfile
import threading
from PIL import Image
import io
import requests

# 添加当前目录到Python路径，以便导入gemini_api
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append('..')

try:
    from gemini_api import NanoBananaAPI
except ImportError:
    print("❌ 无法导入gemini_api模块，请确保文件存在")
    sys.exit(1)

# 全局变量（在 lifespan 中初始化）
api_client = None
conversations_db = {}
active_connections: List[WebSocket] = []
_db_lock = threading.Lock()  # Protect conversations_db and file I/O

# Lifespan: replace import-time startup_init() with proper lifecycle
@asynccontextmanager
async def lifespan(application: FastAPI):
    """Run startup tasks inside the async event loop, not at import time."""
    startup_init()
    yield
    # Shutdown: persist any unsaved state
    with _db_lock:
        _save_conversations_unlocked()

app = FastAPI(title="Nano-Banana AI", description="Vue + FastAPI AI对话应用", lifespan=lifespan)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境请限制为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据模型
class Message(BaseModel):
    model_config = {"protected_namespaces": ()}  # 允许model_前缀字段
    
    role: str  # "user" 或 "assistant"
    content: str
    image_url: Optional[str] = None
    input_image_url: Optional[str] = None  # 用户上传的输入图像
    mask_image_url: Optional[str] = None  # 🎯 新增：遮罩图像URL
    model_type: Optional[str] = None  # "generate" 或 "edit"
    timestamp: Optional[str] = None
    image_resolution: Optional[str] = None  # 新增：图像分辨率信息

class Conversation(BaseModel):
    id: str
    title: str
    messages: List[Message]
    created_at: str
    updated_at: str

class ChatRequest(BaseModel):
    model_config = {"protected_namespaces": ()}  # 允许model_前缀字段
    
    message: str
    conversation_id: Optional[str] = None
    input_image_url: Optional[str] = None  # 用户上传的图像URL
    mask_image_url: Optional[str] = None  # 🎯 新增：遮罩图像URL（用于指定编辑区域）
    model_type: str = "generate"  # "generate" 或 "edit"
    aspect_ratio: Optional[str] = "auto"  # 🎯 新增：图像比例

class ChatResponse(BaseModel):
    message: str
    image_url: Optional[str] = None
    conversation_id: str
    is_image: bool = False
    image_resolution: Optional[str] = None  # 新增：图像分辨率信息



# 初始化API客户端
def init_api():
    global api_client
    try:
        # 从config.json读取API密钥
        config_file = "config.json"
        if not os.path.exists(config_file):
            print("❌ 配置文件 config.json 不存在")
            print("💡 请复制 config.example.json 为 config.json 并填写您的API密钥")
            return False
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 优先从环境变量读取API密钥
        api_key = os.getenv('NANO_BANANA_API_KEY')
        
        # 如果环境变量不存在，从配置文件读取
        if not api_key:
            api_key = config.get('api', {}).get('nano_banana_api_key')
        
        if not api_key or api_key == "YOUR_API_KEY_HERE":
            print("❌ API密钥未配置")
            print("💡 请在 config.json 中设置 api.nano_banana_api_key")
            print("💡 或设置环境变量 NANO_BANANA_API_KEY")
            return False
        
        api_client = NanoBananaAPI(api_key=api_key)
        print("✅ Nano-Banana API初始化成功")
        return True
    except Exception as e:
        print(f"❌ API初始化失败: {e}")
        return False

# 加载对话历史
# 辅助函数
def generate_conversation_id():
    """生成唯一的对话ID"""
    return str(uuid.uuid4())[:8]

def get_image_resolution(image_url: str, is_startup: bool = False) -> Optional[str]:
    """获取图像分辨率信息
    
    Args:
        image_url: 图像URL
        is_startup: 是否为启动时调用（启动时会跳过网络图像以提高速度）
    """
    try:
        if image_url.startswith('http'):
            # 启动时跳过网络图像检查
            if is_startup:
                return "网络图像"
                
            # 网络图片 - 添加更好的网络配置
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            # 设置合理的超时时间
            response = requests.get(
                image_url, 
                timeout=10,  # API调用时使用较长超时
                headers=headers,
                proxies={"http": None, "https": None}  # 禁用代理
            )
            response.raise_for_status()
            image = Image.open(io.BytesIO(response.content))
        else:
            # 本地图片
            local_path = f".{image_url}" if image_url.startswith('/') else image_url
            if os.path.exists(local_path):
                image = Image.open(local_path)
            else:
                return None
        
        width, height = image.size
        return f"{width}×{height}"
    except requests.exceptions.RequestException as e:
        print(f"⚠️ 网络图像分辨率获取失败（跳过）: {type(e).__name__}")
        return "网络图像"  # 返回默认值而不是None
    except Exception as e:
        print(f"⚠️ 获取图像分辨率失败: {e}")
        return None

def load_conversations():
    global conversations_db
    try:
        history_file = "conversation_history.json"
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 转换格式
            for conv_id, conv_data in data.items():
                messages = []
                history = conv_data.get('history', [])
                
                for i in range(0, len(history), 2):
                    if i < len(history):
                        # 用户消息
                        user_msg = history[i]
                        if isinstance(user_msg, str):
                            # 旧格式：纯字符串
                            messages.append(Message(
                                role="user",
                                content=user_msg,
                                timestamp=datetime.now().isoformat()
                            ))
                        elif isinstance(user_msg, dict):
                            # 新格式：包含图片信息的字典
                            messages.append(Message(
                                role="user",
                                content=user_msg.get("content", ""),
                                input_image_url=user_msg.get("input_image_url"),
                                timestamp=datetime.now().isoformat()
                            ))
                    
                    if i + 1 < len(history):
                        # AI回复
                        ai_msg = history[i + 1]
                        if isinstance(ai_msg, (tuple, list)) and len(ai_msg) == 2:
                            # 图像回复 (url, caption)
                            # 启动时快速加载，包括网络图像
                            resolution = get_image_resolution(ai_msg[0], is_startup=True)
                            messages.append(Message(
                                role="assistant",
                                content=ai_msg[1],
                                image_url=ai_msg[0],
                                image_resolution=resolution,
                                timestamp=datetime.now().isoformat()
                            ))
                        elif isinstance(ai_msg, str):
                            # 文本回复
                            messages.append(Message(
                                role="assistant",
                                content=ai_msg,
                                timestamp=datetime.now().isoformat()
                            ))
                
                # 处理时间戳格式
                timestamp = conv_data.get('timestamp', datetime.now().isoformat())
                if isinstance(timestamp, (int, float)):
                    timestamp = datetime.fromtimestamp(timestamp).isoformat()
                elif not isinstance(timestamp, str):
                    timestamp = datetime.now().isoformat()
                
                conversations_db[conv_id] = Conversation(
                    id=conv_id,
                    title=conv_data.get('title', f'对话 {conv_id[:8]}'),
                    messages=messages,
                    created_at=timestamp,
                    updated_at=timestamp
                )
                
        print(f"✅ 加载了 {len(conversations_db)} 条对话历史")
    except Exception as e:
        print(f"❌ 加载对话历史失败: {e}")
        conversations_db = {}

# 保存对话历史（无锁版本，调用者须持有 _db_lock）
def _save_conversations_unlocked():
    """Atomic write: write to temp file then rename. Caller must hold _db_lock."""
    try:
        history_file = "conversation_history.json"
        data = {}
        
        for conv_id, conversation in conversations_db.items():
            history = []
            for msg in conversation.messages:
                if msg.role == "user":
                    user_data = {"content": msg.content, "role": "user"}
                    if hasattr(msg, 'input_image_url') and msg.input_image_url:
                        user_data["input_image_url"] = msg.input_image_url
                    history.append(user_data)
                elif msg.role == "assistant":
                    if msg.image_url:
                        history.append((msg.image_url, msg.content))
                    else:
                        history.append(msg.content)
            
            data[conv_id] = {
                'title': conversation.title,
                'history': history,
                'timestamp': conversation.created_at
            }
        
        # Atomic write: temp file + rename
        dir_name = os.path.dirname(os.path.abspath(history_file))
        fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix='.json')
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, history_file)  # atomic on POSIX
        except BaseException:
            # Clean up temp file on failure
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise
            
        print(f"✅ 保存了 {len(data)} 条对话历史")
    except Exception as e:
        print(f"❌ 保存对话历史失败: {e}")


def save_conversations():
    """Thread-safe wrapper that acquires the lock before writing."""
    with _db_lock:
        _save_conversations_unlocked()

# WebSocket连接管理
async def connect_websocket(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    print(f"🔌 WebSocket连接建立，当前连接数: {len(active_connections)}")

def disconnect_websocket(websocket: WebSocket):
    if websocket in active_connections:
        active_connections.remove(websocket)
    print(f"🔌 WebSocket连接断开，当前连接数: {len(active_connections)}")

async def broadcast_message(message: dict):
    """广播消息到所有连接的客户端"""
    for connection in active_connections.copy():
        try:
            await connection.send_text(json.dumps(message, ensure_ascii=False))
        except:
            disconnect_websocket(connection)

# 检测是否为图像生成请求
def is_image_generation_request(text: str) -> bool:
    image_keywords = [
        '生成', '画', '创建', '制作', '设计', '图像', '图片', '照片',
        'generate', 'create', 'draw', 'make'
    ]
    return any(keyword in text.lower() for keyword in image_keywords)

# 图像处理现在使用KIE.ai文件上传服务

# API路由
@app.get("/")
async def serve_frontend():
    """提供前端页面"""
    return FileResponse("index.html")

@app.get("/api/conversations")
async def get_conversations():
    """获取所有对话列表"""
    conversations_list = []
    for conv in conversations_db.values():
        conversations_list.append({
            "id": conv.id,
            "title": conv.title,
            "message_count": len(conv.messages),
            "created_at": conv.created_at,
            "updated_at": conv.updated_at
        })
    
    # 按创建时间排序（最新的在前）
    conversations_list.sort(key=lambda x: x['created_at'], reverse=True)
    return conversations_list

@app.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """获取特定对话的详细信息"""
    if conversation_id not in conversations_db:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    return conversations_db[conversation_id]

@app.post("/api/conversations")
async def create_conversation():
    """创建新对话"""
    conversation_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().isoformat()
    
    new_conversation = Conversation(
        id=conversation_id,
        title=f"新对话 {conversation_id}",
        messages=[],
        created_at=timestamp,
        updated_at=timestamp
    )
    
    conversations_db[conversation_id] = new_conversation
    save_conversations()
    
    # 广播新对话创建事件
    await broadcast_message({
        "type": "conversation_created",
        "conversation": {
            "id": new_conversation.id,
            "title": new_conversation.title,
            "message_count": 0,
            "created_at": new_conversation.created_at,
            "updated_at": new_conversation.updated_at
        }
    })
    
    return {"conversation_id": conversation_id}

@app.delete("/api/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """删除对话"""
    if conversation_id not in conversations_db:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    del conversations_db[conversation_id]
    save_conversations()
    
    # 广播对话删除事件
    await broadcast_message({
        "type": "conversation_deleted",
        "conversation_id": conversation_id
    })
    
    return {"success": True}

@app.post("/api/clean-image")
async def clean_image(request: dict):
    """清理图片，返回干净的Base64数据以避免Canvas污染"""
    try:
        image_url = request.get('imageUrl')
        if not image_url:
            raise HTTPException(status_code=400, detail="缺少图片URL")
        
        print(f"🖼️ 处理图片清理请求: {image_url}")
        
        # 🔧 优先处理本地文件，避免循环请求
        if image_url.startswith('/uploads/') or (image_url.startswith('http://localhost') and '/uploads/' in image_url):
            # 提取文件路径
            if image_url.startswith('/uploads/'):
                local_path = f".{image_url}"
            else:
                # 从localhost URL中提取文件路径
                file_path = image_url.split('/uploads/')[-1]
                local_path = f"./uploads/{file_path}"
            
            if os.path.exists(local_path):
                # 读取本地文件并转换为Base64
                with open(local_path, 'rb') as f:
                    image_data = f.read()
                    
                    # 检查原图尺寸
                    from PIL import Image
                    import io
                    img = Image.open(io.BytesIO(image_data))
                    print(f"📐 本地图片原始尺寸: {img.width} x {img.height}")
                    
                    import base64
                    base64_data = base64.b64encode(image_data).decode('utf-8')
                    # 添加MIME类型前缀
                    clean_base64 = f"data:image/png;base64,{base64_data}"
                    
                print(f"✅ 本地图片转换成功，大小: {len(clean_base64)} 字符")
                return {"success": True, "imageData": clean_base64}
            else:
                print(f"❌ 本地文件不存在: {local_path}")
                return {"success": False, "error": "本地文件不存在"}
        
        # 如果是网络URL，下载并转换
        elif image_url.startswith(('http://', 'https://')):
            import requests
            response = requests.get(image_url, timeout=10)
            if response.status_code == 200:
                # 检查下载图片的尺寸
                from PIL import Image
                import io
                img = Image.open(io.BytesIO(response.content))
                print(f"📐 网络图片下载尺寸: {img.width} x {img.height}")
                
                import base64
                base64_data = base64.b64encode(response.content).decode('utf-8')
                # 检测MIME类型
                content_type = response.headers.get('content-type', 'image/png')
                clean_base64 = f"data:{content_type};base64,{base64_data}"
                
                print(f"✅ 网络图片下载转换成功，大小: {len(clean_base64)} 字符")
                return {"success": True, "imageData": clean_base64}
            else:
                print(f"❌ 网络图片下载失败，状态码: {response.status_code}")
                return {"success": False, "error": f"图片下载失败: {response.status_code}"}
        
        else:
            print(f"❌ 不支持的图片URL格式: {image_url}")
            return {"success": False, "error": "不支持的图片URL格式"}
            
    except Exception as e:
        print(f"❌ 图片清理处理异常: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """上传图像文件"""
    import shutil
    
    # 检查文件类型
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="只支持图像文件")
    
    # 检查文件大小 (限制为10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    file_size = 0
    
    # 创建上传目录
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    # 生成唯一文件名
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
    unique_filename = f"upload_{uuid.uuid4().hex[:8]}.{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    try:
        # 保存文件
        with open(file_path, "wb") as buffer:
            while True:
                chunk = await file.read(1024)
                if not chunk:
                    break
                file_size += len(chunk)
                if file_size > max_size:
                    # 删除已保存的部分文件
                    os.remove(file_path)
                    raise HTTPException(status_code=413, detail="文件大小超过10MB限制")
                buffer.write(chunk)
        
        # 返回文件URL (这里简化处理，实际项目中可能需要配置静态文件服务)
        file_url = f"/uploads/{unique_filename}"
        
        print(f"📁 文件上传成功: {file.filename} -> {file_path} ({file_size} bytes)")
        
        return {
            "success": True,
            "file_url": file_url,
            "original_filename": file.filename,
            "file_size": file_size
        }
        
    except Exception as e:
        # 清理失败的上传文件
        if os.path.exists(file_path):
            os.remove(file_path)
        print(f"❌ 文件上传失败: {e}")
        raise HTTPException(status_code=500, detail="文件上传失败")

@app.get("/uploads/{filename}")
async def get_uploaded_file(filename: str):
    """获取上传的文件"""
    # Sanitize filename to prevent path traversal
    safe_name = os.path.basename(filename)
    if safe_name != filename:
        raise HTTPException(status_code=400, detail="잘못된 파일명입니다")
    file_path = os.path.join("uploads", safe_name)
    # Resolve to absolute path and verify it stays within uploads/
    uploads_dir = os.path.abspath("uploads")
    resolved_path = os.path.abspath(file_path)
    if not resolved_path.startswith(uploads_dir + os.sep) and resolved_path != uploads_dir:
        raise HTTPException(status_code=400, detail="잘못된 파일 경로입니다")
    if not os.path.exists(resolved_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    return FileResponse(resolved_path)

@app.get("/api/proxy-image")
async def proxy_image(url: str):
    """代理外部图片以避免CORS问题"""
    try:
        print(f"🔄 代理图片请求: {url}")
        
        # 验证URL格式
        if not url.startswith(('http://', 'https://')):
            raise HTTPException(status_code=400, detail="无效的图片URL")
        
        # 请求外部图片
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail=f"图片请求失败: {response.status_code}")
        
        # 检查内容类型
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="URL不是图片资源")
        
        print(f"✅ 图片代理成功，大小: {len(response.content)} bytes")
        
        # 返回图片内容
        from fastapi.responses import Response
        return Response(
            content=response.content,
            media_type=content_type,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET",
                "Access-Control-Allow-Headers": "*"
            }
        )
        
    except requests.RequestException as e:
        print(f"❌ 图片代理请求失败: {e}")
        raise HTTPException(status_code=500, detail=f"图片代理失败: {str(e)}")
    except Exception as e:
        print(f"❌ 图片代理处理失败: {e}")
        raise HTTPException(status_code=500, detail=f"图片代理处理失败: {str(e)}")

@app.post("/api/merge-canvas")
async def merge_canvas(request: dict):
    """服务器端Canvas合成，解决前端Canvas污染问题"""
    try:
        print("🎨 服务器端Canvas合成请求")
        
        width = request.get('width', 600)
        height = request.get('height', 400)
        background_image_url = request.get('backgroundImageUrl')
        paths = request.get('paths', [])
        
        print(f"📐 Canvas尺寸: {width}x{height}")
        print(f"🖼️ 背景图像: {background_image_url}")
        print(f"🎨 绘制路径数量: {len(paths)}")
        
        # 使用PIL创建合成图像
        from PIL import Image, ImageDraw
        import requests
        import io
        import base64
        
        # 创建基础图像
        if background_image_url:
            # 🔧 智能处理背景图像加载
            if background_image_url.startswith('http://localhost') or background_image_url.startswith('http://127.0.0.1'):
                # 本地服务器URL - 转换为文件路径
                if '/uploads/' in background_image_url:
                    file_path = background_image_url.split('/uploads/')[-1]
                    local_path = f"./uploads/{file_path}"
                    print(f"🔄 本地服务器URL转换为文件路径: {local_path}")
                    background_img = Image.open(local_path)
                else:
                    print(f"⚠️ 无法解析本地URL: {background_image_url}")
                    background_img = Image.new('RGB', (width, height), 'white')
            elif background_image_url.startswith('http'):
                # 外部URL - 下载
                print(f"🌐 下载外部图像: {background_image_url}")
                response = requests.get(background_image_url, timeout=30)
                background_img = Image.open(io.BytesIO(response.content))
            else:
                # 本地文件路径
                local_path = f".{background_image_url}" if background_image_url.startswith('/') else background_image_url
                print(f"📁 加载本地文件: {local_path}")
                background_img = Image.open(local_path)
            
            # 调整尺寸
            background_img = background_img.resize((width, height), Image.Resampling.LANCZOS)
        else:
            # 创建白色背景
            background_img = Image.new('RGB', (width, height), 'white')
        
        # 创建绘图对象
        draw = ImageDraw.Draw(background_img)
        
        # 绘制所有路径
        for path in paths:
            points = path.get('points', [])
            if len(points) < 2:
                continue
                
            mode = path.get('mode', 'brush')
            color = path.get('color', '#000000')
            size = path.get('size', 5)
            
            # 🔧 确保size是整数类型
            try:
                size = int(float(size))  # 支持字符串和浮点数转换
                if size < 1:
                    size = 1
                elif size > 100:
                    size = 100
            except (ValueError, TypeError):
                size = 5  # 默认值
            
            if mode == 'eraser':
                continue  # PIL中橡皮擦需要特殊处理，暂时跳过
            
            # 将点转换为PIL格式
            pil_points = []
            for point in points:
                try:
                    x = int(float(point['x']))
                    y = int(float(point['y']))
                    pil_points.append((x, y))
                except (ValueError, TypeError, KeyError):
                    continue  # 跳过无效的点
            
            # 绘制线条
            if len(pil_points) > 1:
                for i in range(len(pil_points) - 1):
                    draw.line([pil_points[i], pil_points[i + 1]], fill=color, width=size)
        
        # 转换为Base64
        output_buffer = io.BytesIO()
        background_img.save(output_buffer, format='PNG')
        output_buffer.seek(0)
        
        base64_data = base64.b64encode(output_buffer.getvalue()).decode('utf-8')
        result_data = f"data:image/png;base64,{base64_data}"
        
        print("✅ 服务器端Canvas合成完成")
        
        return {
            "success": True,
            "imageData": result_data
        }
        
    except Exception as e:
        print(f"❌ 服务器端Canvas合成失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/download-image")
async def download_image_proxy(image_url: str):
    """代理下载外部图像，解决跨域问题"""
    try:
        from fastapi.responses import StreamingResponse
        
        # 获取图像数据
        response = requests.get(image_url, timeout=30, stream=True)
        response.raise_for_status()
        
        # 获取内容类型
        content_type = response.headers.get('content-type', 'image/png')
        
        # 从URL提取文件名
        filename = image_url.split('/')[-1]
        if not filename or '.' not in filename:
            filename = 'nano-banana-image.png'
        
        # 创建流式响应
        def generate():
            for chunk in response.iter_content(chunk_size=8192):
                yield chunk
        
        return StreamingResponse(
            generate(),
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Access-Control-Allow-Origin": "*"
            }
        )
        
    except Exception as e:
        print(f"❌ 代理下载失败: {e}")
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """处理聊天请求"""
    try:
        # 确定对话ID
        conversation_id = request.conversation_id
        if not conversation_id or conversation_id not in conversations_db:
            # 创建新对话
            conversation_id = str(uuid.uuid4())[:8]
            timestamp = datetime.now().isoformat()
            conversations_db[conversation_id] = Conversation(
                id=conversation_id,
                title=f"新对话 {conversation_id}",
                messages=[],
                created_at=timestamp,
                updated_at=timestamp
            )
        
        conversation = conversations_db[conversation_id]
        
        # 添加用户消息
        user_message = Message(
            role="user",
            content=request.message,
            input_image_url=request.input_image_url,
            mask_image_url=request.mask_image_url,  # 🎯 新增遮罩信息
            model_type=request.model_type,
            timestamp=datetime.now().isoformat()
        )
        conversation.messages.append(user_message)
        
        # 处理AI回复
        if request.model_type == "edit" and request.input_image_url:
            # 图像编辑模式
            print(f"✏️ 处理图像编辑请求: {request.message}")
            print(f"📥 输入图像: {request.input_image_url}")
            
            # 🎯 检查是否有遮罩数据
            if request.mask_image_url:
                print(f"🎯 检测到遮罩数据，将进行局部编辑")
                print(f"🎯 遮罩图像: {request.mask_image_url[:100]}..." if len(request.mask_image_url) > 100 else request.mask_image_url)
            else:
                print(f"🎯 无遮罩数据，将进行全图编辑")
            
            # 智能处理输入图像
            input_image_data = request.input_image_url
            
            if input_image_data.startswith('/uploads/'):
                # 本地上传文件 - 上传到KIE.ai公网服务
                local_file_path = f".{input_image_data}"  # 转换为相对路径 ./uploads/xxx.png
                print(f"🔄 处理本地上传文件: {local_file_path}")
                
                # 使用KIE.ai文件上传服务
                public_url = api_client.upload_file_to_kie(local_file_path)
                if public_url:
                    input_image_data = public_url
                    print(f"✅ 成功上传图像到公网: {public_url}")
                else:
                    print(f"❌ 上传图像到公网失败")
                    input_image_data = None
                    
            elif input_image_data.startswith(('http://', 'https://')):
                # 网络图像URL - 检查是否为本地服务器
                if ('localhost:8000' in input_image_data or '127.0.0.1' in input_image_data) and '/uploads/' in input_image_data:
                    # 本地服务器URL - 需要上传到公网
                    file_path = input_image_data.split('/uploads/')[-1]
                    local_file_path = f"./uploads/{file_path}"
                    print(f"🔄 检测到本地服务器URL，上传到公网: {local_file_path}")
                    
                    # 使用KIE.ai文件上传服务
                    public_url = api_client.upload_file_to_kie(local_file_path)
                    if public_url:
                        input_image_data = public_url
                        print(f"✅ 成功上传图像到公网: {public_url}")
                    else:
                        print(f"❌ 上传图像到公网失败")
                        input_image_data = None
                else:
                    # 真正的网络图像URL - 直接使用
                    print(f"🌐 使用网络图像URL: {input_image_data}")
                
            elif input_image_data.startswith('data:image/'):
                # Base64图像数据 - 保存为临时文件并上传
                print(f"🎨 处理Base64图像数据")
                try:
                    import base64
                    import tempfile
                    from PIL import Image
                    import io
                    
                    # 解析Base64数据
                    header, data = input_image_data.split(',', 1)
                    image_data = base64.b64decode(data)
                    
                    # 检查图片尺寸
                    img = Image.open(io.BytesIO(image_data))
                    print(f"📐 接收到的Base64图片尺寸: {img.width} x {img.height}")
                    
                    # 创建临时文件
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                        temp_file.write(image_data)
                        temp_path = temp_file.name
                    
                    print(f"📝 Base64图像已保存到临时文件: {temp_path}")
                    
                    # 上传到KIE.ai公网服务
                    public_url = api_client.upload_file_to_kie(temp_path)
                    if public_url:
                        input_image_data = public_url
                        print(f"✅ 成功上传Base64图像到公网: {public_url}")
                    else:
                        print(f"❌ 上传Base64图像到公网失败")
                        input_image_data = None
                    
                    # 清理临时文件
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
                        
                except Exception as e:
                    print(f"❌ 处理Base64图像数据失败: {e}")
                    input_image_data = None
                
            else:
                print(f"⚠️ 未知图像格式: {input_image_data[:100]}...")
                # 尝试作为本地文件路径处理
                if os.path.exists(input_image_data):
                    # 如果是本地文件，上传到KIE.ai
                    public_url = api_client.upload_file_to_kie(input_image_data)
                    if public_url:
                        input_image_data = public_url
                        print(f"✅ 将本地文件上传到公网: {public_url}")
                    else:
                        print(f"❌ 上传本地文件到公网失败")
                        input_image_data = None
                else:
                    print(f"❌ 无法处理图像: 文件不存在或格式不支持")
                    input_image_data = None
            
            # 如果图像处理失败，返回错误
            if input_image_data is None:
                error_msg = "❌ 图像处理失败，请检查图像格式或重新上传"
                ai_message = Message(
                    role="assistant",
                    content=error_msg,
                    model_type="edit",
                    timestamp=datetime.now().isoformat()
                )
                conversation.messages.append(ai_message)
                
                response = ChatResponse(
                    message=error_msg,
                    conversation_id=conversation_id,
                    is_image=False
                )
            else:
                # 🎯 处理遮罩数据
                mask_data = None
                if request.mask_image_url:
                    print(f"🎯 处理遮罩图像: {request.mask_image_url[:100]}...")
                    
                    # 上传遮罩图像到公网（如果需要）
                    if request.mask_image_url.startswith('data:image/'):
                        # Base64遮罩数据
                        try:
                            import base64
                            import tempfile
                            
                            # 解析Base64数据
                            header, data = request.mask_image_url.split(',', 1)
                            mask_image_data = base64.b64decode(data)
                            
                            # 创建临时文件
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                                temp_file.write(mask_image_data)
                                temp_path = temp_file.name
                            
                            print(f"📝 遮罩Base64数据已保存到临时文件: {temp_path}")
                            
                            # 上传到KIE.ai公网服务
                            public_mask_url = api_client.upload_file_to_kie(temp_path)
                            if public_mask_url:
                                mask_data = public_mask_url
                                print(f"✅ 成功上传遮罩到公网: {public_mask_url}")
                            else:
                                print(f"❌ 上传遮罩到公网失败")
                            
                            # 清理临时文件
                            try:
                                os.unlink(temp_path)
                            except:
                                pass
                                
                        except Exception as e:
                            print(f"❌ 处理遮罩Base64数据失败: {e}")
                    else:
                        mask_data = request.mask_image_url
                
                image_url = api_client.edit_image_with_nano_banana(
                    request.message, 
                    input_image_data, 
                    mask_data,
                    aspect_ratio=request.aspect_ratio
                )
                
                if image_url and isinstance(image_url, str):
                    # 检查返回值是否为错误信息
                    if image_url.startswith("ERROR:"):
                        # API返回了具体错误信息
                        error_msg = f"❌ 图像编辑失败: {image_url[6:]}"  # 去掉"ERROR:"前缀
                        ai_message = Message(
                            role="assistant",
                            content=error_msg,
                            model_type="edit",
                            timestamp=datetime.now().isoformat()
                        )
                        conversation.messages.append(ai_message)
                        
                        response = ChatResponse(
                            message=error_msg,
                            conversation_id=conversation_id,
                            is_image=False
                        )
                    else:
                        # 成功返回图像URL
                        ai_response = ""  # 不显示成功提示文本
                        
                        # 获取图像分辨率
                        resolution = get_image_resolution(image_url)
                        
                        ai_message = Message(
                            role="assistant",
                            content=ai_response,
                            image_url=image_url,
                            model_type="edit",
                            timestamp=datetime.now().isoformat(),
                            image_resolution=resolution
                        )
                        conversation.messages.append(ai_message)
                        
                        response = ChatResponse(
                            message=ai_response,
                            image_url=image_url,
                            conversation_id=conversation_id,
                            is_image=True,
                            image_resolution=resolution
                        )
                else:
                    error_msg = "❌ 图像编辑失败，可能是网络问题或服务超时，请稍后重试"
                    ai_message = Message(
                        role="assistant",
                        content=error_msg,
                        model_type="edit",
                        timestamp=datetime.now().isoformat()
                    )
                    conversation.messages.append(ai_message)
                    
                    response = ChatResponse(
                        message=error_msg,
                        conversation_id=conversation_id,
                        is_image=False
                    )
                
        elif is_image_generation_request(request.message):
            # 图像生成模式
            print(f"🎨 处理图像生成请求: {request.message}")
            image_url = api_client.generate_image_with_nano_banana(
                request.message, 
                num_images=1,
                aspect_ratio=request.aspect_ratio
            )
            
            if isinstance(image_url, list) and len(image_url) > 0:
                image_url = image_url[0]
            
            if image_url and isinstance(image_url, str):
                ai_response = ""  # 不显示成功提示文本
                
                # 获取图像分辨率
                resolution = get_image_resolution(image_url)
                
                ai_message = Message(
                    role="assistant",
                    content=ai_response,
                    image_url=image_url,
                    model_type="generate",
                    timestamp=datetime.now().isoformat(),
                    image_resolution=resolution
                )
                conversation.messages.append(ai_message)
                
                response = ChatResponse(
                    message=ai_response,
                    image_url=image_url,
                    conversation_id=conversation_id,
                    is_image=True,
                    image_resolution=resolution
                )
            else:
                error_msg = "❌ 图像生成失败，可能是网络问题或服务超时，请稍后重试"
                ai_message = Message(
                    role="assistant",
                    content=error_msg,
                    model_type="generate",
                    timestamp=datetime.now().isoformat()
                )
                conversation.messages.append(ai_message)
                
                response = ChatResponse(
                    message=error_msg,
                    conversation_id=conversation_id,
                    is_image=False
                )
        else:
            # 文本对话
            print(f"💬 处理文本对话: {request.message}")
            ai_response = api_client.generate_content(request.message)
            
            ai_message = Message(
                role="assistant",
                content=ai_response,
                timestamp=datetime.now().isoformat()
            )
            conversation.messages.append(ai_message)
            
            response = ChatResponse(
                message=ai_response,
                conversation_id=conversation_id,
                is_image=False
            )
        
        # 更新对话标题（如果是第一条消息）
        if len(conversation.messages) == 2:  # 用户消息 + AI回复
            conversation.title = request.message[:20] + "..." if len(request.message) > 20 else request.message
        
        conversation.updated_at = datetime.now().isoformat()
        save_conversations()
        
        return response
        
    except Exception as e:
        print(f"❌ 聊天处理错误: {e}")
        raise HTTPException(status_code=500, detail=f"处理请求时发生错误: {str(e)}")

# WebSocket端点
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await connect_websocket(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # 这里可以处理WebSocket消息
            message = json.loads(data)
            print(f"📨 收到WebSocket消息: {message}")
            
    except WebSocketDisconnect:
        disconnect_websocket(websocket)

# 启动时初始化
def startup_init():
    print("🚀 启动Nano-Banana Vue + FastAPI应用...")
    if not init_api():
        print("❌ API初始化失败，应用可能无法正常工作")
    load_conversations()
    print("✅ 应用启动完成！")

# 静态文件（Vue构建后的文件）
# app.mount("/static", StaticFiles(directory="dist"), name="static")  # 单文件应用暂不需要

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
