"""
结果标准化器

负责将不同来源的识别结果转换为统一的标准格式
"""
from typing import Dict, Any


class ResultNormalizer:
    """结果标准化器"""

    @staticmethod
    def normalize(
        invoice_type: str,
        raw_result: Dict[str, Any],
        source: str = "ai"
    ) -> Dict[str, Any]:
        """
        标准化识别结果

        Args:
            invoice_type: 发票类型
            raw_result: 原始结果
            source: 结果来源 (ai, xml, ofd, local_ocr)

        Returns:
            标准化后的结果
        """
        if source == "xml":
            return ResultNormalizer._normalize_from_xml(invoice_type, raw_result)
        elif source == "ofd":
            return ResultNormalizer._normalize_from_ofd(invoice_type, raw_result)
        elif source == "ai":
            return ResultNormalizer._normalize_from_ai(invoice_type, raw_result)
        elif source == "local_ocr":
            return ResultNormalizer._normalize_from_local_ocr(invoice_type, raw_result)
        else:
            raise ValueError(f"不支持的结果来源: {source}")

    @staticmethod
    def _normalize_from_xml(invoice_type: str, raw_result: Dict[str, Any]) -> Dict[str, Any]:
        """从 XML 解析结果标准化"""
        # XML 解析结果已经是标准格式，直接返回
        return raw_result

    @staticmethod
    def _normalize_from_ofd(invoice_type: str, raw_result: Dict[str, Any]) -> Dict[str, Any]:
        """从 OFD 解析结果标准化"""
        # OFD 解析结果已经是标准格式，直接返回
        return raw_result

    @staticmethod
    def _normalize_from_ai(invoice_type: str, raw_result: Dict[str, Any]) -> Dict[str, Any]:
        """从 AI 识别结果标准化"""
        # AI 返回的结果已经按照 prompt 要求的格式返回，这里做最后的字段映射和清理
        normalized = {}

        if invoice_type == "vat_special":
            # 增值税专用发票字段映射
            normalized = {
                "invoice_type": raw_result.get("invoice_type", ""),
                "invoice_code": raw_result.get("invoice_code", ""),
                "invoice_number": raw_result.get("invoice_number", ""),
                "invoice_date": raw_result.get("invoice_date", ""),
                "buyer_name": raw_result.get("buyer_name", ""),
                "buyer_tax_id": raw_result.get("buyer_tax_id", ""),
                "buyer_address_phone": raw_result.get("buyer_address_phone", ""),
                "buyer_bank_account": raw_result.get("buyer_bank_account", ""),
                "seller_name": raw_result.get("seller_name", ""),
                "seller_tax_id": raw_result.get("seller_tax_id", ""),
                "seller_address_phone": raw_result.get("seller_address_phone", ""),
                "seller_bank_account": raw_result.get("seller_bank_account", ""),
                "item_name": raw_result.get("item_name", ""),
                "amount_excluding_tax": raw_result.get("amount_excluding_tax", ""),
                "tax_rate": raw_result.get("tax_rate", ""),
                "tax_amount": raw_result.get("tax_amount", ""),
                "total_amount_cn": raw_result.get("total_amount_cn", ""),
                "total_amount": raw_result.get("total_amount", ""),
                "payee": raw_result.get("payee", ""),
                "reviewer": raw_result.get("reviewer", ""),
                "issuer": raw_result.get("issuer", ""),
                "remark": raw_result.get("remark", "")
            }
        elif invoice_type == "vat_normal":
            # 增值税普通发票字段映射（与专票保持一致，普票也可能有地址电话和开户行）
            normalized = {
                "invoice_type": raw_result.get("invoice_type", ""),
                "invoice_code": raw_result.get("invoice_code", ""),
                "invoice_number": raw_result.get("invoice_number", ""),
                "invoice_date": raw_result.get("invoice_date", ""),
                "buyer_name": raw_result.get("buyer_name", ""),
                "buyer_tax_id": raw_result.get("buyer_tax_id", ""),
                "buyer_address_phone": raw_result.get("buyer_address_phone", ""),
                "buyer_bank_account": raw_result.get("buyer_bank_account", ""),
                "seller_name": raw_result.get("seller_name", ""),
                "seller_tax_id": raw_result.get("seller_tax_id", ""),
                "seller_address_phone": raw_result.get("seller_address_phone", ""),
                "seller_bank_account": raw_result.get("seller_bank_account", ""),
                "item_name": raw_result.get("item_name", ""),
                "amount_excluding_tax": raw_result.get("amount_excluding_tax", ""),
                "tax_rate": raw_result.get("tax_rate", ""),
                "tax_amount": raw_result.get("tax_amount", ""),
                "total_amount_cn": raw_result.get("total_amount_cn", ""),
                "total_amount": raw_result.get("total_amount", ""),
                "payee": raw_result.get("payee", ""),
                "reviewer": raw_result.get("reviewer", ""),
                "issuer": raw_result.get("issuer", ""),
                "remark": raw_result.get("remark", "")
            }
        elif invoice_type == "railway_ticket":
            # 火车票字段映射（与 prompt 和 schema_validator 保持一致）
            normalized = {
                "invoice_type": raw_result.get("invoice_type", ""),
                "invoice_number": raw_result.get("invoice_number", ""),
                "invoice_date": raw_result.get("invoice_date", ""),
                "train_number": raw_result.get("train_number", ""),
                "departure_station": raw_result.get("departure_station", ""),
                "train_date": raw_result.get("train_date", ""),
                "seat_class": raw_result.get("seat_class", ""),
                "ticket_price": raw_result.get("ticket_price", ""),
                "passenger_name": raw_result.get("passenger_name", ""),
                "ticket_id": raw_result.get("ticket_id", ""),
                "buyer_name": raw_result.get("buyer_name", ""),
                "buyer_credit_code": raw_result.get("buyer_credit_code", "")
            }
        else:
            # 未知类型，直接返回原始结果
            normalized = raw_result

        return normalized

    @staticmethod
    def _normalize_from_local_ocr(invoice_type: str, raw_result: Dict[str, Any]) -> Dict[str, Any]:
        """从本地 OCR 结果标准化"""
        # 本地 OCR 结果需要根据具体实现进行映射
        # 这里预留接口，未来实现
        return raw_result
