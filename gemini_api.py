"""
Nano-Banana API接口模块（使用kie.ai平台）
支持文本生成和图像生成功能
"""

import os
import requests
import json
import time
import base64
import mimetypes
from typing import Optional, Dict, Any, List, Union
from PIL import Image
from io import BytesIO


class NanoBananaAPI:
    """Nano-Banana API接口类（基于kie.ai平台）"""

    RATIO_MAPPING = {
        "auto": "auto",
        "1:1": "1:1",
        "9:16": "9:16",
        "16:9": "16:9",
        "3:4": "3:4",
        "4:3": "4:3",
        "3:2": "3:2",
        "2:3": "2:3",
        "5:4": "5:4",
        "4:5": "4:5"
    }

    def _apply_aspect_ratio(self, payload: dict, aspect_ratio: str,
                            image_size: str = "auto") -> str:
        """Apply aspect ratio settings to an API payload.

        Sets the ratio in multiple payload fields (config, input.aspect_ratio,
        input.image_size) because the upstream API docs are ambiguous about which
        field it reads. All three are set consistently to the same resolved value.

        Returns the resolved ratio string.
        """
        resolved = self.RATIO_MAPPING.get(aspect_ratio, image_size)
        value = resolved if aspect_ratio != "auto" else "1:1"

        payload["config"] = {
            "response_modalities": ["Image"],
            "image_config": {"aspect_ratio": value},
        }
        payload["input"]["aspect_ratio"] = value
        payload["input"]["image_size"] = value
        return resolved

    def __init__(self, api_key: str):
        """
        初始化Nano-Banana API
        
        Args:
            api_key: Nano-Banana API密钥
        """
        self.api_key = api_key
        self.base_url = "https://api.kie.ai"
        self.create_task_endpoint = "/api/v1/jobs/createTask"
        # 根据官方示例使用正确的查询端点
        self.query_task_endpoint = "/api/v1/jobs/recordInfo"
        # KIE.ai文件上传API配置
        self.upload_base_url = "https://kieai.redpandaai.co"
        
        print(f"🍌 使用Nano-Banana API - 图像生成: kie.ai平台")
    
    def generate_content(self, text: str, conversation_history: Optional[List[Dict]] = None) -> Optional[str]:
        """
        生成文本内容（使用简单回复，因为Nano-Banana主要用于图像生成）
        
        Args:
            text: 输入文本
            conversation_history: 对话历史（可选）
            
        Returns:
            生成的文本内容
        """
        # 为Nano-Banana API提供简单的文本回复
        # 因为主要用途是图像生成，文本对话功能相对简单
        if "图" in text or "生成" in text or "image" in text.lower():
            return "🍌 我是Nano-Banana AI，主要用于图像生成。请告诉我您想要生成什么样的图像，我会为您创作精美的视觉内容！"
        else:
            return f"🍌 你好！我是Nano-Banana AI，主要擅长图像生成。您的问题是：{text}。如果您需要生成图像，请直接描述您想要的内容！"
    
    def enhance_image_prompt(self, user_input: str) -> str:
        """
        使用Gemini优化图像生成提示词
        
        Args:
            user_input: 用户原始输入
            
        Returns:
            优化后的提示词
        """
        enhancement_prompt = f"""
请将以下用户描述转换为更详细、更适合AI图像生成的英文提示词。要求：
1. 保持原意，但添加更多视觉细节
2. 使用适合AI图像生成的描述风格
3. 包含质量词汇如"high quality", "detailed", "beautiful"
4. 直接返回优化后的英文提示词，不要额外解释

用户描述：{user_input}
"""
        
        enhanced = self.generate_content(enhancement_prompt)
        return enhanced if enhanced else user_input
    
    def generate_image_with_nano_banana(self, prompt: str, num_images: int = 1, 
                                      output_format: str = "png", 
                                      image_size: str = "auto",
                                      aspect_ratio: str = "auto") -> Optional[List[Image.Image]]:
        """
        使用Nano-Banana API生成图像
        
        Args:
            prompt: 图像描述提示词
            num_images: 生成图像数量（1-4张）
            output_format: 输出格式 ("png" 或 "jpeg")
            image_size: 图像尺寸 ("auto", "1:1", "3:4", "9:16", "4:3", "16:9")
            aspect_ratio: 图像比例 ("auto", "1:1", "9:16", "16:9", "3:4", "4:3", "3:2", "2:3", "5:4", "4:5")
            
        Returns:
            生成的图像列表
        """
        try:
            # 限制图像数量
            num_images = max(1, min(4, num_images))
            
            enhanced_prompt = prompt
            
            print(f"\U0001f34c 使用Nano-Banana API生成{num_images}张图像: {enhanced_prompt}")
            
            # 按照官方示例构建请求数据
            payload = {
                "model": "google/nano-banana",
                "input": {
                    "prompt": enhanced_prompt,
                    "output_format": output_format.lower()
                }
            }
            
            # Apply aspect ratio to payload
            final_image_size = self._apply_aspect_ratio(payload, aspect_ratio, image_size)
            print(f"\U0001f4d0 图像比例: {aspect_ratio} -> {final_image_size}")
            
            print(f"\U0001f50d 完整payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            images = []
            
            # 为每张图像发送请求
            for i in range(num_images):
                print(f"🚀 正在生成第 {i+1}/{num_images} 张图像...")
                
                # 按照官方示例发送请求
                response = requests.post(
                    f"{self.base_url}{self.create_task_endpoint}",
                    headers=headers,
                    data=json.dumps(payload),
                    timeout=60
                )
                
                print(f"📊 API响应状态: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ 任务创建成功: {result}")
                    
                    # 检查API是否支持我们的config格式
                    if "error" in result or "message" in result:
                        print(f"⚠️ API可能不支持当前格式: {result}")
                    
                    # 检查任务状态和结果
                    if "data" in result:
                        task_data = result["data"]
                        
                        # 如果直接返回了图像结果
                        if "output" in task_data:
                            output = task_data["output"]
                            
                            # 处理不同的输出格式
                            if isinstance(output, str):
                                if output.startswith('http'):
                                    # URL格式
                                    try:
                                        img_response = requests.get(output, timeout=30)
                                        if img_response.status_code == 200:
                                            image = Image.open(BytesIO(img_response.content))
                                            images.append(image)
                                            print(f"✅ 成功下载图像 {i+1}: {image.size}")
                                    except Exception as e:
                                        print(f"❌ 图像下载失败: {e}")
                                elif output.startswith('data:image/'):
                                    # Base64 Data URL格式
                                    try:
                                        image_data = base64.b64decode(output.split(',')[1])
                                        image = Image.open(BytesIO(image_data))
                                        images.append(image)
                                        print(f"✅ 成功解码图像 {i+1}: {image.size}")
                                    except Exception as e:
                                        print(f"❌ 图像解码失败: {e}")
                            elif isinstance(output, dict) and "url" in output:
                                # 嵌套的URL格式
                                try:
                                    img_response = requests.get(output["url"], timeout=30)
                                    if img_response.status_code == 200:
                                        image = Image.open(BytesIO(img_response.content))
                                        images.append(image)
                                        print(f"✅ 成功下载图像 {i+1}: {image.size}")
                                except Exception as e:
                                    print(f"❌ 图像下载失败: {e}")
                        
                        # 如果需要轮询任务状态
                        elif "taskId" in task_data or "recordId" in task_data:
                            task_id = task_data.get("taskId") or task_data.get("recordId")
                            print(f"🔄 任务ID: {task_id}, 轮询任务状态...")

                            result_urls = self._poll_task_result(task_id)
                            if result_urls:
                                for url in result_urls:
                                    images.append(url)
                                    print(f"✅ 成功获取图像URL {i+1}: {url}")
                elif response.status_code == 401:
                    print(f"❌ 认证失败: API密钥无效或没有权限")
                    print(f"详细信息: {response.text}")
                    break
                elif response.status_code == 400:
                    print(f"❌ 请求参数错误: {response.text}")
                    break
                else:
                    print(f"❌ API请求失败: {response.status_code}")
                    print(f"详细信息: {response.text}")
                    break
            
            return images if images else None
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Nano-Banana图像生成失败: {error_msg}")
            
            # 特殊处理不同类型的错误
            if "unauthorized" in error_msg.lower() or "401" in error_msg:
                print("💡 解决建议:")
                print("1. 检查API密钥是否正确")
                print("2. 确认API密钥是否有权限访问nano-banana服务")
            elif "quota" in error_msg.lower() or "429" in error_msg:
                print("💡 配额限制:")
                print("1. API调用次数已达到限制")
                print("2. 请等待配额重置或升级账户")
            elif "timeout" in error_msg.lower():
                print("💡 网络问题:")
                print("1. 网络连接超时，请检查网络状况")
                print("2. 可以尝试重新生成")
            
            return None
    
    def edit_image_with_nano_banana(self, prompt: str, input_image_url: str, 
                                  mask_image_url: Optional[str] = None,
                                  output_format: str = "png", 
                                  image_size: str = "auto",
                                  aspect_ratio: str = "auto") -> Optional[str]:
        """
        使用Nano-Banana Edit API编辑图像
        
        Args:
            prompt: 编辑指令描述
            input_image_url: 输入图像URL
            mask_image_url: 遮罩图像URL（可选，指定编辑区域）
            output_format: 输出格式 ("png" 或 "jpeg")
            image_size: 图像尺寸 ("auto", "1:1", "3:4", "9:16", "4:3", "16:9")
            aspect_ratio: 图像比例 ("auto", "1:1", "9:16", "16:9", "3:4", "4:3", "3:2", "2:3", "5:4", "4:5")
            
        Returns:
            编辑后的图像URL
        """
        try:
            # 使用原始prompt，让API通过image_config处理比例
            enhanced_prompt = prompt
            
            print(f"🎨 使用Nano-Banana Edit API编辑图像: {enhanced_prompt}")
            print(f"📥 输入图像: {input_image_url[:100]}..." if len(input_image_url) > 100 else input_image_url)
            
            if mask_image_url:
                print(f"🎯 遮罩图像: {mask_image_url[:100]}..." if len(mask_image_url) > 100 else mask_image_url)
            
            # 如果是中文指令，尝试简单翻译为英文
            english_prompt = self._translate_to_english(prompt)
            if english_prompt != prompt:
                print(f"🌐 指令翻译: {prompt} -> {english_prompt}")
            
            # 按照官方示例构建请求数据
            payload = {
                "model": "google/nano-banana-edit",
                "input": {
                    "prompt": enhanced_prompt,
                    "image_urls": [input_image_url],
                    "output_format": output_format.lower()
                }
            }
            
            # Apply aspect ratio to payload
            final_image_size = self._apply_aspect_ratio(payload, aspect_ratio, image_size)
            
            if mask_image_url:
                payload["input"]["mask_image"] = mask_image_url
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            print(f"🚀 正在编辑图像...")
            
            # 按照官方示例发送请求
            response = requests.post(
                f"{self.base_url}{self.create_task_endpoint}",
                headers=headers,
                data=json.dumps(payload),
                timeout=60
            )
            
            print(f"📊 API响应状态: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 任务创建成功: {result}")
                
                # 首先检查API返回的code字段
                if result.get("code") != 200:
                    # API返回了错误
                    error_msg = result.get("msg", "未知错误")
                    error_code = result.get("code", "")
                    print(f"❌ API返回错误: [{error_code}] {error_msg}")
                    return f"ERROR: [{error_code}] {error_msg}"
                
                # 检查任务状态和结果
                if "data" in result:
                    task_data = result["data"]
                    
                    # 如果直接返回了图像结果
                    if "output" in task_data:
                        output = task_data["output"]
                        
                        # 处理不同的输出格式
                        if isinstance(output, str):
                            if output.startswith('http'):
                                # URL格式
                                print(f"✅ 成功获取编辑图像URL: {output}")
                                return output
                            elif output.startswith('data:image/'):
                                # Base64 Data URL格式
                                print(f"✅ 获取到Base64图像数据")
                                return output
                        elif isinstance(output, dict) and "url" in output:
                            # 嵌套的URL格式
                            print(f"✅ 成功获取编辑图像URL: {output['url']}")
                            return output["url"]
                    
                    # 如果需要轮询任务状态
                    elif "taskId" in task_data or "recordId" in task_data:
                        task_id = task_data.get("taskId") or task_data.get("recordId")
                        print(f"🔄 任务ID: {task_id}, 轮询任务状态...")

                        result_urls = self._poll_task_result(task_id)
                        if result_urls:
                            image_url = result_urls[0]
                            print(f"✅ 成功获取编辑图像URL: {image_url}")
                            return image_url

            elif response.status_code == 401:
                print(f"❌ 认证失败: API密钥无效或没有权限")
                print(f"详细信息: {response.text}")
            elif response.status_code == 400:
                print(f"❌ 请求参数错误: {response.text}")
            else:
                print(f"❌ API请求失败: {response.status_code}")
                print(f"详细信息: {response.text}")
            
            return None
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Nano-Banana图像编辑失败: {error_msg}")
            
            # 特殊处理不同类型的错误
            if "unauthorized" in error_msg.lower() or "401" in error_msg:
                print("💡 解决建议:")
                print("1. 检查API密钥是否正确")
                print("2. 确认API密钥是否有权限访问nano-banana-edit服务")
            elif "quota" in error_msg.lower() or "429" in error_msg:
                print("💡 配额限制:")
                print("1. API调用次数已达到限制")
                print("2. 请等待配额重置或升级账户")
            elif "timeout" in error_msg.lower():
                print("💡 网络问题:")
                print("1. 网络连接超时，请检查网络状况")
                print("2. 可以尝试重新编辑")
            
            return None

    def _poll_task_result(self, task_id: str) -> Optional[List[str]]:
        """
        轮询异步任务状态直到完成或超时。

        Args:
            task_id: API返回的任务ID (taskId or recordId)

        Returns:
            成功时返回 resultUrls 列表；失败时返回 None。
            失败信息通过 stderr 打印。
        """
        max_retries = 60
        poll_interval = 3

        for retry in range(max_retries):
            time.sleep(poll_interval)

            try:
                params = {"taskId": task_id}
                query_headers = {"Authorization": f"Bearer {self.api_key}"}

                status_response = requests.get(
                    f"{self.base_url}{self.query_task_endpoint}",
                    headers=query_headers,
                    params=params,
                    timeout=30
                )

                if status_response.status_code == 200:
                    status_result = status_response.json()
                    print(f"🔄 第{retry+1}次查询，API响应码: {status_result.get('code', 'unknown')}")

                    if status_result.get("code") == 200 and "data" in status_result:
                        data = status_result["data"]
                        current_state = data.get("state", "unknown")
                        print(f"📋 任务状态: {current_state}")

                        if current_state == "success":
                            if "resultJson" in data and data["resultJson"]:
                                try:
                                    result_json = json.loads(data["resultJson"])
                                    print(f"🎯 解析结果: {result_json}")

                                    if "resultUrls" in result_json and result_json["resultUrls"]:
                                        return result_json["resultUrls"]
                                    else:
                                        print("⚠️ resultJson中没有找到resultUrls")
                                except json.JSONDecodeError as e:
                                    print(f"❌ 解析resultJson失败: {e}")
                                    print(f"原始resultJson: {data.get('resultJson', 'None')}")
                            else:
                                print("⚠️ 任务成功但没有resultJson")
                            return None

                        elif current_state == "fail":
                            fail_msg = data.get("failMsg", "未知错误")
                            fail_code = data.get("failCode", "")
                            print(f"❌ 任务失败: [{fail_code}] {fail_msg}")
                            return None

                        elif current_state in ["waiting", "processing", "pending", "running", "generating"]:
                            print(f"⏳ 任务仍在处理中... ({retry+1}/{max_retries})")
                            continue
                        else:
                            print(f"🔄 未知任务状态: {current_state}")
                    else:
                        print(f"❌ API响应错误: 代码={status_result.get('code')}, 消息={status_result.get('message')}")
                else:
                    print(f"❌ 查询任务状态失败: {status_response.status_code} - {status_response.text[:100]}")

            except Exception as e:
                print(f"❌ 查询异常: {e}")

        print("⚠️ 任务超时，请稍后手动检查")
        return None

    def _translate_to_english(self, chinese_prompt: str) -> str:
        """
        简单的中文到英文翻译（基于常见编辑指令）
        """
        # 常见的图像编辑指令翻译
        translations = {
            "换成": "change to",
            "变成": "turn into", 
            "改成": "change to",
            "替换": "replace with",
            "金色": "golden",
            "银色": "silver",
            "红色": "red",
            "蓝色": "blue",
            "绿色": "green",
            "黄色": "yellow",
            "黑色": "black",
            "白色": "white",
            "宝石": "gem",
            "水晶": "crystal",
            "钻石": "diamond",
            "卡通": "cartoon style",
            "卡通风格": "cartoon style",
            "现实": "realistic",
            "写实": "realistic",
            "油画": "oil painting style",
            "素描": "sketch style",
            "左前方": "front left",
            "右前方": "front right", 
            "45度": "45 degree",
            "仰视角": "low angle view",
            "俯视角": "top view",
            "侧视角": "side view",
            "logo": "logo",
            "标志": "logo"
        }
        
        # 检查是否包含中文字符
        if not any('\u4e00' <= char <= '\u9fff' for char in chinese_prompt):
            return chinese_prompt  # 已经是英文，直接返回
        
        # 简单替换
        english_prompt = chinese_prompt
        for chinese, english in translations.items():
            english_prompt = english_prompt.replace(chinese, english)
        
        # 如果仍然包含大量中文，提供通用翻译
        if sum(1 for char in english_prompt if '\u4e00' <= char <= '\u9fff') > 3:
            # 提取关键词进行基本翻译
            if "换" in chinese_prompt or "变" in chinese_prompt or "改" in chinese_prompt:
                return f"change this image: {english_prompt}"
            else:
                return f"edit this image: {english_prompt}"
        
        return english_prompt.strip()
    
    def upload_file_to_kie(self, file_path: str) -> Optional[str]:
        """
        使用Base64方式上传本地文件到KIE.ai公网服务
        
        Args:
            file_path: 本地文件路径
            
        Returns:
            公网文件URL，失败返回None
        """
        try:
            print(f"📤 Base64上传文件到KIE.ai: {file_path}")
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                print(f"❌ 文件不存在: {file_path}")
                return None
            
            # 读取文件并转换为Base64
            with open(file_path, 'rb') as file:
                file_data = file.read()
                base64_data = base64.b64encode(file_data).decode('utf-8')
                
                # 获取MIME类型
                mime_type, _ = mimetypes.guess_type(file_path)
                if not mime_type:
                    mime_type = 'image/png'  # 默认为PNG
                
                # 构造data URL格式
                data_url = f"data:{mime_type};base64,{base64_data}"
                
                print(f"📊 Base64数据长度: {len(base64_data)} 字符")
                
                # 准备请求数据
                payload = {
                    "base64Data": data_url,
                    "uploadPath": "nano-banana-images",
                    "fileName": f"nano-edit-{os.path.basename(file_path)}"
                }
                
                headers = {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                }
                
                # 发送Base64上传请求
                response = requests.post(
                    f"{self.upload_base_url}/api/file-base64-upload",
                    json=payload,
                    headers=headers,
                    timeout=60
                )
                
                print(f"📊 Base64上传响应状态: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Base64上传成功: {result}")
                    
                    if result.get('success') and result.get('data'):
                        # 根据文档，使用downloadUrl字段
                        download_url = result['data'].get('downloadUrl')
                        if download_url:
                            print(f"🌐 公网文件URL: {download_url}")
                            return download_url
                        else:
                            print(f"❌ 响应中未找到downloadUrl")
                            return None
                    else:
                        print(f"❌ Base64上传失败: {result.get('msg', 'Unknown error')}")
                        return None
                else:
                    print(f"❌ Base64上传失败，HTTP状态码: {response.status_code}")
                    try:
                        error_info = response.json()
                        print(f"❌ 错误详情: {error_info}")
                    except:
                        print(f"❌ 响应内容: {response.text}")
                    return None
                    
        except Exception as e:
            print(f"❌ Base64上传异常: {e}")
            return None
    
    def test_connection(self) -> bool:
        """
        测试API连接
        
        Returns:
            连接是否成功
        """
        try:
            test_response = self.generate_content("你好")
            return test_response is not None
        except:
            return False


def create_gemini_api(api_key: str = "", use_mock: bool = False):
    """
    创建Nano-Banana API实例
    
    Args:
        api_key: API密钥
        use_mock: 是否使用模拟API
        
    Returns:
        API实例
    """
    if use_mock or not api_key:
        from tests.mock_api import MockGeminiAPI
        return MockGeminiAPI(api_key)
    else:
        return NanoBananaAPI(api_key)