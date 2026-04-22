from pathlib import Path
from typing import Dict, Any, List, Optional
from app.services.recognition.preprocessors.base import FilePreprocessor, PreprocessorResult


class OFDPreprocessor(FilePreprocessor):
    """OFD 发票预处理器（不经过 AI，直接结构化解析）"""

    # EInvoice Tag.xml 标签名 → 标准字段名
    TAG_FIELD_MAPPING = {
        # 发票号码（TaxSupervisionInfo 下）
        "InvoiceNumber": "invoice_number",
        # 开票日期
        "IssueTime": "invoice_date",
        "RequestTime": "invoice_date",
        # 购买方
        "BuyerName": "buyer_name",
        "BuyerIdNum": "buyer_tax_id",
        "BuyerAddr": "_buyer_addr",
        "BuyerTelNum": "_buyer_tel",
        "BuyerBankName": "_buyer_bank_name",
        "BuyerBankAccNum": "_buyer_bank_acc",
        # 销售方
        "SellerName": "seller_name",
        "SellerIdNum": "seller_tax_id",
        "SellerAddr": "_seller_addr",
        "SellerTelNum": "_seller_tel",
        "SellerBankName": "_seller_bank_name",
        "SellerBankAccNum": "_seller_bank_acc",
        # 金额
        "TotalAmWithoutTax": "amount_excluding_tax",
        "TotalTaxAm": "tax_amount",
        "TotalTax-includedAmount": "total_amount",
        "TotalTax-includedAmountInChinese": "total_amount_cn",
        # 项目
        "ItemName": "item_name",
        "TaxRate": "tax_rate",
        "Amount": "_item_amount",
        "ComTaxAm": "_item_tax",
        # 开票人
        "Drawer": "issuer",
        # 发票类型标签
        "GeneralOrSpecialVAT": "_invoice_type_label",
        "EInvoiceType": "_einvoice_type_label",
    }

    async def preprocess(self, file_path: Path) -> PreprocessorResult:
        parsed_data = self.parse_ofd_invoice(file_path)
        return PreprocessorResult(
            images=[],
            metadata={
                "is_structured": True,
                "parsed_data": parsed_data,
                "original_format": ".ofd"
            }
        )

    def parse_ofd_invoice(self, file_path: Path) -> Dict[str, Any]:
        """解析 OFD 发票文件"""
        try:
            import zipfile
            import xml.etree.ElementTree as ET

            result: Dict[str, Any] = {
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

            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                all_files = zip_ref.namelist()

                # Step 1: Build TextObject ID → text map from all Content.xml pages
                text_object_map = self._build_text_object_map(zip_ref, all_files)
                print(f"[OFD] TextObject map: {len(text_object_map)} entries")

                # Step 2: Find and parse Tag.xml (EInvoice structured data)
                tag_files = [f for f in all_files if f.lower().endswith('tag.xml')]
                for tag_file in tag_files:
                    try:
                        xml_content = zip_ref.read(tag_file).decode('utf-8')
                        root = ET.fromstring(xml_content)
                        self._extract_from_tag_xml(root, result, text_object_map)
                    except Exception as e:
                        print(f"[OFD] 解析 {tag_file} 失败: {e}")

                # Step 3: Compose address_phone and bank_account fields
                self._compose_combined_fields(result)

                # Step 4: Fallback — scan all XML files for CustomData style fields
                if not result.get("invoice_number"):
                    xml_files = [f for f in all_files if f.lower().endswith('.xml')]
                    for xml_file in xml_files:
                        if xml_file.lower().endswith('tag.xml'):
                            continue
                        try:
                            xml_content = zip_ref.read(xml_file).decode('utf-8')
                            root = ET.fromstring(xml_content)
                            self._extract_fallback(root, result)
                        except Exception:
                            continue

            print(f"[OFD] 最终解析结果: {result}")
            return result

        except Exception as e:
            raise ValueError(f"OFD 解析失败: {str(e)}")

    def _build_text_object_map(self, zip_ref, all_files: List[str]) -> Dict[str, str]:
        """从所有 Content.xml 页面构建 TextObject ID → 文本 映射，同时记录 ID 顺序"""
        import xml.etree.ElementTree as ET

        text_map: Dict[str, str] = {}
        self._text_object_ids: List[str] = []  # 按出现顺序记录所有 TextObject ID
        content_files = [f for f in all_files if 'content.xml' in f.lower()]

        for cf in content_files:
            try:
                xml_content = zip_ref.read(cf).decode('utf-8')
                root = ET.fromstring(xml_content)
                for elem in root.iter():
                    tag = elem.tag
                    if '}' in tag:
                        tag = tag.split('}', 1)[1]
                    if tag == 'TextObject':
                        obj_id = elem.get('ID')
                        if not obj_id:
                            continue
                        self._text_object_ids.append(obj_id)
                        texts = []
                        for child in elem.iter():
                            child_tag = child.tag
                            if '}' in child_tag:
                                child_tag = child_tag.split('}', 1)[1]
                            if child_tag == 'TextCode' and child.text:
                                texts.append(child.text.strip())
                        if texts:
                            text_map[obj_id] = ''.join(texts)
            except Exception as e:
                print(f"[OFD] 解析 {cf} 构建文本映射失败: {e}")

        return text_map

    def _extract_from_tag_xml(
        self,
        element,
        result: Dict[str, Any],
        text_object_map: Dict[str, str]
    ):
        """递归解析 Tag.xml (EInvoice 结构)，提取字段值"""
        tag = element.tag
        if '}' in tag:
            tag = tag.split('}', 1)[1]

        # Check if this tag maps to a field
        if tag in self.TAG_FIELD_MAPPING:
            field_key = self.TAG_FIELD_MAPPING[tag]
            value = self._resolve_element_value(element, text_object_map)
            if value and not result.get(field_key):
                result[field_key] = value
                print(f"[OFD] Tag匹配: {tag} -> {field_key} = {value}")

        # Special: LabelName contains invoice type text
        if tag == 'LabelName':
            value = self._resolve_element_value(element, text_object_map)
            if value and ('增值税' in value or '电子发票' in value) and '蓝字' not in value:
                if not result.get("invoice_type"):
                    result["invoice_type"] = value
                    print(f"[OFD] 发票类型: {value}")

        # Special: EIid contains the invoice number (header level)
        if tag == 'EIid':
            value = self._resolve_element_value(element, text_object_map)
            if value and value != 'null' and not result.get("invoice_number"):
                result["invoice_number"] = value
                print(f"[OFD] EIid发票号码: {value}")

        # Recurse into children
        for child in element:
            self._extract_from_tag_xml(child, result, text_object_map)

    def _resolve_element_value(self, element, text_object_map: Dict[str, str]) -> str:
        """解析元素的值：优先 ObjectData 文本，其次 ObjectRef 引用，最后 element.text"""

        # Check for ofd:ObjectData child
        for child in element:
            child_tag = child.tag
            if '}' in child_tag:
                child_tag = child_tag.split('}', 1)[1]
            if child_tag == 'ObjectData':
                text = (child.text or '').strip()
                if text and text != 'null':
                    return text

        # Check for ofd:ObjectRef child — resolve via text_object_map
        for child in element:
            child_tag = child.tag
            if '}' in child_tag:
                child_tag = child_tag.split('}', 1)[1]
            if child_tag == 'ObjectRef':
                ref_id = (child.text or '').strip()
                if ref_id and ref_id in text_object_map:
                    value = text_object_map[ref_id]
                    # 如果值是纯符号（如 ¥、￥），尝试取下一个相邻 TextObject 的值
                    if value in ('¥', '￥', '¥', '$', '€'):
                        next_value = self._get_next_text_object_value(ref_id, text_object_map)
                        if next_value:
                            return next_value
                    return value

        # Fallback: direct text
        text = (element.text or '').strip()
        if text and text != 'null':
            return text

        return ""

    def _get_next_text_object_value(self, current_id: str, text_object_map: Dict[str, str]) -> str:
        """获取当前 TextObject 之后的下一个 TextObject 的文本值"""
        ids = getattr(self, '_text_object_ids', [])
        try:
            idx = ids.index(current_id)
            if idx + 1 < len(ids):
                next_id = ids[idx + 1]
                return text_object_map.get(next_id, "")
        except ValueError:
            pass
        return ""

    def _compose_combined_fields(self, result: Dict[str, Any]):
        """组合地址电话、开户行账号等复合字段"""
        # 购买方地址电话
        addr = result.pop("_buyer_addr", "") or ""
        tel = result.pop("_buyer_tel", "") or ""
        if addr or tel:
            combined = f"{addr} {tel}".strip() if addr and tel else (addr or tel)
            if not result.get("buyer_address_phone"):
                result["buyer_address_phone"] = combined

        # 购买方开户行账号
        bank = result.pop("_buyer_bank_name", "") or ""
        acc = result.pop("_buyer_bank_acc", "") or ""
        if bank or acc:
            combined = f"{bank} {acc}".strip() if bank and acc else (bank or acc)
            if not result.get("buyer_bank_account"):
                result["buyer_bank_account"] = combined

        # 销售方地址电话
        addr = result.pop("_seller_addr", "") or ""
        tel = result.pop("_seller_tel", "") or ""
        if addr or tel:
            combined = f"{addr} {tel}".strip() if addr and tel else (addr or tel)
            if not result.get("seller_address_phone"):
                result["seller_address_phone"] = combined

        # 销售方开户行账号
        bank = result.pop("_seller_bank_name", "") or ""
        acc = result.pop("_seller_bank_acc", "") or ""
        if bank or acc:
            combined = f"{bank} {acc}".strip() if bank and acc else (bank or acc)
            if not result.get("seller_bank_account"):
                result["seller_bank_account"] = combined

        # Clean up any remaining temp fields
        for key in list(result.keys()):
            if key.startswith("_"):
                result.pop(key, None)

        # 日期格式处理：去掉时间部分，只保留日期
        if result.get("invoice_date"):
            date_str = result["invoice_date"]
            # "2026-02-02 13:56:50" -> "2026-02-02"
            if " " in date_str:
                date_str = date_str.split(" ")[0]
            result["invoice_date"] = date_str

    def _extract_fallback(self, element, result: Dict[str, Any]):
        """回退方案：扫描 CustomData 风格的 XML 节点"""
        FALLBACK_MAP = {
            "发票号码": "invoice_number", "开票日期": "invoice_date",
            "购买方名称": "buyer_name", "购方名称": "buyer_name",
            "购买方纳税人识别号": "buyer_tax_id", "购买方税号": "buyer_tax_id",
            "销售方名称": "seller_name", "销方名称": "seller_name",
            "销售方纳税人识别号": "seller_tax_id", "销售方税号": "seller_tax_id",
            "合计金额": "amount_excluding_tax", "合计税额": "tax_amount",
            "价税合计": "total_amount", "开票人": "issuer",
        }

        tag = element.tag
        if '}' in tag:
            tag = tag.split('}', 1)[1]

        name_attr = element.get('Name') or element.get('name') or ""
        if name_attr and name_attr in FALLBACK_MAP:
            field_key = FALLBACK_MAP[name_attr]
            value = (element.text or "").strip()
            if value and not result.get(field_key):
                result[field_key] = value

        if tag in FALLBACK_MAP:
            field_key = FALLBACK_MAP[tag]
            value = (element.text or "").strip()
            if value and not result.get(field_key):
                result[field_key] = value

        for child in element:
            self._extract_fallback(child, result)

    def supports_file_type(self, file_type: str) -> bool:
        return file_type == "ofd"
