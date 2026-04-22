from pathlib import Path
from PIL import Image
import io
import fitz  # PyMuPDF
from app.services.recognition.preprocessors.base import FilePreprocessor, PreprocessorResult


class PDFPreprocessor(FilePreprocessor):
    """PDF 预处理器"""

    async def preprocess(self, file_path: Path) -> PreprocessorResult:
        """
        预处理 PDF 文件（将每一页转换为图片）

        Args:
            file_path: PDF 文件路径

        Returns:
            预处理结果（多张图片，每页一张）
        """
        images = []

        # 打开 PDF
        pdf_document = fitz.open(file_path)
        page_count = pdf_document.page_count

        try:
            for page_num in range(page_count):
                # 获取页面
                page = pdf_document[page_num]

                # 设置缩放比例（提高分辨率）
                zoom = 2.0  # 2x 缩放
                mat = fitz.Matrix(zoom, zoom)

                # 渲染页面为图片
                pix = page.get_pixmap(matrix=mat)

                # 转换为 PIL Image
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                # 限制最大尺寸
                max_size = 4096
                if img.width > max_size or img.height > max_size:
                    ratio = min(max_size / img.width, max_size / img.height)
                    new_size = (int(img.width * ratio), int(img.height * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)

                # 转换为 JPEG 字节流
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=95)
                image_bytes = buffer.getvalue()

                images.append(image_bytes)

        finally:
            pdf_document.close()

        return PreprocessorResult(
            images=images,
            metadata={
                "page_count": page_count,
                "original_format": ".pdf"
            }
        )

    def supports_file_type(self, file_type: str) -> bool:
        """检查是否支持该文件类型"""
        return file_type == "pdf"
