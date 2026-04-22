"""
智谱 GLM 提示词

适用于: GLM-4V, GLM-4V-Plus 等
特点: 中文理解能力强，但需要明确强调只返回 JSON，
      不要包含 markdown 代码块标记
"""

VAT_INVOICE_PROMPT = """请识别这张增值税发票中的所有字段信息，直接返回 JSON 结果。

要求：
1. 严格按照 JSON 格式返回结果
2. 所有字段都必须返回，如果某个字段在发票上不存在或无法识别，返回空字符串 ""
3. 日期格式统一为 YYYY-MM-DD
4. 税率格式为百分比字符串，如 "13%"
5. 金额字段返回字符串格式，保留两位小数
6. 只返回 JSON 对象，不要包含任何解释、说明或 markdown 代码块标记

JSON 字段定义：
{
  "invoice_type": "增值税专用发票 或 增值税普通发票",
  "invoice_code": "发票代码",
  "invoice_number": "发票号码",
  "invoice_date": "开票日期 YYYY-MM-DD",
  "buyer_name": "购买方名称",
  "buyer_tax_id": "购买方税号",
  "buyer_address_phone": "购买方地址电话",
  "buyer_bank_account": "购买方开户行及账号",
  "seller_name": "销售方名称",
  "seller_tax_id": "销售方税号",
  "seller_address_phone": "销售方地址电话",
  "seller_bank_account": "销售方开户行及账号",
  "item_name": "项目名称（货物或应税劳务、服务名称）",
  "amount_excluding_tax": "不含税金额",
  "tax_rate": "税率（如 13%）",
  "tax_amount": "税额",
  "total_amount_cn": "价税合计大写",
  "total_amount": "价税合计小写",
  "payee": "收款人",
  "reviewer": "复核人",
  "issuer": "开票人"
}"""


RAILWAY_TICKET_PROMPT = """请识别这张高铁票中的所有字段信息，直接返回 JSON 结果。

要求：
1. 严格按照 JSON 格式返回结果
2. 所有字段都必须返回，如果某个字段在票面上不存在或无法识别，返回空字符串 ""
3. 日期格式统一为 YYYY-MM-DD
4. 票价返回字符串格式，保留两位小数
5. 只返回 JSON 对象，不要包含任何解释、说明或 markdown 代码块标记

JSON 字段定义：
{
  "invoice_type": "高铁票",
  "invoice_number": "发票号码",
  "invoice_date": "开票日期 YYYY-MM-DD",
  "train_number": "车次号",
  "departure_station": "起始站",
  "train_date": "高铁发车日期 YYYY-MM-DD",
  "seat_class": "座位等级（如 二等座、一等座、商务座）",
  "ticket_price": "票价",
  "passenger_name": "乘车人",
  "ticket_id": "电子客票号",
  "buyer_name": "购买方名称",
  "buyer_credit_code": "购买方统一社会信用代码"
}"""


PROMPTS = {
    "vat": VAT_INVOICE_PROMPT,
    "railway": RAILWAY_TICKET_PROMPT,
}
