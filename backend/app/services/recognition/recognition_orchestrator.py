"""
识别编排器

负责编排整个识别流程，根据执行路径调用不同的处理器
"""
from typing import Dict, Any, List, Optional
from pathlib import Path
from sqlalchemy.orm import Session

from app.services.recognition.execution_path import ExecutionPath, ExecutionPathResolver
from app.services.recognition.preprocessors import PreprocessorFactory
from app.services.recognition.provider_factory import ProviderClientFactory
from app.services.recognition.prompts import get_prompt_template
from app.services.recognition.result_normalizer import ResultNormalizer
from app.services.recognition.schema_validator import validate_and_fill_result
from app.services.recognition.active_config_resolver import ActiveConfigResolver
from app.services.ai.rate_limiter import rate_limit_registry


class RecognitionOrchestrator:
    """识别编排器"""

    def __init__(self, db: Session):
        self.db = db
        self.config_resolver = ActiveConfigResolver(db)

    # ==================== 公共入口 ====================

    async def execute(
        self,
        file_path: Path,
        file_type: str,
        invoice_type: str,
        recognition_mode: str
    ) -> List[Dict[str, Any]]:
        """
        执行识别流程

        Returns:
            识别结果列表，每个元素包含：
            {
                "page_number": int | None,
                "item_index": int,
                "raw_response": dict | None,
                "result": dict,
                "confidence_score": float | None
            }
        """
        execution_path = ExecutionPathResolver.resolve(file_type, recognition_mode)

        if execution_path == ExecutionPath.XML_PARSER:
            return await self._execute_structured_parser(file_path, invoice_type, "xml")
        elif execution_path == ExecutionPath.OFD_PARSER:
            return await self._execute_structured_parser(file_path, invoice_type, "ofd")
        elif execution_path == ExecutionPath.AI_IMAGE:
            return await self._execute_ai_image(file_path, invoice_type)
        elif execution_path == ExecutionPath.AI_PDF:
            return await self._execute_ai_pdf(file_path, invoice_type)
        elif execution_path == ExecutionPath.LOCAL_OCR_IMAGE:
            raise NotImplementedError("本地 OCR 图片识别尚未实现")
        elif execution_path == ExecutionPath.LOCAL_OCR_PDF:
            raise NotImplementedError("本地 OCR PDF 识别尚未实现")
        elif execution_path == ExecutionPath.HYBRID_IMAGE:
            raise NotImplementedError("混合模式图片识别尚未实现")
        elif execution_path == ExecutionPath.HYBRID_PDF:
            raise NotImplementedError("混合模式 PDF 识别尚未实现")
        else:
            raise ValueError(f"不支持的执行路径: {execution_path}")

    # ==================== 内部工具方法 ====================

    def _normalize_and_validate(
        self, invoice_type: str, raw_data: dict, source: str
    ) -> dict:
        """标准化 + 验证补全（所有路径共用）"""
        normalized = ResultNormalizer.normalize(invoice_type, raw_data, source=source)
        return validate_and_fill_result(invoice_type, normalized)

    @staticmethod
    def _build_result_item(
        result: dict,
        item_index: int,
        page_number: Optional[int] = None,
        raw_response: Optional[dict] = None,
    ) -> Dict[str, Any]:
        """构建单条识别结果"""
        return {
            "page_number": page_number,
            "item_index": item_index,
            "raw_response": raw_response,
            "result": result,
            "confidence_score": None,  # 由置信度评分器计算
        }

    def _get_ai_client_and_prompt(self, invoice_type: str):
        """获取 AI 客户端和提示词（AI 路径共用）"""
        ai_config = self.config_resolver.validate_active_config()
        rate_limit_registry.configure(max_concurrency=ai_config.max_concurrency)

        client = ProviderClientFactory.create_client(
            provider_vendor=ai_config.provider_vendor,
            api_style=ai_config.api_style,
            base_url=ai_config.base_url,
            api_key=ai_config.api_key,
            model_name=ai_config.model_name,
            timeout=ai_config.timeout,
            temperature=ai_config.temperature,
            max_tokens=ai_config.max_tokens,
            ocr_chat_model=getattr(ai_config, "ocr_chat_model", None),
        )
        prompt_template = get_prompt_template(invoice_type, ai_config.provider_vendor)
        return ai_config, client, prompt_template

    async def _recognize_images(
        self, client, images: list, invoice_type: str, prompt_template: str,
        start_page: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """对一组图片逐张调用 AI 识别（AI image / AI PDF 转图片共用）"""
        results = []
        for idx, image_data in enumerate(images):
            ai_result = await rate_limit_registry.execute_with_limit(
                client.recognize_invoice(
                    image_data=image_data,
                    invoice_type=invoice_type,
                    prompt_template=prompt_template,
                )
            )
            validated = self._normalize_and_validate(
                invoice_type, ai_result["parsed_result"], source="ai"
            )
            page_number = (start_page + idx) if start_page is not None else None
            results.append(
                self._build_result_item(
                    validated, idx, page_number=page_number,
                    raw_response=ai_result.get("raw_response"),
                )
            )
        return results

    # ==================== 执行路径实现 ====================

    async def _execute_structured_parser(
        self, file_path: Path, invoice_type: str, file_type: str
    ) -> List[Dict[str, Any]]:
        """执行结构化解析（XML / OFD 共用）"""
        preprocess_result = await PreprocessorFactory.preprocess_file(file_path, file_type)
        parsed_data = preprocess_result.metadata.get("parsed_data", {})
        validated = self._normalize_and_validate(invoice_type, parsed_data, source=file_type)
        return [self._build_result_item(validated, 0)]

    async def _execute_ai_image(
        self, file_path: Path, invoice_type: str
    ) -> List[Dict[str, Any]]:
        """执行 AI 图片识别"""
        _, client, prompt_template = self._get_ai_client_and_prompt(invoice_type)

        preprocess_result = await PreprocessorFactory.preprocess_file(file_path, "image")
        images = preprocess_result.images
        if not images:
            raise ValueError("未能从文件中提取到图片")

        return await self._recognize_images(client, images, invoice_type, prompt_template)

    async def _execute_ai_pdf(
        self, file_path: Path, invoice_type: str
    ) -> List[Dict[str, Any]]:
        """执行 AI PDF 识别"""
        ai_config, client, prompt_template = self._get_ai_client_and_prompt(invoice_type)

        # 尝试 direct_pdf 策略
        if ai_config.pdf_strategy == "direct_pdf":
            try:
                with open(file_path, "rb") as f:
                    pdf_data = f.read()

                ai_result = await rate_limit_registry.execute_with_limit(
                    client.recognize_invoice_from_pdf(
                        pdf_data=pdf_data,
                        invoice_type=invoice_type,
                        prompt_template=prompt_template,
                    )
                )
                validated = self._normalize_and_validate(
                    invoice_type, ai_result["parsed_result"], source="ai"
                )
                return [
                    self._build_result_item(
                        validated, 0, raw_response=ai_result.get("raw_response")
                    )
                ]
            except NotImplementedError:
                pass  # 回退到转图片

        # 转图片策略（默认或回退）
        preprocess_result = await PreprocessorFactory.preprocess_file(file_path, "pdf")
        images = preprocess_result.images
        if not images:
            raise ValueError("未能从 PDF 中提取到图片")

        return await self._recognize_images(
            client, images, invoice_type, prompt_template, start_page=1
        )
