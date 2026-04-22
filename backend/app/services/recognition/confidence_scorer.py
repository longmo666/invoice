"""
置信度评分器

基于字段完整度、格式校验、交叉验证计算识别结果的置信度分数
"""
import re
from typing import Dict, Any, Tuple


class ConfidenceScorer:
    """置信度评分器"""

    # 增值税发票必填字段及权重
    VAT_REQUIRED_FIELDS = {
        "invoice_number": 10,
        "invoice_date": 8,
        "buyer_name": 10,
        "buyer_tax_id": 8,
        "seller_name": 10,
        "seller_tax_id": 8,
        "item_name": 6,
        "amount_excluding_tax": 10,
        "tax_rate": 5,
        "tax_amount": 8,
        "total_amount": 12,
        "issuer": 5,
    }

    # 高铁票必填字段及权重
    RAILWAY_REQUIRED_FIELDS = {
        "invoice_number": 10,
        "train_number": 12,
        "departure_station": 10,
        "train_date": 10,
        "seat_class": 8,
        "ticket_price": 15,
        "passenger_name": 12,
        "ticket_id": 10,
    }

    # 字段中文名映射
    FIELD_LABELS = {
        "invoice_number": "发票号码",
        "invoice_date": "开票日期",
        "buyer_name": "购买方名称",
        "buyer_tax_id": "购买方税号",
        "seller_name": "销售方名称",
        "seller_tax_id": "销售方税号",
        "item_name": "项目名称",
        "amount_excluding_tax": "不含税金额",
        "tax_rate": "税率",
        "tax_amount": "税额",
        "total_amount": "价税合计",
        "issuer": "开票人",
        "train_number": "车次号",
        "departure_station": "出发站",
        "train_date": "发车日期",
        "seat_class": "座位等级",
        "ticket_price": "票价",
        "passenger_name": "乘车人",
        "ticket_id": "电子客票号",
    }

    @staticmethod
    def score(invoice_type: str, result: Dict[str, Any]) -> Tuple[float, str]:
        """
        计算置信度分数

        Returns:
            (score, reason) - score 0.0~1.0, reason 说明扣分原因
        """
        if invoice_type in ("vat_special", "vat_normal"):
            return ConfidenceScorer._score_vat(result)
        elif invoice_type == "railway_ticket":
            return ConfidenceScorer._score_railway(result)
        return 0.5, "未知发票类型"

    @staticmethod
    def _score_vat(result: Dict[str, Any]) -> Tuple[float, str]:
        total_weight = sum(ConfidenceScorer.VAT_REQUIRED_FIELDS.values())
        earned = 0
        issues = []

        for field, weight in ConfidenceScorer.VAT_REQUIRED_FIELDS.items():
            val = str(result.get(field, "")).strip()
            label = ConfidenceScorer.FIELD_LABELS.get(field, field)
            if not val:
                issues.append(f"{label}未识别")
                continue

            # 格式校验扣分
            penalty = ConfidenceScorer._validate_field(field, val)
            earned += weight * (1.0 - penalty)
            if penalty > 0:
                issues.append(f"{label}格式存疑")

        # 交叉验证：金额 + 税额 ≈ 价税合计
        cross_penalty = ConfidenceScorer._cross_validate_amounts(result)
        if cross_penalty > 0:
            earned *= (1.0 - cross_penalty * 0.15)
            issues.append("金额合计校验不通过")

        score = earned / total_weight if total_weight > 0 else 0
        score = max(0.0, min(1.0, score))
        reason = "; ".join(issues) if issues else "全部通过"
        return score, reason

    @staticmethod
    def _score_railway(result: Dict[str, Any]) -> Tuple[float, str]:
        total_weight = sum(ConfidenceScorer.RAILWAY_REQUIRED_FIELDS.values())
        earned = 0
        issues = []

        for field, weight in ConfidenceScorer.RAILWAY_REQUIRED_FIELDS.items():
            val = str(result.get(field, "")).strip()
            label = ConfidenceScorer.FIELD_LABELS.get(field, field)
            if not val:
                issues.append(f"{label}未识别")
                continue

            penalty = ConfidenceScorer._validate_field(field, val)
            earned += weight * (1.0 - penalty)
            if penalty > 0:
                issues.append(f"{label}格式存疑")

        score = earned / total_weight if total_weight > 0 else 0
        score = max(0.0, min(1.0, score))
        reason = "; ".join(issues) if issues else "全部通过"
        return score, reason

    @staticmethod
    def _validate_field(field: str, value: str) -> float:
        """
        校验单个字段格式，返回扣分比例 0.0~1.0
        0.0 = 完全正确, 1.0 = 完全错误
        """
        if not value:
            return 1.0

        # 发票号码：应为纯数字，8~20位
        if field == "invoice_number":
            cleaned = re.sub(r'[\s\-]', '', value)
            if not re.match(r'^\d{8,20}$', cleaned):
                return 0.3
            return 0.0

        # 税号：15~20位字母数字
        if field in ("buyer_tax_id", "seller_tax_id"):
            cleaned = re.sub(r'[\s\-]', '', value)
            if not re.match(r'^[A-Za-z0-9]{15,20}$', cleaned):
                return 0.4
            return 0.0

        # 日期：应包含年月日或 YYYY-MM-DD
        if field in ("invoice_date", "train_date"):
            if re.search(r'\d{4}[-/年]\d{1,2}[-/月]\d{1,2}', value):
                return 0.0
            return 0.3

        # 金额：应为数字（可含逗号、小数点）
        if field in ("amount_excluding_tax", "tax_amount", "total_amount", "ticket_price"):
            cleaned = re.sub(r'[¥￥,，\s]', '', value)
            try:
                float(cleaned)
                return 0.0
            except ValueError:
                return 0.5

        # 税率：应包含百分号或数字
        if field == "tax_rate":
            if re.search(r'\d+\.?\d*%?', value):
                return 0.0
            return 0.3

        return 0.0

    @staticmethod
    def _cross_validate_amounts(result: Dict[str, Any]) -> float:
        """
        交叉验证金额字段
        返回 0.0 = 通过, 1.0 = 完全不通过
        """
        try:
            amount_str = re.sub(r'[¥￥,，\s]', '', str(result.get("amount_excluding_tax", "")))
            tax_str = re.sub(r'[¥￥,，\s]', '', str(result.get("tax_amount", "")))
            total_str = re.sub(r'[¥￥,，\s]', '', str(result.get("total_amount", "")))

            if not amount_str or not tax_str or not total_str:
                return 0.0  # 缺字段不在这里扣分

            amount = float(amount_str)
            tax = float(tax_str)
            total = float(total_str)

            if total == 0:
                return 0.0

            expected = amount + tax
            diff_ratio = abs(expected - total) / total

            if diff_ratio < 0.01:  # 误差 < 1%
                return 0.0
            elif diff_ratio < 0.05:  # 误差 < 5%
                return 0.3
            else:
                return 1.0
        except (ValueError, ZeroDivisionError):
            return 0.0
