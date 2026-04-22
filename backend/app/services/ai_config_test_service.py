"""
AI 配置样本测试服务

职责：接收管理员上传的样本文件，调用 AI 识别并返回测试结果。
URL 构造通过共享层 http_helpers 完成。
zhipu_ocr 走独立流程，不经过标准端点映射。
"""
import json
import time
from typing import Dict, Any
from sqlalchemy.orm import Session
from fastapi import UploadFile

from app.models.ai_config_test_run import AIConfigTestRun
from app.repositories.ai_config import AIConfigRepository
from app.services.recognition.provider_factory import ProviderClientFactory
from app.services.recognition.pdf_strategy_runner import PDFStrategyRunner
from app.services.recognition.prompts import get_prompt_template
from app.services.ai.http_helpers import get_api_endpoint
from app.core.exceptions import NotFoundException, ValidationException
from app.services.recognition.provider_base import RecognitionError


def _resolve_request_path(config) -> str:
    """根据 api_style 构造请求路径（zhipu_ocr 走 files API，其他走标准端点）"""
    if config.api_style == "zhipu_ocr":
        return f"{config.base_url}/api/paas/v4/files"
    return f"{config.base_url}{get_api_endpoint(config.api_style, config.model_name)}"


class AIConfigTestService:
    """AI 配置样本测试服务"""

    def __init__(self, db: Session):
        self.db = db
        self.config_repo = AIConfigRepository(db)

    def _create_client(self, config):
        """从配置创建 AI 客户端（统一传 ocr_chat_model）"""
        return ProviderClientFactory.create_client(
            provider_vendor=config.provider_vendor,
            api_style=config.api_style,
            base_url=config.base_url,
            api_key=config.api_key,
            model_name=config.model_name,
            timeout=config.timeout,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            ocr_chat_model=getattr(config, 'ocr_chat_model', None),
        )

    async def test_image_sample(
        self,
        config_id: int,
        user_id: int,
        file: UploadFile,
        invoice_type: str
    ) -> Dict[str, Any]:
        """测试图片样本"""
        config = self.config_repo.get_by_id(config_id)
        if not config:
            raise NotFoundException("配置不存在")

        file_data = await file.read()
        file_name = file.filename
        prompt_template = get_prompt_template(invoice_type, config.provider_vendor)
        client = self._create_client(config)

        start_time = time.time()
        request_path = _resolve_request_path(config)
        execution_path = "image_single"

        try:
            result = await client.recognize_invoice(
                image_data=file_data,
                invoice_type=invoice_type,
                prompt_template=prompt_template
            )

            latency_ms = int((time.time() - start_time) * 1000)

            _steps = result.get("diagnostic_steps", [])
            _last_code = _steps[-1].get("status_code") if _steps else None
            _actual_path = " → ".join(s.get("url", "") for s in _steps if s.get("url")) or request_path
            test_run = AIConfigTestRun(
                config_id=config_id,
                tester_user_id=user_id,
                file_name=file_name,
                file_type="image",
                invoice_type=invoice_type,
                test_mode="image_single",
                tested_strategy=None,
                success=True,
                request_path=_actual_path,
                execution_path=execution_path,
                latency_ms=latency_ms,
                error_message=None,
                raw_response=json.dumps(result.get("raw_response"), ensure_ascii=False),
                parsed_result=json.dumps(result.get("parsed_result"), ensure_ascii=False),
                status_code=_last_code,
                diagnostic_steps=json.dumps(_steps, ensure_ascii=False),
            )
            self.db.add(test_run)
            self.db.commit()

            return {
                "test_mode": "image_single",
                "file_name": file_name,
                "file_type": "image",
                "invoice_type": invoice_type,
                "result": {
                    "success": True,
                    "strategy": None,
                    "latency_ms": latency_ms,
                    "request_path": _actual_path,
                    "execution_path": execution_path,
                    "status_code": _last_code,
                    "error_message": None,
                    "raw_response": result.get("raw_response"),
                    "structured_result": result.get("parsed_result"),
                    "diagnostic_steps": result.get("diagnostic_steps", []),
                }
            }

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)

            fail_steps = e.diagnostic_steps if isinstance(e, RecognitionError) else []
            _fail_code = fail_steps[-1].get("status_code") if fail_steps else None
            _fail_path = " → ".join(s.get("url", "") for s in fail_steps if s.get("url")) or request_path
            test_run = AIConfigTestRun(
                config_id=config_id,
                tester_user_id=user_id,
                file_name=file_name,
                file_type="image",
                invoice_type=invoice_type,
                test_mode="image_single",
                tested_strategy=None,
                success=False,
                request_path=_fail_path,
                execution_path=execution_path,
                latency_ms=latency_ms,
                error_message=str(e),
                raw_response=None,
                parsed_result=None,
                status_code=_fail_code,
                diagnostic_steps=json.dumps(fail_steps, ensure_ascii=False),
            )
            self.db.add(test_run)
            self.db.commit()

            return {
                "test_mode": "image_single",
                "file_name": file_name,
                "file_type": "image",
                "invoice_type": invoice_type,
                "result": {
                    "success": False,
                    "strategy": None,
                    "latency_ms": latency_ms,
                    "request_path": _fail_path,
                    "execution_path": execution_path,
                    "status_code": _fail_code,
                    "error_message": str(e),
                    "raw_response": None,
                    "structured_result": None,
                    "diagnostic_steps": fail_steps,
                }
            }

    async def test_pdf_sample(
        self,
        config_id: int,
        user_id: int,
        file: UploadFile,
        invoice_type: str
    ) -> Dict[str, Any]:
        """测试 PDF 样本（自动双策略对比）"""
        config = self.config_repo.get_by_id(config_id)
        if not config:
            raise NotFoundException("配置不存在")

        file_data = await file.read()
        file_name = file.filename
        prompt_template = get_prompt_template(invoice_type, config.provider_vendor)
        client = self._create_client(config)

        runner = PDFStrategyRunner(client)

        comparison = await runner.run_both_strategies(
            pdf_data=file_data,
            invoice_type=invoice_type,
            prompt_template=prompt_template
        )

        direct_result = comparison["direct_pdf_result"]
        _d_steps = direct_result.get("diagnostic_steps", [])
        _d_code = _d_steps[-1].get("status_code") if _d_steps else None
        test_run_direct = AIConfigTestRun(
            config_id=config_id,
            tester_user_id=user_id,
            file_name=file_name,
            file_type="pdf",
            invoice_type=invoice_type,
            test_mode="pdf_compare",
            tested_strategy="direct_pdf",
            success=direct_result["success"],
            request_path=direct_result["request_path"],
            execution_path=direct_result["execution_path"],
            latency_ms=direct_result["latency_ms"],
            error_message=direct_result["error_message"],
            raw_response=json.dumps(direct_result["raw_response"], ensure_ascii=False) if direct_result["raw_response"] else None,
            parsed_result=json.dumps(direct_result["structured_result"], ensure_ascii=False) if direct_result["structured_result"] else None,
            status_code=_d_code,
            diagnostic_steps=json.dumps(_d_steps, ensure_ascii=False),
        )
        self.db.add(test_run_direct)

        convert_result = comparison["convert_to_images_result"]
        _c_steps = convert_result.get("diagnostic_steps", [])
        _c_code = _c_steps[-1].get("status_code") if _c_steps else None
        test_run_convert = AIConfigTestRun(
            config_id=config_id,
            tester_user_id=user_id,
            file_name=file_name,
            file_type="pdf",
            invoice_type=invoice_type,
            test_mode="pdf_compare",
            tested_strategy="convert_to_images",
            success=convert_result["success"],
            request_path=convert_result["request_path"],
            execution_path=convert_result["execution_path"],
            latency_ms=convert_result["latency_ms"],
            error_message=convert_result["error_message"],
            raw_response=json.dumps(convert_result["raw_response"], ensure_ascii=False) if convert_result["raw_response"] else None,
            parsed_result=json.dumps(convert_result["structured_result"], ensure_ascii=False) if convert_result["structured_result"] else None,
            status_code=_c_code,
            diagnostic_steps=json.dumps(_c_steps, ensure_ascii=False),
        )
        self.db.add(test_run_convert)
        self.db.commit()

        return {
            "test_mode": "pdf_compare",
            "file_name": file_name,
            "file_type": "pdf",
            "invoice_type": invoice_type,
            "direct_pdf_result": direct_result,
            "convert_to_images_result": convert_result,
            "recommended_strategy": comparison["recommended_strategy"],
            "recommendation_reason": comparison["recommendation_reason"]
        }

    def update_pdf_strategy(self, config_id: int, pdf_strategy: str) -> bool:
        """更新配置的 PDF 策略"""
        config = self.config_repo.get_by_id(config_id)
        if not config:
            raise NotFoundException("配置不存在")

        config.pdf_strategy = pdf_strategy
        self.db.commit()
        return True
