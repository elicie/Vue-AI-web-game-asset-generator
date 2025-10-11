# 📦 安装指南 | Installation Guide

[中文](#chinese) | [English](#english)

---

## <a id="chinese"></a>🇨🇳 详细安装步骤

### 系统要求

- **操作系统**: Windows 10/11, macOS 10.15+, Linux (Ubuntu 18.04+)
- **Python**: 3.8 或更高版本
- **内存**: 至少 4GB RAM
- **磁盘空间**: 至少 1GB 可用空间
- **网络**: 稳定的互联网连接（用于API调用）

### 步骤 1: 安装 Python

#### Windows
1. 访问 [Python官网](https://www.python.org/downloads/)
2. 下载 Python 3.8+ 安装程序
3. 运行安装程序，**勾选 "Add Python to PATH"**
4. 验证安装：
   ```cmd
   python --version
   ```

#### macOS
```bash
# 使用 Homebrew
brew install python@3.11

# 验证安装
python3 --version
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv

# 验证安装
python3 --version
```

### 步骤 2: 克隆项目

```bash
# 使用 HTTPS
git clone https://github.com/yourusername/nano-banana-ai.git

# 或使用 SSH
git clone git@github.com:yourusername/nano-banana-ai.git

# 进入项目目录
cd nano-banana-ai
```

### 步骤 3: 创建虚拟环境（推荐）

#### Windows
```cmd
python -m venv venv
venv\Scripts\activate
```

#### macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

### 步骤 4: 安装依赖

```bash
# 升级 pip
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt
```

如果遇到安装问题，可以尝试：
```bash
pip install -r requirements.txt --no-cache-dir
```

### 步骤 5: 配置 API 密钥

#### 方式 1: 使用配置文件（推荐）

```bash
# 复制配置模板
cp config.example.json config.json

# Windows
copy config.example.json config.json
```

编辑 `config.json`，填入您的API密钥：
```json
{
  "api": {
    "nano_banana_api_key": "your_actual_api_key_here"
  }
}
```

#### 方式 2: 使用环境变量

**Linux/macOS**:
```bash
export NANO_BANANA_API_KEY="your_api_key_here"
```

**Windows PowerShell**:
```powershell
$env:NANO_BANANA_API_KEY="your_api_key_here"
```

**Windows CMD**:
```cmd
set NANO_BANANA_API_KEY=your_api_key_here
```

### 步骤 6: 获取 API 密钥

1. 访问 [KIE.ai](https://kie.ai/)
2. 注册/登录账户
3. 进入控制台
4. 创建新的API密钥
5. 复制密钥并保存到 `config.json`

### 步骤 7: 启动应用

```bash
# 方式 1: 使用启动脚本
python run.py

# 方式 2: 直接启动
python backend.py

# 方式 3: 使用 uvicorn
uvicorn backend:app --host 0.0.0.0 --port 8000 --reload
```

### 步骤 8: 访问应用

打开浏览器访问：
- **主界面**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

---

## 🔧 常见问题

### 问题 1: ModuleNotFoundError

**错误**: `ModuleNotFoundError: No module named 'fastapi'`

**解决**:
```bash
# 确保虚拟环境已激活
pip install -r requirements.txt
```

### 问题 2: 端口被占用

**错误**: `Address already in use`

**解决**:
```bash
# 更改端口
uvicorn backend:app --port 8001
```

### 问题 3: API密钥无效

**错误**: `❌ API密钥未配置`

**解决**:
1. 检查 `config.json` 是否存在
2. 确认 API 密钥格式正确
3. 验证密钥是否有效

### 问题 4: Python版本过低

**错误**: `SyntaxError` 或版本相关错误

**解决**:
```bash
# 检查Python版本
python --version

# 应该是 3.8 或更高
# 如果不是，请升级Python
```

### 问题 5: pip 安装速度慢

**解决**:
```bash
# 使用国内镜像源（中国用户）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 📱 Docker 部署（可选）

创建 `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "run.py"]
```

构建和运行：
```bash
# 构建镜像
docker build -t nano-banana-ai .

# 运行容器
docker run -p 8000:8000 -v $(pwd)/config.json:/app/config.json nano-banana-ai
```

---

## 🔄 更新项目

```bash
# 拉取最新代码
git pull origin main

# 更新依赖
pip install -r requirements.txt --upgrade

# 重启应用
python run.py
```

---

## <a id="english"></a>🇺🇸 English

### System Requirements

- **OS**: Windows 10/11, macOS 10.15+, Linux (Ubuntu 18.04+)
- **Python**: 3.8 or higher
- **Memory**: At least 4GB RAM
- **Disk Space**: At least 1GB free space
- **Network**: Stable internet connection (for API calls)

### Step 1: Install Python

#### Windows
1. Visit [Python official website](https://www.python.org/downloads/)
2. Download Python 3.8+ installer
3. Run installer, **check "Add Python to PATH"**
4. Verify installation:
   ```cmd
   python --version
   ```

#### macOS
```bash
# Using Homebrew
brew install python@3.11

# Verify installation
python3 --version
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Verify installation
python3 --version
```

### Step 2: Clone Repository

```bash
# Using HTTPS
git clone https://github.com/yourusername/nano-banana-ai.git

# Or using SSH
git clone git@github.com:yourusername/nano-banana-ai.git

# Enter project directory
cd nano-banana-ai
```

### Step 3: Create Virtual Environment (Recommended)

#### Windows
```cmd
python -m venv venv
venv\Scripts\activate
```

#### macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 4: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt
```

If you encounter installation issues:
```bash
pip install -r requirements.txt --no-cache-dir
```

### Step 5: Configure API Key

#### Method 1: Using Config File (Recommended)

```bash
# Copy config template
cp config.example.json config.json

# Windows
copy config.example.json config.json
```

Edit `config.json` with your API key:
```json
{
  "api": {
    "nano_banana_api_key": "your_actual_api_key_here"
  }
}
```

#### Method 2: Using Environment Variable

**Linux/macOS**:
```bash
export NANO_BANANA_API_KEY="your_api_key_here"
```

**Windows PowerShell**:
```powershell
$env:NANO_BANANA_API_KEY="your_api_key_here"
```

**Windows CMD**:
```cmd
set NANO_BANANA_API_KEY=your_api_key_here
```

### Step 6: Get API Key

1. Visit [KIE.ai](https://kie.ai/)
2. Register/Login
3. Go to dashboard
4. Create new API key
5. Copy and save to `config.json`

### Step 7: Launch Application

```bash
# Method 1: Using launch script
python run.py

# Method 2: Direct launch
python backend.py

# Method 3: Using uvicorn
uvicorn backend:app --host 0.0.0.0 --port 8000 --reload
```

### Step 8: Access Application

Open browser and visit:
- **Main Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

---

## 🔧 Troubleshooting

### Issue 1: ModuleNotFoundError

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
# Make sure virtual environment is activated
pip install -r requirements.txt
```

### Issue 2: Port Already in Use

**Error**: `Address already in use`

**Solution**:
```bash
# Change port
uvicorn backend:app --port 8001
```

### Issue 3: Invalid API Key

**Error**: `❌ API密钥未配置`

**Solution**:
1. Check if `config.json` exists
2. Verify API key format
3. Validate key is active

### Issue 4: Python Version Too Old

**Error**: `SyntaxError` or version-related errors

**Solution**:
```bash
# Check Python version
python --version

# Should be 3.8 or higher
# If not, upgrade Python
```

### Issue 5: Slow pip Installation

**Solution**:
```bash
# Use mirror (for users in China)
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 📱 Docker Deployment (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "run.py"]
```

Build and run:
```bash
# Build image
docker build -t nano-banana-ai .

# Run container
docker run -p 8000:8000 -v $(pwd)/config.json:/app/config.json nano-banana-ai
```

---

## 🔄 Update Project

```bash
# Pull latest code
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart application
python run.py
```

---

<div align="center">

**Need help? Create an issue on GitHub!**

</div>


