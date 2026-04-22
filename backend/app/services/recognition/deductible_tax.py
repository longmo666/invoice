"""
可抵扣税额计算模块

根据中国增值税法规计算发票的可抵扣进项税额。

法规依据：
- 《增值税暂行条例》
- 财政部 税务总局 海关总署公告2019年第39号

计算规则：
┌─────────────────────┬──────────────────────────────────────────────┐
│ 发票类型             │ 可抵扣税额                                    │
├─────────────────────┼──────────────────────────────────────────────┤
│ 增值税专用发票       │ 税额全额抵扣                                  │
│ 增值税普通发票       │ 不可抵扣                                      │
│ 铁路客运发票         │ 票价 ÷ (1 + 9%) × 9%                        │
└─────────────────────┴──────────────────────────────────────────────┘

注意：
- 判断专票/普票优先使用 AI 识别结果中的 invoice_type 字段（如"增值税专用发票"），
  而非任务创建时用户选择的类型。
- 普票不能作为进项税额抵扣凭证，统一返回 0。
- 实际抵扣需以企业税务认定为准，本计算仅供参考。
"""
import re
from typing import Dict, Any, Tuple


def _parse_amount(value) -> float:
    """解析金额字符串为浮点数"""
    if value is None:
        return 0.0
    cleaned = re.sub(r'[¥￥$€,，\s]', '', str(value))
    try:
        return float(cleaned)
    except (ValueError, TypeError):
        return 0.0


def _parse_tax_rate(value) -> float:
    """
    解析税率字符串为小数

    支持格式：'13%', '13', '0.13', '13％', '***'(免税)
    """
    if value is None:
        return 0.0
    s = str(value).strip()
    # 免税标记
    if s in ('***', '免税', '不征税', '0', ''):
        return 0.0
    cleaned = s.replace('%', '').replace('％', '')
    try:
        rate = float(cleaned)
        if rate > 1:
            rate = rate / 100.0
        return rate
    except (ValueError, TypeError):
        return 0.0


def _is_tax_exempt(result: Dict[str, Any]) -> bool:
    """判断是否为免税/不征税发票"""
    tax_rate_str = str(result.get("tax_rate", "")).strip()
    return tax_rate_str in ('***', '免税', '不征税', '0', '0%', '0.00', '')


def calculate_deductible_tax(result: Dict[str, Any], invoice_type: str) -> float:
    """
    计算可抵扣税额

    Args:
        result: 识别结果字典
        invoice_type: 任务级别的发票类型 (vat_special / vat_normal / railway_ticket)

    Returns:
        可抵扣税额（浮点数），不可抵扣返回 0.0
    """
    # 高铁票直接按公式算
    if invoice_type == "railway_ticket":
        return _calc_railway_ticket(result)

    # 对于 vat_special / vat_normal，根据识别结果中的实际发票类型判断
    actual_type = _detect_actual_invoice_type(result, invoice_type)

    if actual_type == "special":
        return _calc_vat_special(result)
    else:
        # 普票不可抵扣
        return 0.0


def _detect_actual_invoice_type(result: Dict[str, Any], task_invoice_type: str) -> str:
    """
    根据识别结果判断实际发票类型（专票 or 普票）

    优先看 AI 识别出的 invoice_type 字段，回退到任务级别类型。

    Returns:
        "special" 或 "normal"
    """
    recognized_type = str(result.get("invoice_type", "")).strip()

    # AI 识别结果明确标注了类型
    if "专用" in recognized_type:
        return "special"
    if "普通" in recognized_type:
        return "normal"

    # 回退到任务级别类型
    if task_invoice_type == "vat_special":
        return "special"
    return "normal"


def calculate_deductible_tax_detail(result: Dict[str, Any], invoice_type: str) -> Tuple[float, str]:
    """
    计算可抵扣税额（带说明）

    Returns:
        (可抵扣税额, 计算说明)
    """
    if invoice_type == "railway_ticket":
        amount = _calc_railway_ticket(result)
        price = _parse_amount(result.get("ticket_price", ""))
        if amount > 0:
            return amount, f"铁路客运: {price:.2f} ÷ 1.09 × 9% = {amount:.2f}"
        return 0.0, "票价为空，无法计算"

    actual_type = _detect_actual_invoice_type(result, invoice_type)

    if actual_type == "special":
        amount = _calc_vat_special(result)
        if amount > 0:
            return amount, f"专票税额全额抵扣: {amount:.2f}"
        return 0.0, "专票税额为空，无法计算"
    else:
        return 0.0, "普票不可抵扣进项税额"


def _calc_vat_special(result: Dict[str, Any]) -> float:
    """
    增值税专用发票：税额全额可抵扣

    专票是最主要的进项抵扣凭证，发票上注明的税额可全额抵扣。
    """
    tax_amount = _parse_amount(result.get("tax_amount", ""))
    if tax_amount > 0:
        return round(tax_amount, 2)

    # 如果没有直接的税额字段，尝试用 不含税金额 × 税率 计算
    amount = _parse_amount(result.get("amount_excluding_tax", ""))
    rate = _parse_tax_rate(result.get("tax_rate", ""))
    if amount > 0 and rate > 0:
        return round(amount * rate, 2)

    # 如果有价税合计和税率，反算：合计 ÷ (1+税率) × 税率
    total = _parse_amount(result.get("total_amount", ""))
    if total > 0 and rate > 0:
        return round(total / (1 + rate) * rate, 2)

    return 0.0


def _calc_vat_normal(result: Dict[str, Any]) -> float:
    """
    增值税普通发票：不可抵扣

    普票不能作为进项税额抵扣凭证，统一返回 0。
    """
    return 0.0


def _calc_railway_ticket(result: Dict[str, Any]) -> float:
    """
    铁路客运发票（高铁票/动车票）

    计算公式：票价 ÷ (1 + 9%) × 9%
    依据：财政部 税务总局 海关总署公告2019年第39号 第六条
    """
    ticket_price = _parse_amount(result.get("ticket_price", ""))
    if ticket_price <= 0:
        return 0.0
    return round(ticket_price / (1 + 0.09) * 0.09, 2)
