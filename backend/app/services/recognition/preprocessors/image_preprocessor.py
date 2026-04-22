from pathlib import Path
from PIL import Image
import io
from app.services.recognition.preprocessors.base import FilePreprocessor, PreprocessorResult


class ImagePreprocessor(FilePreprocessor):
    """图片预处理器"""

    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}

    async def preprocess(self, file_path: Path) -> PreprocessorResult:
        """
        预处理图片文件

        Args:
            file_path: 图片文件路径

        Returns:
            预处理结果（单张图片）
        """
        # 读取图片
        with Image.open(file_path) as img:
            # 转换为 RGB 模式（去除 alpha 通道）
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = rgb_img
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            # 限制最大尺寸（避免图片过大导致 API 调用失败）
            max_size = 4096
            if img.width > max_size or img.height > max_size:
                ratio = min(max_size / img.width, max_size / img.height)
                new_size = (int(img.width * ratio), int(img.height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)

            # 转换为 JPEG 字节流
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=95)
            image_bytes = buffer.getvalue()

        return PreprocessorResult(
            images=[image_bytes],
            metadata={
                "page_count": 1,
                "original_format": file_path.suffix.lower()
            }
        )

    def supports_file_type(self, file_type: str) -> bool:
        """检查是否支持该文件类型"""
        return file_type == "image"
