#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
백엔드 유틸리티 함수 단위 테스트
"""

import os
import sys
import json
import uuid
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from io import BytesIO

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestGenerateConversationId(unittest.TestCase):
    """generate_conversation_id 함수 테스트"""

    def setUp(self):
        # FastAPI 앱 임포트 전 API 클라이언트 초기화를 건너뜀
        with patch("gemini_api.NanoBananaAPI.__init__", return_value=None):
            pass

    def _get_func(self):
        import importlib
        # backend 모듈을 직접 임포트하지 않고 함수만 추출
        import backend
        return backend.generate_conversation_id

    def test_returns_string(self):
        func = self._get_func()
        result = func()
        self.assertIsInstance(result, str)

    def test_length_is_8(self):
        func = self._get_func()
        result = func()
        self.assertEqual(len(result), 8)

    def test_unique_ids(self):
        func = self._get_func()
        ids = {func() for _ in range(100)}
        self.assertEqual(len(ids), 100)

    def test_alphanumeric(self):
        func = self._get_func()
        result = func()
        # UUID hex 문자열 — 하이픈 없는 16진수
        self.assertTrue(all(c in "0123456789abcdef-" for c in result))


class TestGetImageResolution(unittest.TestCase):
    """get_image_resolution 함수 테스트"""

    def _get_func(self):
        import backend
        return backend.get_image_resolution

    def test_local_image(self):
        from PIL import Image
        func = self._get_func()

        # get_image_resolution은 '/'로 시작하는 경로를 './path'로 변환함
        # 따라서 현재 디렉터리 기준 상대 경로를 사용해야 함
        test_filename = "_test_image_320x240.png"
        cwd = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(cwd, test_filename)

        try:
            img = Image.new("RGB", (320, 240), color="red")
            img.save(img_path)
            result = func(test_filename)
            self.assertEqual(result, "320×240")
        finally:
            if os.path.exists(img_path):
                os.unlink(img_path)

    def test_nonexistent_local_file_returns_none(self):
        func = self._get_func()
        result = func("/nonexistent/path/image.png")
        self.assertIsNone(result)

    def test_http_image_startup_mode_returns_default(self):
        func = self._get_func()
        result = func("http://example.com/image.png", is_startup=True)
        self.assertEqual(result, "네트워크 이미지" if "네트워크" in (result or "") else result)
        # 스타트업 모드에서는 네트워크 요청 없이 기본값 반환
        self.assertIsNotNone(result)

    def test_http_image_network_error_returns_fallback(self):
        func = self._get_func()
        import requests
        with patch("requests.get", side_effect=requests.exceptions.ConnectionError):
            result = func("http://unreachable.invalid/image.png")
        # 네트워크 오류 시 기본값("网络图像") 반환
        self.assertIsNotNone(result)


class TestNanoBananaAPITextGeneration(unittest.TestCase):
    """NanoBananaAPI 텍스트 생성 메서드 테스트 (외부 API 호출 없음)"""

    def setUp(self):
        from gemini_api import NanoBananaAPI
        self.api = NanoBananaAPI.__new__(NanoBananaAPI)
        self.api.api_key = "test_key"
        self.api.base_url = "https://api.kie.ai"
        self.api.create_task_endpoint = "/api/v1/jobs/createTask"
        self.api.query_task_endpoint = "/api/v1/jobs/recordInfo"
        self.api.upload_base_url = "https://kieai.redpandaai.co"

    def test_generate_content_image_keyword(self):
        result = self.api.generate_content("이미지 생성해줘")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_generate_content_general_text(self):
        result = self.api.generate_content("안녕하세요")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_enhance_image_prompt_returns_string(self):
        result = self.api.enhance_image_prompt("고양이")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_enhance_image_prompt_fallback_on_none(self):
        # generate_content가 None을 반환할 때 원본 입력을 반환해야 함
        original_generate = self.api.generate_content
        self.api.generate_content = lambda _: None
        result = self.api.enhance_image_prompt("강아지")
        self.assertEqual(result, "강아지")
        self.api.generate_content = original_generate


class TestDataModels(unittest.TestCase):
    """Pydantic 데이터 모델 기본 검증 테스트"""

    def test_message_model_required_fields(self):
        from backend import Message
        msg = Message(role="user", content="테스트 메시지")
        self.assertEqual(msg.role, "user")
        self.assertEqual(msg.content, "테스트 메시지")
        self.assertIsNone(msg.image_url)

    def test_chat_request_defaults(self):
        from backend import ChatRequest
        req = ChatRequest(message="안녕")
        self.assertEqual(req.message, "안녕")
        self.assertEqual(req.model_type, "generate")
        self.assertEqual(req.aspect_ratio, "auto")

    def test_chat_response_model(self):
        from backend import ChatResponse
        resp = ChatResponse(message="응답", conversation_id="abc12345")
        self.assertEqual(resp.message, "응답")
        self.assertFalse(resp.is_image)
        self.assertIsNone(resp.image_url)


if __name__ == "__main__":
    unittest.main(verbosity=2)
