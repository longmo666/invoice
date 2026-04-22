from typing import Dict, Any


# 增值税发票字段定义
VAT_INVOICE_FIELDS = {
    "invoice_type": "",
    "invoice_code": "",
    "invoice_number": "",
    "invoice_date": "",
    "buyer_name": "",
    "buyer_tax_id": "",
    "buyer_address_phone": "",
    "buyer_bank_account": "",
    "seller_name": "",
    "seller_tax_id": "",
    "seller_address_phone": "",
    "seller_bank_account": "",
    "item_name": "",
    "amount_excluding_tax": "",
    "tax_rate": "",
    "tax_amount": "",
    "total_amount_cn": "",
    "total_amount": "",
    "payee": "",
    "reviewer": "",
    "issuer": ""
}

# 高铁票字段定义
RAILWAY_TICKET_FIELDS = {
    "invoice_type": "",
    "invoice_number": "",
    "invoice_date": "",
    "train_number": "",
    "departure_station": "",
    "train_date": "",
    "seat_class": "",
    "ticket_price": "",
    "passenger_name": "",
    "ticket_id": "",
    "buyer_name": "",
    "buyer_credit_code": ""
}


def validate_and_fill_vat_invoice(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    验证并补全增值税发票结果

    Args:
        result: AI 返回的识别结果

    Returns:
        补全后的结果字典
    """
    validated = VAT_INVOICE_FIELDS.copy()

    for key in validated.keys():
        if key in result and result[key] is not None:
            validated[key] = str(result[key])
        else:
            validated[key] = ""

    return validated


def validate_and_fill_railway_ticket(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    验证并补全高铁票结果

    Args:
        result: AI 返回的识别结果

    Returns:
        补全后的结果字典
    """
    validated = RAILWAY_TICKET_FIELDS.copy()

    for key in validated.keys():
        if key in result and result[key] is not None:
            validated[key] = str(result[key])
        else:
            validated[key] = ""

    return validated


def validate_and_fill_result(invoice_type: str, result: Dict[str, Any]) -> Dict[str, Any]:
    """
    根据发票类型验证并补全结果

    Args:
        invoice_type: 发票类型 (vat_special, vat_normal, railway_ticket)
        result: AI 返回的识别结果

    Returns:
        补全后的结果字典
    """
    if invoice_type in ["vat_special", "vat_normal"]:
        return validate_and_fill_vat_invoice(result)
    elif invoice_type == "railway_ticket":
        return validate_and_fill_railway_ticket(result)
    else:
        raise ValueError(f"不支持的发票类型: {invoice_type}")
