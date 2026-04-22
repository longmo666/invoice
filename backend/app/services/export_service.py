"""
导出服务

负责将识别结果导出为不同格式
"""
from typing import List
from io import BytesIO
import csv
from openpyxl import Workbook
from sqlalchemy.orm import Session

from app.models.recognition_item import RecognitionItem
from app.repositories.recognition_item import RecognitionItemRepository


class ExportService:
    """导出服务"""

    def __init__(self, db: Session):
        self.db = db
        self.item_repo = RecognitionItemRepository(db)

    def export_to_excel(
        self,
        task_id: int,
        invoice_type: str
    ) -> BytesIO:
        """
        导出为 Excel

        Args:
            task_id: 任务 ID
            invoice_type: 发票类型

        Returns:
            Excel 文件的字节流
        """
        # 获取任务的所有识别结果
        items = self.item_repo.get_by_task(task_id)

        # 创建工作簿
        wb = Workbook()
        ws = wb.active
        ws.title = "识别结果"

        # 根据发票类型设置表头
        headers = self._get_headers_for_invoice_type(invoice_type)
        ws.append(headers)

        # 写入数据
        for item in items:
            # 使用复核后的结果
            result = item.reviewed_result
            row = self._extract_row_data(result, invoice_type, item)
            ws.append(row)

        # 保存到字节流
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        return output

    def export_to_csv(
        self,
        task_id: int,
        invoice_type: str
    ) -> BytesIO:
        """
        导出为 CSV

        Args:
            task_id: 任务 ID
            invoice_type: 发票类型

        Returns:
            CSV 文件的字节流
        """
        # 获取任务的所有识别结果
        items = self.item_repo.get_by_task(task_id)

        # 创建 CSV（使用 StringIO 而非 BytesIO）
        from io import StringIO
        string_output = StringIO()
        writer = csv.writer(string_output)

        # 写入表头
        headers = self._get_headers_for_invoice_type(invoice_type)
        writer.writerow(headers)

        # 写入数据
        for item in items:
            result = item.reviewed_result
            row = self._extract_row_data(result, invoice_type, item)
            writer.writerow(row)

        # 转换为 BytesIO
        output = BytesIO()
        output.write(string_output.getvalue().encode('utf-8-sig'))  # 使用 utf-8-sig 以支持 Excel 打开
        output.seek(0)
        return output

    def _get_headers_for_invoice_type(self, invoice_type: str) -> List[str]:
        """获取发票类型对应的表头"""
        if invoice_type == "vat_special":
            return [
                "发票代码",
                "发票号码",
                "开票日期",
                "购买方名称",
                "购买方税号",
                "购买方地址电话",
                "购买方开户行账号",
                "销售方名称",
                "销售方税号",
                "销售方地址电话",
                "销售方开户行账号",
                "不含税金额",
                "税额",
                "价税合计",
                "价税合计大写",
                "可抵扣税额",
                "收款人",
                "复核人",
                "开票人",
                "备注",
                "置信度"
            ]
        elif invoice_type == "vat_normal":
            return [
                "发票代码",
                "发票号码",
                "开票日期",
                "购买方名称",
                "购买方税号",
                "购买方地址电话",
                "购买方开户行账号",
                "销售方名称",
                "销售方税号",
                "销售方地址电话",
                "销售方开户行账号",
                "项目名称",
                "不含税金额",
                "税率",
                "税额",
                "价税合计",
                "价税合计大写",
                "可抵扣税额",
                "收款人",
                "复核人",
                "开票人",
                "备注",
                "置信度"
            ]
        elif invoice_type == "railway_ticket":
            return [
                "发票类型",
                "发票号码",
                "开票日期",
                "车次",
                "出发站",
                "发车日期",
                "座位等级",
                "票价",
                "可抵扣税额",
                "乘车人",
                "电子客票号",
                "购买方名称",
                "购买方信用代码",
                "置信度"
            ]
        else:
            return ["数据", "置信度"]

    def _extract_row_data(self, result: dict, invoice_type: str, item=None) -> List[str]:
        """从结果中提取行数据"""
        from app.services.recognition.deductible_tax import calculate_deductible_tax

        confidence = ""
        if item and hasattr(item, 'confidence_score') and item.confidence_score is not None:
            confidence = f"{item.confidence_score * 100:.1f}%"

        # 计算可抵扣税额
        deductible = calculate_deductible_tax(result, invoice_type)
        deductible_str = f"{deductible:.2f}" if deductible > 0 else ""

        if invoice_type == "vat_special":
            return [
                result.get("invoice_code", ""),
                result.get("invoice_number", ""),
                result.get("invoice_date", ""),
                result.get("buyer_name", ""),
                result.get("buyer_tax_id", ""),
                result.get("buyer_address_phone", ""),
                result.get("buyer_bank_account", ""),
                result.get("seller_name", ""),
                result.get("seller_tax_id", ""),
                result.get("seller_address_phone", ""),
                result.get("seller_bank_account", ""),
                result.get("amount_excluding_tax", ""),
                result.get("tax_amount", ""),
                result.get("total_amount", ""),
                result.get("total_amount_cn", ""),
                deductible_str,
                result.get("payee", ""),
                result.get("reviewer", ""),
                result.get("issuer", ""),
                result.get("remark", ""),
                confidence
            ]
        elif invoice_type == "vat_normal":
            return [
                result.get("invoice_code", ""),
                result.get("invoice_number", ""),
                result.get("invoice_date", ""),
                result.get("buyer_name", ""),
                result.get("buyer_tax_id", ""),
                result.get("buyer_address_phone", ""),
                result.get("buyer_bank_account", ""),
                result.get("seller_name", ""),
                result.get("seller_tax_id", ""),
                result.get("seller_address_phone", ""),
                result.get("seller_bank_account", ""),
                result.get("item_name", ""),
                result.get("amount_excluding_tax", ""),
                result.get("tax_rate", ""),
                result.get("tax_amount", ""),
                result.get("total_amount", ""),
                result.get("total_amount_cn", ""),
                deductible_str,
                result.get("payee", ""),
                result.get("reviewer", ""),
                result.get("issuer", ""),
                result.get("remark", ""),
                confidence
            ]
        elif invoice_type == "railway_ticket":
            return [
                result.get("invoice_type", ""),
                result.get("invoice_number", ""),
                result.get("invoice_date", ""),
                result.get("train_number", ""),
                result.get("departure_station", ""),
                result.get("train_date", ""),
                result.get("seat_class", ""),
                result.get("ticket_price", ""),
                deductible_str,
                result.get("passenger_name", ""),
                result.get("ticket_id", ""),
                result.get("buyer_name", ""),
                result.get("buyer_credit_code", ""),
                confidence
            ]
        else:
            return [str(result), confidence]
