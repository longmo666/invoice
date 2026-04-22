from pathlib import Path
from typing import List, Dict, Any
import xml.etree.ElementTree as ET
from app.services.recognition.preprocessors.base import FilePreprocessor, PreprocessorResult


class XMLParser(FilePreprocessor):
    """XML 发票解析器（不经过 AI，直接结构化解析）"""

    # 标签名/属性名 → 标准字段名 的映射（覆盖常见中文发票 XML 格式）
    FIELD_MAPPING = {
        # 发票号码
        "发票号码": "invoice_number",
        "InvoiceNumber": "invoice_number",
        "FpHm": "invoice_number",
        "Fphm": "invoice_number",
        "fphm": "invoice_number",
        # 开票日期
        "开票日期": "invoice_date",
        "InvoiceDate": "invoice_date",
        "KpRq": "invoice_date",
        "Kprq": "invoice_date",
        "kprq": "invoice_date",
        # 发票类型
        "发票类型": "invoice_type",
        "发票名称": "invoice_type",
        "InvoiceType": "invoice_type",
        # 购买方名称
        "购买方名称": "buyer_name",
        "购方名称": "buyer_name",
        "GfMc": "buyer_name",
        "Gfmc": "buyer_name",
        "gfmc": "buyer_name",
        "BuyerName": "buyer_name",
        # 购买方税号
        "购买方纳税人识别号": "buyer_tax_id",
        "购买方税号": "buyer_tax_id",
        "购方税号": "buyer_tax_id",
        "GfNsrsbh": "buyer_tax_id",
        "Gfsbh": "buyer_tax_id",
        "gfsbh": "buyer_tax_id",
        "BuyerTaxId": "buyer_tax_id",
        # 购买方地址电话
        "购买方地址电话": "buyer_address_phone",
        "购方地址电话": "buyer_address_phone",
        "GfDzdh": "buyer_address_phone",
        "Gfdzdh": "buyer_address_phone",
        # 购买方开户行账号
        "购买方开户行及账号": "buyer_bank_account",
        "购方开户行及账号": "buyer_bank_account",
        "GfYhzh": "buyer_bank_account",
        "Gfyhzh": "buyer_bank_account",
        # 销售方名称
        "销售方名称": "seller_name",
        "销方名称": "seller_name",
        "XfMc": "seller_name",
        "Xfmc": "seller_name",
        "xfmc": "seller_name",
        "SellerName": "seller_name",
        # 销售方税号
        "销售方纳税人识别号": "seller_tax_id",
        "销售方税号": "seller_tax_id",
        "销方税号": "seller_tax_id",
        "XfNsrsbh": "seller_tax_id",
        "Xfsbh": "seller_tax_id",
        "xfsbh": "seller_tax_id",
        "SellerTaxId": "seller_tax_id",
        # 销售方地址电话
        "销售方地址电话": "seller_address_phone",
        "销方地址电话": "seller_address_phone",
        "XfDzdh": "seller_address_phone",
        "Xfdzdh": "seller_address_phone",
        # 销售方开户行账号
        "销售方开户行及账号": "seller_bank_account",
        "销方开户行及账号": "seller_bank_account",
        "XfYhzh": "seller_bank_account",
        "Xfyhzh": "seller_bank_account",
        # 项目名称
        "货物或应税劳务名称": "item_name",
        "项目名称": "item_name",
        "货物或应税劳务、服务名称": "item_name",
        "HwMc": "item_name",
        "Hwmc": "item_name",
        "ItemName": "item_name",
        "SPMC": "item_name",
        "spmc": "item_name",
        # 金额
        "合计金额": "amount_excluding_tax",
        "不含税金额": "amount_excluding_tax",
        "金额合计": "amount_excluding_tax",
        "Hjje": "amount_excluding_tax",
        "hjje": "amount_excluding_tax",
        "AmountExcludingTax": "amount_excluding_tax",
        # 税率
        "税率": "tax_rate",
        "Sl": "tax_rate",
        "sl": "tax_rate",
        "TaxRate": "tax_rate",
        # 税额
        "合计税额": "tax_amount",
        "税额": "tax_amount",
        "税额合计": "tax_amount",
        "Hjse": "tax_amount",
        "hjse": "tax_amount",
        "TaxAmount": "tax_amount",
        # 价税合计
        "价税合计": "total_amount",
        "总金额": "total_amount",
        "价税合计(小写)": "total_amount",
        "Jshj": "total_amount",
        "jshj": "total_amount",
        "TotalAmount": "total_amount",
        # 价税合计大写
        "价税合计大写": "total_amount_cn",
        "价税合计(大写)": "total_amount_cn",
        "TotalAmountCN": "total_amount_cn",
        # 开票人
        "开票人": "issuer",
        "Kpr": "issuer",
        "kpr": "issuer",
        "Issuer": "issuer",
        # 收款人
        "收款人": "payee",
        "Skr": "payee",
        "skr": "payee",
        # 复核人
        "复核人": "reviewer",
        "Fhr": "reviewer",
        "fhr": "reviewer",
    }

    async def preprocess(self, file_path: Path) -> PreprocessorResult:
        parsed_data = self.parse_xml_invoice(file_path)
        return PreprocessorResult(
            images=[],
            metadata={
                "is_structured": True,
                "parsed_data": parsed_data,
                "original_format": ".xml"
            }
        )

    def parse_xml_invoice(self, file_path: Path) -> Dict[str, Any]:
        """解析 XML 发票文件，递归遍历所有节点提取字段"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            result = {
                "invoice_type": "",
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
                "issuer": "",
                "payee": "",
                "reviewer": "",
            }

            # 递归遍历所有节点
            self._extract_from_element(root, result)

            print(f"[XML] 最终解析结果: {result}")
            return result

        except Exception as e:
            raise ValueError(f"XML 解析失败: {str(e)}")

    def _extract_from_element(self, element: ET.Element, result: Dict[str, Any]):
        """递归遍历 XML 元素，提取所有匹配的字段"""
        # 去掉命名空间前缀获取本地标签名
        tag = element.tag
        if '}' in tag:
            tag = tag.split('}', 1)[1]

        # 检查带 Name 属性的节点（如 <Item Name="购买方名称">xxx</Item>）
        name_attr = element.get('Name') or element.get('name') or ""
        if name_attr and name_attr in self.FIELD_MAPPING:
            field_key = self.FIELD_MAPPING[name_attr]
            value = (element.text or "").strip()
            if value and not result.get(field_key):
                result[field_key] = value
                print(f"[XML] 匹配属性: {name_attr} -> {field_key} = {value}")

        # 检查标签名本身是否是字段名
        if tag in self.FIELD_MAPPING:
            field_key = self.FIELD_MAPPING[tag]
            value = (element.text or "").strip()
            if value and not result.get(field_key):
                result[field_key] = value
                print(f"[XML] 匹配标签: {tag} -> {field_key} = {value}")

        # 递归子元素
        for child in element:
            self._extract_from_element(child, result)

    def supports_file_type(self, file_type: str) -> bool:
        return file_type == "xml"
