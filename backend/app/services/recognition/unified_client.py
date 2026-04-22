"""
统一 AI 客户端

使用共享 AI 基础设施（services/ai/）实现统一的 AI 调用接口。
支持 OpenAI / Anthropic / Gemini / 智谱 等多种 API 风格。

职责边界：
- 本文件属于 recognition 业务层，负责发票识别的 AI 调用编排
- 请求构建、响应解析、URL/Header 构造全部委托给 services/ai/ 共享层
"""
import httpx
import json
import time
from typing import Dict, Any, Optional
from app.services.recognition.provider_base import AIProviderClient, RecognitionError, TestConnectionResult, make_diagnostic_step
from app.services.ai.request_builders import get_request_builder
from app.services.ai.response_parsers import get_response_parser
from app.services.ai.transport import TransportMode
from app.services.ai.http_helpers import build_auth_headers, get_api_endpoint, build_full_url


class UnifiedAIClient(AIProviderClient):
    """统一 AI 客户端（支持所有 API 风格）"""

    async def recognize_invoice(
        self,
        image_data: bytes,
        invoice_type: str,
        prompt_template: str
    ) -> Dict[str, Any]:
        """识别发票（图片）"""
        request_builder = get_request_builder(self.api_style)
        payload = request_builder.build_request(
            prompt=prompt_template,
            transport_mode=TransportMode.MULTIMODAL_IMAGE,
            image_data=image_data,
            model_name=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        return await self._send_and_parse(payload)

    async def recognize_invoice_from_pdf(
        self,
        pdf_data: bytes,
        invoice_type: str,
        prompt_template: str
    ) -> Dict[str, Any]:
        """识别发票（PDF 直传）"""
        request_builder = get_request_builder(self.api_style)
        try:
            payload = request_builder.build_request(
                prompt=prompt_template,
                transport_mode=TransportMode.DOCUMENT_FILE,
                file_data=pdf_data,
                file_name="invoice.pdf",
                model_name=self.model_name,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
        except NotImplementedError as e:
            raise NotImplementedError(f"{self.api_style} 不支持 PDF 直传识别") from e
        return await self._send_and_parse(payload)

    async def test_connection(self) -> TestConnectionResult:
        """测试连接 — 返回结构化 dict（含单步 diagnostic）"""
        request_path = None
        status_code = None
        diagnostic_steps = []
        try:
            start_time = time.time()
            request_builder = get_request_builder(self.api_style)
            response_parser = get_response_parser(self.api_style)

            payload = request_builder.build_request(
                prompt="Hello",
                transport_mode=TransportMode.TEXT_ONLY,
                model_name=self.model_name,
                temperature=self.temperature,
                max_tokens=10
            )

            request_path = self._build_full_url()
            headers = self._build_headers()

            step_start = time.time()
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(request_path, headers=headers, json=payload)
                status_code = response.status_code
                response.raise_for_status()
                result = response.json()

            response_parser.parse(result)
            step_ms = int((time.time() - step_start) * 1000)
            diagnostic_steps.append(make_diagnostic_step(
                step="chat_completions", url=request_path,
                status_code=status_code, latency_ms=step_ms,
                success=True, detail="连接成功",
            ))

            latency_ms = int((time.time() - start_time) * 1000)
            return {
                "success": True,
                "message": "连接成功",
                "latency_ms": latency_ms,
                "request_path": request_path,
                "status_code": status_code,
                "diagnostic_steps": diagnostic_steps,
            }

        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            diagnostic_steps.append(make_diagnostic_step(
                step="chat_completions", url=request_path,
                status_code=status_code,
                success=False, detail=f"HTTP 错误: {status_code} - {e.response.text}",
            ))
            return {
                "success": False,
                "message": f"HTTP 错误: {status_code} - {e.response.text}",
                "latency_ms": None,
                "request_path": request_path,
                "status_code": status_code,
                "diagnostic_steps": diagnostic_steps,
            }
        except httpx.TimeoutException:
            diagnostic_steps.append(make_diagnostic_step(
                step="chat_completions", url=request_path,
                success=False, detail=f"连接超时（{self.timeout}秒）",
            ))
            return {
                "success": False,
                "message": f"连接超时（{self.timeout}秒）",
                "latency_ms": None,
                "request_path": request_path,
                "status_code": status_code,
                "diagnostic_steps": diagnostic_steps,
            }
        except Exception as e:
            diagnostic_steps.append(make_diagnostic_step(
                step="chat_completions", url=request_path,
                status_code=status_code,
                success=False, detail=f"连接失败: {str(e)}",
            ))
            return {
                "success": False,
                "message": f"连接失败: {str(e)}",
                "latency_ms": None,
                "request_path": request_path,
                "status_code": status_code,
                "diagnostic_steps": diagnostic_steps,
            }

    # ==================== 内部方法（委托给共享层） ====================

    async def _send_and_parse(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """发送请求并解析响应为标准结果（含单步 diagnostic）
        失败时抛 RecognitionError，携带已完成步骤的 diagnostic_steps。
        """
        response_parser = get_response_parser(self.api_style)
        headers = self._build_headers()
        url = self._build_full_url()
        diagnostic_steps = []

        try:
            step_start = time.time()
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=payload)
                status_code = response.status_code
                response.raise_for_status()
                result = response.json()

            step_ms = int((time.time() - step_start) * 1000)
            standard_response = response_parser.parse(result)
            content = self._extract_json_content(standard_response.content)
            parsed_result = json.loads(content)

            diagnostic_steps.append(make_diagnostic_step(
                step="chat_completions", url=url,
                status_code=status_code, latency_ms=step_ms,
                success=True, detail=f"model={standard_response.model}",
            ))

            return {
                "raw_response": result,
                "parsed_result": parsed_result,
                "model": standard_response.model,
                "usage": standard_response.usage,
                "diagnostic_steps": diagnostic_steps,
            }

        except RecognitionError:
            raise
        except Exception as e:
            diagnostic_steps.append(make_diagnostic_step(
                step="chat_completions", url=url,
                status_code=getattr(getattr(e, "response", None), "status_code", None),
                success=False, detail=str(e)[:300],
            ))
            raise RecognitionError(str(e), diagnostic_steps) from e

    @staticmethod
    def _extract_json_content(raw_content: str) -> str:
        """移除 markdown 代码块包裹，提取纯 JSON"""
        content = raw_content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        return content.strip()

    def _build_headers(self) -> Dict[str, str]:
        """构造请求头（委托给共享层）"""
        return build_auth_headers(self.provider_vendor, self.api_key)

    def _get_endpoint(self) -> str:
        """获取 API 端点路径（委托给共享层）"""
        return get_api_endpoint(self.api_style, self.model_name)

    def _build_full_url(self) -> str:
        """构造完整请求 URL（委托给共享层）"""
        return build_full_url(self.base_url, self.api_style, self.model_name, self.provider_vendor, self.api_key)
