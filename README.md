# 🍌 Vue-AI-web-game-asset-generator

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com)
[![Vue 3](https://img.shields.io/badge/Vue-3.x-4FC08D.svg)](https://vuejs.org/)

**一个强大的AI驱动图像生成与编辑工具，基于Google Nano-Banana模型**

[English](#english) | [中文](#chinese)

<img src="https://via.placeholder.com/800x400/4A90E2/FFFFFF?text=Nano-Banana+AI+Image+Studio" alt="Nano-Banana AI" />

</div>

---

## <a id="chinese"></a>🇨🇳 中文文档

### ✨ 核心特性

- 🎨 **AI图像生成** - 使用自然语言描述，AI即可生成精美图像
- ✏️ **智能图像编辑** - 上传图片并描述修改需求，AI自动编辑
- 🎯 **局部编辑（即将推出）** - 使用画笔精确标记编辑区域
- 📐 **多种图像比例** - 支持1:1、16:9、9:16、4:3、3:4等多种比例
- 💬 **对话管理** - 自动保存所有对话历史和生成的图像
- 📱 **响应式设计** - 完美适配桌面端和移动端
- 🌐 **现代化界面** - 基于Vue 3的流畅用户体验

### 🚀 未来规划

我们正在积极开发以下功能，让AI图像处理更加强大：

- 🔪 **一键抠图** - 智能识别主体，自动去除背景
- 🔍 **图像超分辨率** - AI图像放大，保持细节清晰
- 🎬 **视频生成** - 文本到视频，图像到视频
- 🎭 **风格迁移** - 将任意图像转换为艺术风格
- 🖼️ **批量处理** - 同时处理多张图像
- 🎨 **高级画笔工具** - 更精细的局部编辑控制

### 📦 快速开始

#### 1. 环境要求

- Python 3.8 或更高版本
- pip 包管理器

#### 2. 安装步骤

```bash
# 克隆仓库
git clone https://github.com/yourusername/nano-banana-ai.git
cd nano-banana-ai

# 安装依赖
pip install -r requirements.txt

# 配置API密钥
cp config.example.json config.json
# 编辑 config.json，填入您的 Nano-Banana API 密钥
```

#### 3. 获取API密钥

1. 访问 [KIE.ai](https://kie.ai/) 注册账户
2. 在控制台创建API密钥
3. 将API密钥填入 `config.json` 中的 `api.nano_banana_api_key` 字段

#### 4. 启动应用

```bash
# 方式1：使用启动脚本
python run.py

# 方式2：直接启动后端
python backend.py
```

#### 5. 访问应用

打开浏览器访问：
- **Web界面**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **交互式文档**: http://localhost:8000/redoc

### 🛠️ 技术栈

#### 前端
- **Vue 3** - 渐进式JavaScript框架
- **Axios** - HTTP客户端
- **HTML5 Canvas** - 图像绘制和编辑

#### 后端
- **FastAPI** - 现代化Python Web框架
- **Uvicorn** - 高性能ASGI服务器
- **Pydantic** - 数据验证
- **Pillow** - 图像处理库

#### AI服务
- **Google Nano-Banana** - 图像生成与编辑
- **KIE.ai Platform** - AI模型托管平台

### 📁 项目结构

```
nano-banana-ai/
├── backend.py              # FastAPI后端主程序
├── gemini_api.py           # Nano-Banana API封装
├── index.html              # Vue 3前端界面
├── run.py                  # 应用启动脚本
├── config.json             # 配置文件（需自行创建）
├── config.example.json     # 配置文件模板
├── requirements.txt        # Python依赖包列表
├── .gitignore             # Git忽略文件配置
├── README.md              # 项目说明文档
└── uploads/               # 上传图像存储目录（自动创建）
```

### 🎯 使用指南

#### 图像生成
1. 在输入框中描述您想要的图像，例如："一只可爱的橘猫在草地上玩耍"
2. 选择图像比例（可选）
3. 点击发送，等待AI生成图像

#### 图像编辑
1. 点击"上传图片"按钮，选择要编辑的图像
2. 描述您想要的修改，例如："把天空变成日落"
3. 点击发送，AI将根据您的描述编辑图像

#### 局部编辑（实验性功能）
1. 上传图像后，点击"画笔"工具
2. 在图像上标记需要编辑的区域
3. 描述修改内容，AI将只修改标记区域

### 🔧 配置说明

`config.json` 配置文件说明：

```json
{
  "api": {
    "nano_banana_api_key": "YOUR_API_KEY_HERE",  // 必填：您的API密钥
    "comment": "请在 https://kie.ai/ 申请API密钥"
  },
  "server": {
    "host": "127.0.0.1",      // 服务器地址
    "port": 7864,             // 服务器端口
    "share": false            // 是否生成公网链接
  },
  "generation": {
    "default_width": 512,     // 默认图像宽度
    "default_height": 512,    // 默认图像高度
    "max_width": 1024,        // 最大图像宽度
    "max_height": 1024        // 最大图像高度
  }
}
```

### 🌍 环境变量（可选）

您也可以使用环境变量设置API密钥：

```bash
# Linux/Mac
export NANO_BANANA_API_KEY="your_api_key_here"

# Windows (PowerShell)
$env:NANO_BANANA_API_KEY="your_api_key_here"

# Windows (CMD)
set NANO_BANANA_API_KEY=your_api_key_here
```

### 📝 API端点

主要API端点：

- `GET /` - Web界面
- `GET /api/conversations` - 获取对话列表
- `POST /api/conversations` - 创建新对话
- `DELETE /api/conversations/{id}` - 删除对话
- `POST /api/chat` - 发送聊天消息
- `POST /api/upload-image` - 上传图像
- `GET /uploads/{filename}` - 获取上传的图像

完整API文档请访问：http://localhost:8000/docs

### 🤝 贡献指南

我们欢迎任何形式的贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

#### 如何贡献

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交Pull Request

### 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

### 💡 常见问题

**Q: API密钥在哪里获取？**  
A: 访问 https://kie.ai/ 注册并在控制台创建API密钥。

**Q: 支持哪些图像格式？**  
A: 支持 PNG, JPEG, JPG, WEBP, GIF 等常见格式。

**Q: 生成图像需要多长时间？**  
A: 通常需要10-30秒，具体取决于网络和服务器负载。

**Q: 可以本地部署吗？**  
A: 可以，但需要配置有效的API密钥连接到KIE.ai服务。

**Q: 如何报告Bug或提出建议？**  
A: 请在 GitHub Issues 中提交。

### 🙏 致谢

- [Google Nano-Banana](https://ai.google.dev/) - 强大的AI图像模型
- [KIE.ai](https://kie.ai/) - AI模型托管平台
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化Web框架
- [Vue.js](https://vuejs.org/) - 渐进式前端框架

---

## <a id="english"></a>🇺🇸 English Documentation

### ✨ Key Features

- 🎨 **AI Image Generation** - Generate beautiful images from text descriptions
- ✏️ **Smart Image Editing** - Upload and edit images with natural language
- 🎯 **Local Editing (Coming Soon)** - Precise region editing with brush tools
- 📐 **Multiple Aspect Ratios** - Support for 1:1, 16:9, 9:16, 4:3, 3:4, etc.
- 💬 **Conversation Management** - Auto-save all conversations and generated images
- 📱 **Responsive Design** - Perfect for desktop and mobile devices
- 🌐 **Modern Interface** - Smooth user experience with Vue 3

### 🚀 Roadmap

We're actively developing these powerful features:

- 🔪 **One-Click Background Removal** - Intelligent subject detection
- 🔍 **Image Super-Resolution** - AI-powered image upscaling
- 🎬 **Video Generation** - Text-to-video and image-to-video
- 🎭 **Style Transfer** - Transform images into artistic styles
- 🖼️ **Batch Processing** - Process multiple images simultaneously
- 🎨 **Advanced Brush Tools** - Fine-grained local editing control

### 📦 Quick Start

#### 1. Requirements

- Python 3.8 or higher
- pip package manager

#### 2. Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/nano-banana-ai.git
cd nano-banana-ai

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp config.example.json config.json
# Edit config.json and add your Nano-Banana API key
```

#### 3. Get API Key

1. Visit [KIE.ai](https://kie.ai/) and create an account
2. Generate an API key in the dashboard
3. Add the API key to `config.json` in the `api.nano_banana_api_key` field

#### 4. Launch Application

```bash
# Method 1: Using launch script
python run.py

# Method 2: Direct backend launch
python backend.py
```

#### 5. Access Application

Open your browser and visit:
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Interactive Docs**: http://localhost:8000/redoc

### 🛠️ Tech Stack

#### Frontend
- **Vue 3** - Progressive JavaScript framework
- **Axios** - HTTP client
- **HTML5 Canvas** - Image drawing and editing

#### Backend
- **FastAPI** - Modern Python web framework
- **Uvicorn** - High-performance ASGI server
- **Pydantic** - Data validation
- **Pillow** - Image processing library

#### AI Services
- **Google Nano-Banana** - Image generation and editing
- **KIE.ai Platform** - AI model hosting platform

### 📁 Project Structure

```
nano-banana-ai/
├── backend.py              # FastAPI backend main program
├── gemini_api.py           # Nano-Banana API wrapper
├── index.html              # Vue 3 frontend interface
├── run.py                  # Application launcher
├── config.json             # Configuration file (create manually)
├── config.example.json     # Configuration template
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore configuration
├── README.md              # Project documentation
└── uploads/               # Uploaded images directory (auto-created)
```

### 🎯 Usage Guide

#### Image Generation
1. Describe the image you want, e.g., "a cute orange cat playing on the grass"
2. Select aspect ratio (optional)
3. Click send and wait for AI to generate the image

#### Image Editing
1. Click "Upload Image" button and select an image to edit
2. Describe the changes, e.g., "turn the sky into sunset"
3. Click send, AI will edit the image based on your description

#### Local Editing (Experimental)
1. After uploading an image, click the "Brush" tool
2. Mark the areas you want to edit on the image
3. Describe the changes, AI will only modify the marked regions

### 🔧 Configuration

`config.json` configuration file explanation:

```json
{
  "api": {
    "nano_banana_api_key": "YOUR_API_KEY_HERE",  // Required: Your API key
    "comment": "Get your API key at https://kie.ai/"
  },
  "server": {
    "host": "127.0.0.1",      // Server address
    "port": 7864,             // Server port
    "share": false            // Generate public URL
  },
  "generation": {
    "default_width": 512,     // Default image width
    "default_height": 512,    // Default image height
    "max_width": 1024,        // Maximum image width
    "max_height": 1024        // Maximum image height
  }
}
```

### 🌍 Environment Variables (Optional)

You can also set the API key using environment variables:

```bash
# Linux/Mac
export NANO_BANANA_API_KEY="your_api_key_here"

# Windows (PowerShell)
$env:NANO_BANANA_API_KEY="your_api_key_here"

# Windows (CMD)
set NANO_BANANA_API_KEY=your_api_key_here
```

### 📝 API Endpoints

Main API endpoints:

- `GET /` - Web interface
- `GET /api/conversations` - Get conversation list
- `POST /api/conversations` - Create new conversation
- `DELETE /api/conversations/{id}` - Delete conversation
- `POST /api/chat` - Send chat message
- `POST /api/upload-image` - Upload image
- `GET /uploads/{filename}` - Get uploaded image

Full API documentation: http://localhost:8000/docs

### 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

#### How to Contribute

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details

### 💡 FAQ

**Q: Where do I get an API key?**  
A: Visit https://kie.ai/ to register and create an API key in the dashboard.

**Q: What image formats are supported?**  
A: PNG, JPEG, JPG, WEBP, GIF, and other common formats.

**Q: How long does image generation take?**  
A: Usually 10-30 seconds, depending on network and server load.

**Q: Can I deploy this locally?**  
A: Yes, but you need a valid API key to connect to KIE.ai services.

**Q: How do I report bugs or suggest features?**  
A: Please submit an issue on GitHub Issues.

### 🙏 Acknowledgments

- [Google Nano-Banana](https://ai.google.dev/) - Powerful AI image model
- [KIE.ai](https://kie.ai/) - AI model hosting platform
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [Vue.js](https://vuejs.org/) - Progressive frontend framework

---

<div align="center">

**Made with ❤️ by the Nano-Banana Community**

[⬆ Back to Top](#-nano-banana-ai-image-studio)

</div>
