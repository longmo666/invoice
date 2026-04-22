"""
PDF 策略执行器

负责根据不同策略执行 PDF 识别。
URL 构造通过共享层 http_helpers 完成，不再调用客户端私有方法。
"""
import time
from typing import Dict, Any, Optional
from app.services.recognition.provider_base import AIProviderClient, RecognitionError
from app.services.recognition.pdf_converter import PDFConverter


class PDFStrategyRunner:
    """PDF 策略执行器"""

    def __init__(self, ai_client: AIProviderClient):
        self.ai_client = ai_client

    async def run_direct_pdf(
        self,
        pdf_data: bytes,
        invoice_type: str,
        prompt_template: str
    ) -> Dict[str, Any]:
        """直接传 PDF 策略"""
        start_time = time.time()
        request_path = ""  # 实际路径从 diagnostic_steps 聚合
        execution_path = "direct_pdf"

        try:
            result = await self.ai_client.recognize_invoice_from_pdf(
                pdf_data=pdf_data,
                invoice_type=invoice_type,
                prompt_template=prompt_template
            )

            latency_ms = int((time.time() - start_time) * 1000)

            field_stats = self._calculate_field_completeness(
                result.get("parsed_result"), invoice_type
            )

            # 从 client 返回的 diagnostic_steps 串出真实 request_path
            steps = result.get("diagnostic_steps", [])
            actual_path = " → ".join(s.get("url", "") for s in steps if s.get("url")) or request_path
            last_status = steps[-1].get("status_code") if steps else None

            return {
                "success": True,
                "strategy": "direct_pdf",
                "latency_ms": latency_ms,
                "request_path": actual_path,
                "execution_path": execution_path,
                "status_code": last_status,
                "error_message": None,
                "raw_response": result.get("raw_response"),
                "structured_result": result.get("parsed_result"),
                "field_completeness": field_stats,
                "diagnostic_steps": result.get("diagnostic_steps", []),
            }

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            fail_steps = e.diagnostic_steps if isinstance(e, RecognitionError) else []
            actual_fail_path = " → ".join(s.get("url", "") for s in fail_steps if s.get("url")) or request_path
            fail_status = fail_steps[-1].get("status_code") if fail_steps else None
            return {
                "success": False,
                "strategy": "direct_pdf",
                "latency_ms": latency_ms,
                "request_path": actual_fail_path,
                "execution_path": execution_path,
                "status_code": fail_status,
                "error_message": str(e),
                "raw_response": None,
                "structured_result": None,
                "field_completeness": None,
                "diagnostic_steps": fail_steps,
            }

    async def run_convert_to_images(
        self,
        pdf_data: bytes,
        invoice_type: str,
        prompt_template: str
    ) -> Dict[str, Any]:
        """转图片策略"""
        start_time = time.time()
        request_path = ""  # 实际路径从 diagnostic_steps 聚合
        execution_path = "convert_to_images"

        try:
            converter = PDFConverter()
            images = converter.convert_to_images(pdf_data)

            if not images:
                raise ValueError("PDF 转图片失败，未生成任何图片")

            all_results = []
            all_raw_responses = []
            all_diagnostic_steps = []

            for idx, image_data in enumerate(images):
                result = await self.ai_client.recognize_invoice(
                    image_data=image_data,
                    invoice_type=invoice_type,
                    prompt_template=prompt_template
                )
                all_results.append(result.get("parsed_result"))
                all_raw_responses.append(result.get("raw_response"))
                all_diagnostic_steps.append(result.get("diagnostic_steps", []))

            latency_ms = int((time.time() - start_time) * 1000)

            best_completeness = None
            best_rate = 0
            best_page_index = 0
            best_page_idx = 0
            primary_result = all_results[0] if all_results else {}

            for idx, page_result in enumerate(all_results):
                field_stats = self._calculate_field_completeness(page_result, invoice_type)
                if field_stats:
                    rate = field_stats.get("completeness_rate", 0)
                    if rate > best_rate:
                        best_rate = rate
                        best_completeness = field_stats
                        best_page_index = idx + 1
                        best_page_idx = idx
                        primary_result = page_result

            # 从最佳页的 diagnostic_steps 串出真实 request_path
            best_steps = all_diagnostic_steps[best_page_idx] if all_diagnostic_steps else []
            actual_path = " → ".join(s.get("url", "") for s in best_steps if s.get("url")) or request_path
            last_status = best_steps[-1].get("status_code") if best_steps else None

            return {
                "success": True,
                "strategy": "convert_to_images",
                "latency_ms": latency_ms,
                "request_path": actual_path,
                "execution_path": execution_path,
                "status_code": last_status,
                "error_message": None,
                "raw_response": all_raw_responses[best_page_idx] if all_raw_responses else None,
                "structured_result": primary_result,
                "field_completeness": best_completeness,
                "total_pages": len(images),
                "all_page_results": all_results,
                "best_page_index": best_page_index,
                "diagnostic_steps": all_diagnostic_steps[best_page_idx] if all_diagnostic_steps else [],
            }

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            fail_steps = e.diagnostic_steps if isinstance(e, RecognitionError) else []
            actual_fail_path = " → ".join(s.get("url", "") for s in fail_steps if s.get("url")) or request_path
            fail_status = fail_steps[-1].get("status_code") if fail_steps else None
            return {
                "success": False,
                "strategy": "convert_to_images",
                "latency_ms": latency_ms,
                "request_path": actual_fail_path,
                "execution_path": execution_path,
                "status_code": fail_status,
                "error_message": str(e),
                "raw_response": None,
                "structured_result": None,
                "field_completeness": None,
                "diagnostic_steps": fail_steps,
            }

    async def run_both_strategies(
        self,
        pdf_data: bytes,
        invoice_type: str,
        prompt_template: str
    ) -> Dict[str, Any]:
        """运行两种策略并对比"""
        convert_result = await self.run_convert_to_images(pdf_data, invoice_type, prompt_template)
        direct_result = await self.run_direct_pdf(pdf_data, invoice_type, prompt_template)

        recommended_strategy, recommendation_reason = self._recommend_strategy(
            direct_result, convert_result
        )

        return {
            "direct_pdf_result": direct_result,
            "convert_to_images_result": convert_result,
            "recommended_strategy": recommended_strategy,
            "recommendation_reason": recommendation_reason
        }

    def _calculate_field_completeness(
        self,
        structured_result: Optional[Dict[str, Any]],
        invoice_type: str
    ) -> Optional[Dict[str, Any]]:
        """计算字段完整度"""
        if not structured_result:
            return None

        _vat_fields = [
            "invoice_code", "invoice_number", "invoice_date",
            "buyer_name", "buyer_tax_id",
            "seller_name", "seller_tax_id",
            "amount_excluding_tax", "tax_amount", "total_amount"
        ]
        required_fields_map = {
            "vat_special": _vat_fields,
            "vat_normal": _vat_fields,
            "railway_ticket": [
                "train_number", "departure_station", "train_date",
                "seat_class", "ticket_price", "passenger_name", "ticket_id"
            ],
        }

        required_fields = required_fields_map.get(invoice_type, [])
        if not required_fields:
            return None

        recognized_fields = []
        missing_fields = []

        for field in required_fields:
            value = structured_result.get(field)
            if value and str(value).strip() and str(value).strip() != "未识别":
                recognized_fields.append(field)
            else:
                missing_fields.append(field)

        return {
            "required_fields_total": len(required_fields),
            "recognized_fields_count": len(recognized_fields),
            "missing_fields": missing_fields,
            "completeness_rate": round(len(recognized_fields) / len(required_fields) * 100, 2) if required_fields else 0
        }

    def _recommend_strategy(
        self,
        direct_result: Dict[str, Any],
        convert_result: Dict[str, Any]
    ) -> tuple[Optional[str], Optional[str]]:
        """推荐策略"""
        direct_success = direct_result.get("success", False)
        convert_success = convert_result.get("success", False)

        if direct_success and convert_success:
            direct_completeness = direct_result.get("field_completeness")
            convert_completeness = convert_result.get("field_completeness")

            if direct_completeness and convert_completeness:
                direct_rate = direct_completeness.get("completeness_rate", 0)
                convert_rate = convert_completeness.get("completeness_rate", 0)

                if abs(direct_rate - convert_rate) > 10:
                    if direct_rate > convert_rate:
                        return "direct_pdf", f"直传 PDF 字段完整度更高（{direct_rate}% vs {convert_rate}%）"
                    else:
                        return "convert_to_images", f"转图片字段完整度更高（{convert_rate}% vs {direct_rate}%）"

            direct_latency = direct_result.get("latency_ms", float('inf'))
            convert_latency = convert_result.get("latency_ms", float('inf'))

            if direct_latency < convert_latency:
                return "direct_pdf", f"两种策略完整度相近，直传 PDF 更快（{direct_latency}ms vs {convert_latency}ms）"
            else:
                return "convert_to_images", f"两种策略完整度相近，转图片更快（{convert_latency}ms vs {direct_latency}ms）"

        if direct_success and not convert_success:
            return "direct_pdf", "只有直传 PDF 成功"

        if not direct_success and convert_success:
            return "convert_to_images", "只有转图片成功"

        return None, "两种策略均失败"
