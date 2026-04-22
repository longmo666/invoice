"""
智谱 OCR 专用客户端

两步识别流程：
  1. 上传文件到智谱 files API 获取 OCR 文本
  2. 用 chat completions 做结构化提取

与 UnifiedAIClient 的区别：
- 不走 builder/parser 多态体系（OCR 流程完全不同）
- 不走 http_helpers 的标准端点映射
- 需要额外的 ocr_chat_model 配置
"""
import httpx
import json
import time
import logging
from typing import Dict, Any, Optional
from app.services.recognition.provider_base import AIProviderClient, RecognitionError, TestConnectionResult, make_diagnostic_step
from app.services.ai.response_parsers import get_response_parser

logger = logging.getLogger(__name__)

# OCR 专用模型不支持 chat，结构化提取需要用通用文本模型
_ZHIPU_OCR_ONLY_MODELS = {"glm-ocr"}
_ZHIPU_FALLBACK_CHAT_MODEL = "glm-4-flash"


class ZhipuOCRClient(AIProviderClient):
    """智谱 OCR 专用客户端"""

    def __init__(self, ocr_chat_model: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.ocr_chat_model = ocr_chat_model

    def _get_chat_model(self) -> str:
        """获取结构化提取用的 chat 模型"""
        # 优先使用配置的 ocr_chat_model
        if self.ocr_chat_model:
            return self.ocr_chat_model
        # OCR 专用模型不支持 chat，回退到默认
        if self.model_name in _ZHIPU_OCR_ONLY_MODELS:
            logger.info(f"[ZhipuOCR] {self.model_name} 不支持 chat，结构化提取使用 {_ZHIPU_FALLBACK_CHAT_MODEL}")
            return _ZHIPU_FALLBACK_CHAT_MODEL
        return self.model_name

    async def recognize_invoice(
        self,
        image_data: bytes,
        invoice_type: str,
        prompt_template: str
    ) -> Dict[str, Any]:
        """识别发票（图片）— 走 OCR 两步流程"""
        return await self._ocr_recognize(image_data, "image", prompt_template)

    async def recognize_invoice_from_pdf(
        self,
        pdf_data: bytes,
        invoice_type: str,
        prompt_template: str
    ) -> Dict[str, Any]:
        """识别发票（PDF）— 走 OCR 两步流程"""
        return await self._ocr_recognize(pdf_data, "pdf", prompt_template)

    async def test_connection(self) -> TestConnectionResult:
        """
        测试连接 — 完整 3-hop 诊断：
        1. 上传文件到 files API
        2. 获取 OCR 文本（file content）
        3. chat completions 结构化提取
        """
        upload_url = f"{self.base_url}/api/paas/v4/files"
        diagnostic_steps: list[dict] = []
        overall_start = time.time()
        headers = {"Authorization": f"Bearer {self.api_key}"}
        # 维护当前步骤 URL，确保超时/通用异常能拿到真实失败跳
        current_step_url = upload_url

        # 生成带文字的测试图片（避免空白图片导致 OCR 无内容）
        try:
            from PIL import Image, ImageDraw
            import io
            img = Image.new("RGB", (200, 60), color="white")
            draw = ImageDraw.Draw(img)
            draw.text((10, 20), "Invoice Test 12345", fill="black")
            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            test_bytes = buf.getvalue()
        except Exception as e:
            return {
                "success": False,
                "message": f"生成测试图片失败: {e}",
                "latency_ms": None,
                "request_path": upload_url,
                "status_code": None,
                "diagnostic_steps": [],
            }

        file_id = None
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # ---- Step 1: upload ----
                step_start = time.time()
                resp = await client.post(
                    upload_url,
                    headers=headers,
                    files={"file": ("test.jpg", test_bytes, "image/jpeg")},
                    data={"purpose": "file-extract"},
                )
                step1_code = resp.status_code
                resp.raise_for_status()
                upload_result = resp.json()
                file_id = upload_result.get("id")
                step1_ms = int((time.time() - step_start) * 1000)
                diagnostic_steps.append(make_diagnostic_step(
                    step="upload_file", url=upload_url,
                    status_code=step1_code, latency_ms=step1_ms,
                    success=True, detail=f"file_id={file_id}",
                ))

                if not file_id:
                    diagnostic_steps[-1]["success"] = False
                    diagnostic_steps[-1]["detail"] = f"Files API 返回异常: {upload_result}"
                    _early_path = " → ".join(s.get("url", "") for s in diagnostic_steps if s.get("url")) or upload_url
                    return {
                        "success": False,
                        "message": f"Files API 返回异常: {upload_result}",
                        "latency_ms": int((time.time() - overall_start) * 1000),
                        "request_path": _early_path,
                        "status_code": step1_code,
                        "diagnostic_steps": diagnostic_steps,
                    }

                # ---- Step 2: get OCR content ----
                content_url = f"{self.base_url}/api/paas/v4/files/{file_id}/content"
                current_step_url = content_url
                step_start = time.time()
                content_resp = await client.get(content_url, headers=headers)
                step2_code = content_resp.status_code
                content_resp.raise_for_status()
                ocr_text = content_resp.json().get("content", "")
                step2_ms = int((time.time() - step_start) * 1000)
                diagnostic_steps.append(make_diagnostic_step(
                    step="get_ocr_content", url=content_url,
                    status_code=step2_code, latency_ms=step2_ms,
                    success=True, detail=f"OCR 文本长度: {len(ocr_text)}",
                ))

                # ---- Step 3: chat completions 结构化提取 ----
                chat_url = f"{self.base_url}/api/paas/v4/chat/completions"
                current_step_url = chat_url
                chat_model = self._get_chat_model()
                structurally_verified = False

                if ocr_text.strip():
                    # OCR 有内容：用 OCR 文本做最小结构化提取
                    chat_payload = {
                        "model": chat_model,
                        "temperature": self.temperature,
                        "max_tokens": 100,
                        "messages": [{
                            "role": "user",
                            "content": f"请从以下 OCR 文本中提取关键信息并以 JSON 返回：\n{ocr_text[:500]}",
                        }],
                    }
                    step_start = time.time()
                    chat_resp = await client.post(
                        chat_url,
                        headers={**headers, "Content-Type": "application/json"},
                        json=chat_payload,
                    )
                    step3_code = chat_resp.status_code
                    chat_resp.raise_for_status()
                    step3_ms = int((time.time() - step_start) * 1000)
                    structurally_verified = True
                    diagnostic_steps.append(make_diagnostic_step(
                        step="chat_completions", url=chat_url,
                        status_code=step3_code, latency_ms=step3_ms,
                        success=True, detail=f"结构化提取验证通过，chat model={chat_model}",
                    ))
                else:
                    # OCR 为空：显式跳过结构化验证，不降级为探活
                    diagnostic_steps.append(make_diagnostic_step(
                        step="chat_completions", url=chat_url,
                        success=True, detail="OCR 文本为空，跳过结构化验证",
                    ))

            total_ms = int((time.time() - overall_start) * 1000)
            # 聚合三步：request_path 串联所有 URL，status_code 取最后一步
            aggregated_path = " → ".join(s.get("url", "") for s in diagnostic_steps if s.get("url"))
            last_code = diagnostic_steps[-1].get("status_code") if diagnostic_steps else None
            skip_note = "" if structurally_verified else "，结构化验证被跳过（OCR 文本为空）"
            return {
                "success": True,
                "message": f"连接成功（OCR 3-hop，file_id={file_id}{skip_note}）",
                "latency_ms": total_ms,
                "request_path": aggregated_path,
                "status_code": last_code,
                "diagnostic_steps": diagnostic_steps,
            }

        except httpx.HTTPStatusError as e:
            sc = e.response.status_code
            failed_step = len(diagnostic_steps) + 1
            step_names = ["upload_file", "get_ocr_content", "chat_completions"]
            step_name = step_names[min(failed_step - 1, 2)]
            diagnostic_steps.append(make_diagnostic_step(
                step=step_name,
                url=str(e.request.url) if e.request else "",
                status_code=sc,
                success=False, detail=f"HTTP 错误: {sc} - {e.response.text[:200]}",
            ))
            _fail_path = " → ".join(s.get("url", "") for s in diagnostic_steps if s.get("url")) or upload_url
            _fail_code = diagnostic_steps[-1].get("status_code") if diagnostic_steps else sc
            return {
                "success": False,
                "message": f"第 {failed_step} 步失败: HTTP {sc}",
                "latency_ms": int((time.time() - overall_start) * 1000),
                "request_path": _fail_path,
                "status_code": _fail_code,
                "diagnostic_steps": diagnostic_steps,
            }
        except httpx.TimeoutException:
            failed_step = len(diagnostic_steps) + 1
            step_names = ["upload_file", "get_ocr_content", "chat_completions"]
            step_name = step_names[min(failed_step - 1, 2)]
            diagnostic_steps.append(make_diagnostic_step(
                step=step_name, url=current_step_url,
                success=False, detail=f"连接超时（{self.timeout}秒）",
            ))
            _fail_path = " → ".join(s.get("url", "") for s in diagnostic_steps if s.get("url")) or upload_url
            _fail_code = diagnostic_steps[-1].get("status_code") if diagnostic_steps else None
            return {
                "success": False,
                "message": f"第 {failed_step} 步超时",
                "latency_ms": int((time.time() - overall_start) * 1000),
                "request_path": _fail_path,
                "status_code": _fail_code,
                "diagnostic_steps": diagnostic_steps,
            }
        except Exception as e:
            failed_step = len(diagnostic_steps) + 1
            step_names = ["upload_file", "get_ocr_content", "chat_completions"]
            step_name = step_names[min(failed_step - 1, 2)]
            diagnostic_steps.append(make_diagnostic_step(
                step=step_name, url=current_step_url,
                success=False, detail=f"连接失败: {str(e)}",
            ))
            _fail_path = " → ".join(s.get("url", "") for s in diagnostic_steps if s.get("url")) or upload_url
            _fail_code = diagnostic_steps[-1].get("status_code") if diagnostic_steps else None
            return {
                "success": False,
                "message": f"第 {failed_step} 步失败: {str(e)}",
                "latency_ms": int((time.time() - overall_start) * 1000),
                "request_path": _fail_path,
                "status_code": _fail_code,
                "diagnostic_steps": diagnostic_steps,
            }

    # ==================== OCR 两步流程 ====================

    async def _ocr_recognize(
        self,
        file_data: bytes,
        file_type: str,
        prompt_template: str
    ) -> Dict[str, Any]:
        """
        智谱 OCR 三步识别（含结构化诊断）：
        1. 上传文件 → 获取 file_id
        2. 获取 OCR 文本
        3. chat completions 结构化提取

        失败时抛 RecognitionError，携带已完成步骤的 diagnostic_steps。
        """
        headers = {"Authorization": f"Bearer {self.api_key}"}
        diagnostic_steps: list = []
        # 维护当前步骤上下文，确保兜底异常能拿到真实 URL
        current_step_name = "upload_file"
        current_step_url = f"{self.base_url}/api/paas/v4/files"

        if file_type == "pdf":
            filename, mime_type = "invoice.pdf", "application/pdf"
        else:
            filename, mime_type = "invoice.jpg", "image/jpeg"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Step 1: 上传文件
                upload_url = current_step_url
                step_start = time.time()
                upload_resp = await client.post(
                    upload_url,
                    headers=headers,
                    files={"file": (filename, file_data, mime_type)},
                    data={"purpose": "file-extract"}
                )
                upload_resp.raise_for_status()
                file_id = upload_resp.json()["id"]
                step_ms = int((time.time() - step_start) * 1000)
                diagnostic_steps.append(make_diagnostic_step(
                    step="upload_file", url=upload_url,
                    status_code=upload_resp.status_code, latency_ms=step_ms,
                    success=True, detail=f"file_id={file_id}",
                ))
                logger.info(f"[ZhipuOCR] 文件上传成功: file_id={file_id}")

                # Step 2: 获取 OCR 文本
                content_url = f"{self.base_url}/api/paas/v4/files/{file_id}/content"
                current_step_name = "get_ocr_content"
                current_step_url = content_url
                step_start = time.time()
                content_resp = await client.get(content_url, headers=headers)
                content_resp.raise_for_status()
                ocr_text = content_resp.json().get("content", "")
                step_ms = int((time.time() - step_start) * 1000)
                diagnostic_steps.append(make_diagnostic_step(
                    step="get_ocr_content", url=content_url,
                    status_code=content_resp.status_code, latency_ms=step_ms,
                    success=True, detail=f"OCR 文本长度: {len(ocr_text)}",
                ))
                logger.info(f"[ZhipuOCR] OCR 文本长度: {len(ocr_text)}")

                if not ocr_text.strip():
                    diagnostic_steps[-1]["success"] = False
                    diagnostic_steps[-1]["detail"] = "OCR 未识别到任何文本内容"
                    raise RecognitionError("OCR 未识别到任何文本内容", diagnostic_steps)

                # Step 3: chat completions 结构化提取
                structured_prompt = f"{prompt_template}\n\n以下是 OCR 识别出的原始文本：\n{ocr_text}"
                chat_url = f"{self.base_url}/api/paas/v4/chat/completions"
                current_step_name = "chat_completions"
                current_step_url = chat_url
                chat_model = self._get_chat_model()
                chat_payload = {
                    "model": chat_model,
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                    "messages": [{"role": "user", "content": structured_prompt}]
                }

                step_start = time.time()
                chat_resp = await client.post(
                    chat_url,
                    headers={**headers, "Content-Type": "application/json"},
                    json=chat_payload
                )
                chat_resp.raise_for_status()
                chat_result = chat_resp.json()
                step_ms = int((time.time() - step_start) * 1000)
                diagnostic_steps.append(make_diagnostic_step(
                    step="chat_completions", url=chat_url,
                    status_code=chat_resp.status_code, latency_ms=step_ms,
                    success=True, detail=f"chat model={chat_model}",
                ))

            # 用智谱 chat completions 解析器解析结果
            response_parser = get_response_parser("zhipu_chat_completions")
            standard_response = response_parser.parse(chat_result)
            content = self._extract_json_content(standard_response.content)
            parsed_result = json.loads(content)

            return {
                "raw_response": {"ocr_text": ocr_text, "chat_response": chat_result},
                "parsed_result": parsed_result,
                "model": standard_response.model,
                "usage": standard_response.usage,
                "diagnostic_steps": diagnostic_steps,
            }

        except RecognitionError:
            raise  # 已携带 diagnostic_steps，直接上抛
        except Exception as e:
            # 给当前失败步骤补一条记录，使用维护的步骤上下文
            failed_url = str(e.request.url) if isinstance(e, httpx.HTTPStatusError) and e.request else current_step_url
            failed_step_idx = len(diagnostic_steps)
            step_names = ["upload_file", "get_ocr_content", "chat_completions"]
            if failed_step_idx < len(step_names):
                diagnostic_steps.append(make_diagnostic_step(
                    step=step_names[failed_step_idx], url=failed_url,
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
