"""
PDF 转换器

将 PDF 转换为图片
"""
from typing import List
import io
from PIL import Image
import fitz  # PyMuPDF


class PDFConverter:
    """PDF 转换器"""

    def convert_to_images(
        self,
        pdf_data: bytes,
        dpi: int = 200
    ) -> List[bytes]:
        """
        将 PDF 转换为图片列表

        Args:
            pdf_data: PDF 文件数据
            dpi: 分辨率

        Returns:
            图片数据列表（每页一张图片）
        """
        images = []

        # 打开 PDF
        pdf_document = fitz.open(stream=pdf_data, filetype="pdf")

        try:
            # 遍历每一页
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]

                # 设置缩放比例以达到指定 DPI
                zoom = dpi / 72  # 72 是 PDF 的默认 DPI
                mat = fitz.Matrix(zoom, zoom)

                # 渲染页面为图片
                pix = page.get_pixmap(matrix=mat)

                # 转换为 PIL Image
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                # 转换为 bytes（使用 JPEG 格式，与正常识别流程一致）
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='JPEG', quality=95)
                img_byte_arr.seek(0)

                images.append(img_byte_arr.getvalue())

        finally:
            pdf_document.close()

        return images
