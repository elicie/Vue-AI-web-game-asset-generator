#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mock Gemini API for testing purposes.
Extracted from gemini_api.py to avoid shipping test code in production.
"""

from typing import List, Dict, Optional
import random


class MockGeminiAPI:
    """模拟Gemini API（用于测试）"""
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        print("使用模拟Gemini API（测试模式）")
    
    def generate_content(self, text: str, conversation_history: Optional[List[Dict]] = None) -> str:
        """模拟文本生成"""
        if "图" in text or "image" in text.lower() or "画" in text:
            return f"我理解您想要生成关于'{text[:20]}'的图像。这是一个很有有趣的想法！"
        else:
            responses = [
                f"您好！我收到了您的消息：'{text[:30]}...'，这是一个模拟回复。",
                f"非常有趣的问题！关于'{text[:20]}'，我可以给您一些建议。",
                f"谢谢您的问题。对于'{text[:20]}'，这确实是一个值得思考的话题。"
            ]
            return random.choice(responses)
    
    def enhance_image_prompt(self, user_input: str) -> str:
        """模拟提示词优化"""
        enhancements = {
            "猫": "a cute cat, high quality, detailed, beautiful",
            "狗": "a beautiful dog, high quality, detailed, adorable", 
            "风景": "beautiful landscape, high quality, detailed, scenic",
            "城市": "futuristic city, high quality, detailed, cyberpunk",
            "花": "beautiful flowers, high quality, detailed, colorful",
            "山": "majestic mountains, high quality, detailed, scenic",
            "海": "ocean waves, high quality, detailed, serene"
        }
        
        for key, value in enhancements.items():
            if key in user_input:
                return value
        
        return f"{user_input}, high quality, detailed, beautiful"
    
    def test_connection(self) -> bool:
        """模拟连接测试"""
        return True
    
    def generate_image_with_nano_banana(self, prompt: str, num_images: int = 1, 
                                       output_format: str = "png", 
                                       image_size: str = "auto",
                                       aspect_ratio: str = "auto") -> List[str]:
        """模拟Nano-Banana图像生成"""
        urls = []
        num_images = max(1, min(4, num_images))
        
        for i in range(num_images):
            mock_url = f"https://mock-generate-result.com/gen_{hash(prompt + str(i)) % 10000}.png"
            urls.append(mock_url)
        
        return urls
    
    def edit_image_with_nano_banana(self, prompt: str, input_image_url: str, 
                                   output_format: str = "png", 
                                   image_size: str = "auto",
                                   aspect_ratio: str = "auto") -> str:
        """模拟Nano-Banana图像编辑"""
        from PIL import Image
        
        print(f"🎨 模拟Nano-Banana编辑图像: {prompt}")
        print(f"📥 输入图像: {input_image_url}")
        
        width, height = 512, 512
        img = Image.new('RGB', (width, height))
        pixels = []
        
        base_color = hash(prompt + input_image_url) % 256
        
        for y in range(height):
            for x in range(width):
                r = (base_color + x // 3) % 256
                g = (base_color + y // 3) % 256  
                b = (base_color + (x + y) // 6) % 256
                pixels.append((r, g, b))
        
        img.putdata(pixels)
        
        mock_url = f"https://mock-edit-result.com/edited_{hash(prompt + input_image_url) % 10000}.png"
        print(f"✅ 模拟Nano-Banana编辑完成: {width}x{height}")
        print(f"📤 模拟编辑结果URL: {mock_url}")
        
        return mock_url
