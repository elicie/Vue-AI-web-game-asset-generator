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
import logging
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)


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
        
        logger.info("🍌 使用Nano-Banana API - 图像生成: kie.ai平台")
    
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
    
    @staticmethod
    def _extract_output_url(output) -> Optional[str]:
        """Extract a URL string from various API output formats.

        The upstream API may return the image as:
          - a bare HTTP URL string
          - a data:image/... base64 data-URL string
          - a dict {"url": "..."}

        Returns the URL/data-URL string, or None if the format is unrecognized.
        """
        if isinstance(output, str):
            if output.startswith('http') or output.startswith('data:image/'):
                return output
        elif isinstance(output, dict) and "url" in output:
            return output["url"]
        return None

    @staticmethod
    def _log_error_advice(error_msg: str) -> None:
        """Log contextual advice for common API error patterns."""
        lower = error_msg.lower()
        if "unauthorized" in lower or "401" in error_msg:
            logger.info("💡 解决建议: 检查API密钥是否正确且有权限")
        elif "quota" in lower or "429" in error_msg:
            logger.info("💡 配额限制: 请等待配额重置或升级账户")
        elif "timeout" in lower:
            logger.info("💡 网络问题: 网络连接超时，请检查网络状况")

    def generate_image_with_nano_banana(self, prompt: str, num_images: int = 1, 
                                      output_format: str = "png", 
                                      image_size: str = "auto",
                                      aspect_ratio: str = "auto") -> Optional[List[str]]:
        """
        使用Nano-Banana API生成图像
        
        Args:
            prompt: 图像描述提示词
            num_images: 生成图像数量（1-4张）
            output_format: 输出格式 ("png" 或 "jpeg")
            image_size: 图像尺寸 ("auto", "1:1", "3:4", "9:16", "4:3", "16:9")
            aspect_ratio: 图像比例 ("auto", "1:1", "9:16", "16:9", "3:4", "4:3", "3:2", "2:3", "5:4", "4:5")
            
        Returns:
            生成的图像URL列表，失败返回None
        """
        try:
            # 限制图像数量
            num_images = max(1, min(4, num_images))
            
            enhanced_prompt = prompt
            
            logger.info("🍌 使用Nano-Banana API生成%d张图像: %s", num_images, enhanced_prompt)
            
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
            logger.debug("📐 图像比例: %s -> %s", aspect_ratio, final_image_size)
            
            logger.debug("🔍 完整payload: %s", json.dumps(payload, indent=2, ensure_ascii=False))
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            images = []
            
            # 为每张图像发送请求
            for i in range(num_images):
                logger.info("🚀 正在生成第 %d/%d 张图像...", i+1, num_images)
                
                # 按照官方示例发送请求
                response = requests.post(
                    f"{self.base_url}{self.create_task_endpoint}",
                    headers=headers,
                    data=json.dumps(payload),
                    timeout=60
                )
                
                logger.debug("📊 API响应状态(generate): %d", response.status_code)
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info("✅ 任务创建成功: %s", result)
                    
                    # 检查API是否支持我们的config格式
                    if "error" in result or "message" in result:
                        logger.warning("⚠️ API可能不支持当前格式: %s", result)
                    
                    if "data" in result:
                        task_data = result["data"]
                        
                        # 如果直接返回了图像结果
                        if "output" in task_data:
                            url = self._extract_output_url(task_data["output"])
                            if url:
                                images.append(url)
                                logger.info("✅ 成功获取图像URL %s", i+1)
                        
                        # 如果需要轮询任务状态
                        elif "taskId" in task_data or "recordId" in task_data:
                            task_id = task_data.get("taskId") or task_data.get("recordId")
                            logger.debug("🔄 任务ID: %s, 轮询任务状态...", task_id)

                            result_urls = self._poll_task_result(task_id)
                            if result_urls:
                                for url in result_urls:
                                    images.append(url)
                                    logger.info("✅ 成功获取图像URL %s: %s", i+1, url)
                elif response.status_code == 401:
                    logger.error("❌ 认证失败: API密钥无效或没有权限")
                    logger.debug("详细信息: %s", response.text)
                    break
                elif response.status_code == 400:
                    logger.error("❌ 请求参数错误: %s", response.text)
                    break
                else:
                    logger.error("❌ API请求失败: %s", response.status_code)
                    logger.debug("详细信息: %s", response.text)
                    break
            
            return images if images else None
            
        except Exception as e:
            error_msg = str(e)
            logger.error("❌ Nano-Banana图像生成失败: %s", error_msg)
            
            self._log_error_advice(error_msg)
            
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
            
            logger.debug("🎨 使用Nano-Banana Edit API编辑图像: %s", enhanced_prompt)
            logger.debug("📥 输入图像: %s", input_image_url[:100] + "..." if len(input_image_url) > 100 else input_image_url)
            
            if mask_image_url:
                logger.debug("🎯 遮罩图像: %s", mask_image_url[:100] + "..." if len(mask_image_url) > 100 else mask_image_url)
            
            # 如果是中文指令，尝试简单翻译为英文
            english_prompt = self._translate_to_english(prompt)
            if english_prompt != prompt:
                logger.debug("🌐 指令翻译: %s -> %s", prompt, english_prompt)
            
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
            
            logger.debug("🚀 正在编辑图像...")
            
            # 按照官方示例发送请求
            response = requests.post(
                f"{self.base_url}{self.create_task_endpoint}",
                headers=headers,
                data=json.dumps(payload),
                timeout=60
            )
            
            logger.debug("📊 API响应状态: %s", response.status_code)
            
            if response.status_code == 200:
                result = response.json()
                logger.info("✅ 任务创建成功: %s", result)
                
                # 首先检查API返回的code字段
                if result.get("code") != 200:
                    # API返回了错误
                    error_msg = result.get("msg", "未知错误")
                    error_code = result.get("code", "")
                    logger.error("❌ API返回错误: [%s] %s", error_code, error_msg)
                    return f"ERROR: [{error_code}] {error_msg}"
                
                # 检查任务状态和结果
                if "data" in result:
                    task_data = result["data"]
                    
                    # 如果直接返回了图像结果
                    if "output" in task_data:
                        url = self._extract_output_url(task_data["output"])
                        if url:
                            logger.info("✅ 成功获取编辑图像URL: %s", url)
                            return url
                    
                    # 如果需要轮询任务状态
                    elif "taskId" in task_data or "recordId" in task_data:
                        task_id = task_data.get("taskId") or task_data.get("recordId")
                        logger.debug("🔄 任务ID: %s, 轮询任务状态...", task_id)

                        result_urls = self._poll_task_result(task_id)
                        if result_urls:
                            image_url = result_urls[0]
                            logger.info("✅ 成功获取编辑图像URL: %s", image_url)
                            return image_url

            elif response.status_code == 401:
                logger.error("❌ 认证失败: API密钥无效或没有权限")
                logger.debug("详细信息: %s", response.text)
            elif response.status_code == 400:
                logger.error("❌ 请求参数错误: %s", response.text)
            else:
                logger.error("❌ API请求失败: %s", response.status_code)
                logger.debug("详细信息: %s", response.text)
            
            return None
            
        except Exception as e:
            error_msg = str(e)
            logger.error("❌ Nano-Banana图像编辑失败: %s", error_msg)
            
            self._log_error_advice(error_msg)
            
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
                    logger.debug("🔄 第%s次查询，API响应码: %s", retry+1, status_result.get('code', 'unknown'))

                    if status_result.get("code") == 200 and "data" in status_result:
                        data = status_result["data"]
                        current_state = data.get("state", "unknown")
                        logger.debug("📋 任务状态: %s", current_state)

                        if current_state == "success":
                            if "resultJson" in data and data["resultJson"]:
                                try:
                                    result_json = json.loads(data["resultJson"])
                                    logger.debug("🎯 解析结果: %s", result_json)

                                    if "resultUrls" in result_json and result_json["resultUrls"]:
                                        return result_json["resultUrls"]
                                    else:
                                        logger.warning("⚠️ resultJson中没有找到resultUrls")
                                except json.JSONDecodeError as e:
                                    logger.error("❌ 解析resultJson失败: %s", e)
                                    logger.debug("原始resultJson: %s", data.get('resultJson', 'None'))
                            else:
                                logger.warning("⚠️ 任务成功但没有resultJson")
                            return None

                        elif current_state == "fail":
                            fail_msg = data.get("failMsg", "未知错误")
                            fail_code = data.get("failCode", "")
                            logger.error("❌ 任务失败: [%s] %s", fail_code, fail_msg)
                            return None

                        elif current_state in ["waiting", "processing", "pending", "running", "generating"]:
                            logger.debug("⏳ 任务仍在处理中... (%s/%s)", retry+1, max_retries)
                            continue
                        else:
                            logger.debug("🔄 未知任务状态: %s", current_state)
                    else:
                        logger.error("❌ API响应错误: 代码=%s, 消息=%s", status_result.get('code'), status_result.get('message'))
                else:
                    logger.error("❌ 查询任务状态失败: %s - %s", status_response.status_code, status_response.text[:100])

            except Exception as e:
                logger.error("❌ 查询异常: %s", e)

        logger.warning("⚠️ 任务超时，请稍后手动检查")
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
            logger.debug("📤 Base64上传文件到KIE.ai: %s", file_path)
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                logger.error("❌ 文件不存在: %s", file_path)
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
                
                logger.debug("📊 Base64数据长度: %s 字符", len(base64_data))
                
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
                
                logger.debug("📊 Base64上传响应状态: %s", response.status_code)
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info("✅ Base64上传成功: %s", result)
                    
                    if result.get('success') and result.get('data'):
                        # 根据文档，使用downloadUrl字段
                        download_url = result['data'].get('downloadUrl')
                        if download_url:
                            logger.debug("🌐 公网文件URL: %s", download_url)
                            return download_url
                        else:
                            logger.error("❌ 响应中未找到downloadUrl")
                            return None
                    else:
                        logger.error("❌ Base64上传失败: %s", result.get('msg', 'Unknown error'))
                        return None
                else:
                    logger.error("❌ Base64上传失败，HTTP状态码: %s", response.status_code)
                    try:
                        error_info = response.json()
                        logger.error("❌ 错误详情: %s", error_info)
                    except (ValueError, KeyError):
                        logger.error("❌ 响应内容: %s", response.text)
                    return None
                    
        except Exception as e:
            logger.error("❌ Base64上传异常: %s", e)
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
        except Exception:
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