# 🤝 贡献指南 | Contributing Guide

[中文](#chinese) | [English](#english)

---

## <a id="chinese"></a>🇨🇳 中文

感谢您对 Nano-Banana AI Image Studio 的关注！我们欢迎所有形式的贡献。

### 📋 贡献方式

- 🐛 **报告Bug** - 帮助我们发现和修复问题
- 💡 **提出建议** - 分享您对新功能的想法
- 📝 **改进文档** - 帮助完善项目文档
- 💻 **提交代码** - 直接贡献代码
- 🌍 **翻译** - 帮助翻译界面和文档

### 🐛 报告Bug

发现Bug？请创建Issue并包含：

1. **清晰的标题** - 简洁描述问题
2. **环境信息**：
   - 操作系统（Windows/Mac/Linux）
   - Python版本
   - 浏览器版本
3. **重现步骤** - 详细说明如何触发Bug
4. **预期行为** - 您期望发生什么
5. **实际行为** - 实际发生了什么
6. **截图/日志** - 如果可能，提供截图或错误日志

**示例**：
```
标题: 图像生成失败并显示超时错误

环境:
- OS: Windows 10
- Python: 3.9.5
- Browser: Chrome 120

步骤:
1. 输入提示词 "a beautiful sunset"
2. 点击发送按钮
3. 等待30秒后显示超时错误

预期: 应该生成日落图像
实际: 显示 "请求超时" 错误

错误日志:
[粘贴错误日志]
```

### 💡 功能建议

有新想法？我们很乐意听到！请创建Issue并说明：

1. **功能描述** - 您想要什么功能
2. **使用场景** - 这个功能解决什么问题
3. **期望实现** - 您期望如何使用这个功能
4. **替代方案** - 是否有其他解决方案

### 💻 提交代码

#### 开发流程

1. **Fork 仓库**
   ```bash
   # 点击GitHub页面右上角的 Fork 按钮
   ```

2. **克隆您的Fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/nano-banana-ai.git
   cd nano-banana-ai
   ```

3. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   # 或
   git checkout -b fix/bug-description
   ```

4. **设置开发环境**
   ```bash
   # 创建虚拟环境
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate  # Windows

   # 安装依赖
   pip install -r requirements.txt
   ```

5. **进行更改**
   - 编写代码
   - 遵循代码风格（见下文）
   - 添加必要的注释

6. **测试您的更改**
   ```bash
   # 运行应用确保一切正常
   python run.py
   ```

7. **提交更改**
   ```bash
   git add .
   git commit -m "描述您的更改"
   ```

8. **推送到您的Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

9. **创建Pull Request**
   - 访问GitHub上的原始仓库
   - 点击 "New Pull Request"
   - 选择您的分支
   - 详细描述您的更改

#### 代码规范

**Python代码**：
- 遵循 [PEP 8](https://pep8.org/) 风格指南
- 使用4个空格缩进（不使用Tab）
- 函数和变量使用snake_case命名
- 类使用PascalCase命名
- 添加文档字符串（docstrings）

**示例**：
```python
def generate_image(prompt: str, aspect_ratio: str = "1:1") -> Optional[str]:
    """
    生成AI图像
    
    Args:
        prompt: 图像描述提示词
        aspect_ratio: 图像比例，默认为"1:1"
        
    Returns:
        图像URL，失败时返回None
    """
    # 实现代码...
    pass
```

**JavaScript/Vue代码**：
- 使用2个空格缩进
- 使用camelCase命名变量和函数
- 使用PascalCase命名Vue组件
- 添加注释说明复杂逻辑

**提交信息**：
- 使用清晰、描述性的提交信息
- 第一行：简短总结（50字符内）
- 空一行
- 详细描述（如需要）

**示例**：
```
添加批量图像生成功能

- 实现批量生成API端点
- 添加前端批量上传界面
- 更新文档说明批量功能
```

#### Pull Request 准则

1. **一个PR只做一件事** - 避免在一个PR中混合多个不相关的更改
2. **更新文档** - 如果添加新功能，请更新README.md
3. **保持向后兼容** - 避免破坏现有API
4. **测试** - 确保所有功能正常工作
5. **描述清楚** - 在PR描述中说明：
   - 改了什么
   - 为什么改
   - 如何测试

### 📝 文档贡献

文档改进非常重要！您可以：

- 修正拼写错误和语法问题
- 改进说明的清晰度
- 添加更多使用示例
- 翻译文档到其他语言

### 🌍 翻译

帮助翻译项目到其他语言：

1. 复制 `README.md` 创建 `README.{lang}.md`
2. 翻译内容
3. 提交Pull Request

### ❓ 问题和讨论

- **提问** - 使用 GitHub Discussions
- **Bug报告** - 使用 GitHub Issues
- **功能请求** - 使用 GitHub Issues

### 📜 行为准则

- 尊重所有贡献者
- 使用友好和包容的语言
- 接受建设性批评
- 关注对社区最有利的事情

### 🎯 优先开发领域

我们特别欢迎以下方面的贡献：

- 🔪 一键抠图功能
- 🔍 图像超分辨率
- 🎬 视频生成功能
- 🎨 更多画笔工具
- 🌐 国际化（i18n）
- 📱 移动端优化
- 🧪 单元测试

### 📧 联系方式

如有疑问，请：
- 创建 GitHub Issue
- 发起 GitHub Discussion

---

## <a id="english"></a>🇺🇸 English

Thank you for your interest in contributing to Nano-Banana AI Image Studio! We welcome all forms of contributions.

### 📋 Ways to Contribute

- 🐛 **Report Bugs** - Help us find and fix issues
- 💡 **Suggest Features** - Share your ideas for new features
- 📝 **Improve Documentation** - Help improve project docs
- 💻 **Submit Code** - Contribute code directly
- 🌍 **Translate** - Help translate interface and docs

### 🐛 Reporting Bugs

Found a bug? Please create an Issue including:

1. **Clear Title** - Briefly describe the problem
2. **Environment Info**:
   - Operating System (Windows/Mac/Linux)
   - Python version
   - Browser version
3. **Reproduction Steps** - Detailed steps to trigger the bug
4. **Expected Behavior** - What you expected to happen
5. **Actual Behavior** - What actually happened
6. **Screenshots/Logs** - If possible, provide screenshots or error logs

**Example**:
```
Title: Image generation fails with timeout error

Environment:
- OS: Windows 10
- Python: 3.9.5
- Browser: Chrome 120

Steps:
1. Enter prompt "a beautiful sunset"
2. Click send button
3. After 30 seconds, timeout error appears

Expected: Should generate sunset image
Actual: Shows "Request timeout" error

Error log:
[paste error log]
```

### 💡 Feature Requests

Have a new idea? We'd love to hear it! Please create an Issue explaining:

1. **Feature Description** - What feature you want
2. **Use Case** - What problem does this solve
3. **Expected Implementation** - How you expect to use this feature
4. **Alternatives** - Any alternative solutions

### 💻 Contributing Code

#### Development Workflow

1. **Fork the Repository**
   ```bash
   # Click the Fork button in the top right of the GitHub page
   ```

2. **Clone Your Fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/nano-banana-ai.git
   cd nano-banana-ai
   ```

3. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```

4. **Set Up Development Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate  # Windows

   # Install dependencies
   pip install -r requirements.txt
   ```

5. **Make Changes**
   - Write code
   - Follow code style (see below)
   - Add necessary comments

6. **Test Your Changes**
   ```bash
   # Run the application to ensure everything works
   python run.py
   ```

7. **Commit Changes**
   ```bash
   git add .
   git commit -m "Describe your changes"
   ```

8. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

9. **Create Pull Request**
   - Visit the original repository on GitHub
   - Click "New Pull Request"
   - Select your branch
   - Describe your changes in detail

#### Code Style

**Python Code**:
- Follow [PEP 8](https://pep8.org/) style guide
- Use 4 spaces for indentation (no tabs)
- Use snake_case for functions and variables
- Use PascalCase for classes
- Add docstrings

**Example**:
```python
def generate_image(prompt: str, aspect_ratio: str = "1:1") -> Optional[str]:
    """
    Generate AI image
    
    Args:
        prompt: Image description prompt
        aspect_ratio: Image aspect ratio, defaults to "1:1"
        
    Returns:
        Image URL, or None if failed
    """
    # Implementation...
    pass
```

**JavaScript/Vue Code**:
- Use 2 spaces for indentation
- Use camelCase for variables and functions
- Use PascalCase for Vue components
- Add comments for complex logic

**Commit Messages**:
- Use clear, descriptive commit messages
- First line: Short summary (under 50 characters)
- Blank line
- Detailed description (if needed)

**Example**:
```
Add batch image generation feature

- Implement batch generation API endpoint
- Add frontend batch upload interface
- Update documentation for batch feature
```

#### Pull Request Guidelines

1. **One PR, One Purpose** - Avoid mixing unrelated changes
2. **Update Documentation** - Update README.md if adding new features
3. **Maintain Backward Compatibility** - Avoid breaking existing APIs
4. **Test** - Ensure all features work properly
5. **Clear Description** - In PR description, explain:
   - What changed
   - Why it changed
   - How to test

### 📝 Documentation Contributions

Documentation improvements are important! You can:

- Fix typos and grammar issues
- Improve clarity of explanations
- Add more usage examples
- Translate docs to other languages

### 🌍 Translation

Help translate the project to other languages:

1. Copy `README.md` to create `README.{lang}.md`
2. Translate content
3. Submit Pull Request

### ❓ Questions and Discussions

- **Questions** - Use GitHub Discussions
- **Bug Reports** - Use GitHub Issues
- **Feature Requests** - Use GitHub Issues

### 📜 Code of Conduct

- Respect all contributors
- Use welcoming and inclusive language
- Accept constructive criticism
- Focus on what's best for the community

### 🎯 Priority Development Areas

We especially welcome contributions in:

- 🔪 One-click background removal
- 🔍 Image super-resolution
- 🎬 Video generation
- 🎨 More brush tools
- 🌐 Internationalization (i18n)
- 📱 Mobile optimization
- 🧪 Unit testing

### 📧 Contact

If you have questions:
- Create a GitHub Issue
- Start a GitHub Discussion

---

<div align="center">

**Thank you for contributing! 🎉**

</div>


