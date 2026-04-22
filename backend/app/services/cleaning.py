import os
import zipfile
import py7zr
import rarfile
import shutil
import json
import magic
import threading
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import UploadFile
from app.models.cleaning_task import CleaningTask, CleaningStatus, ArchiveType
from app.repositories.cleaning_task import CleaningTaskRepository
from app.core.exceptions import ValidationException, NotFoundException


# 文件类型映射配置
TYPE_MAPPING = {
    "image": {
        "extensions": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".ico", ".tif", ".tiff"],
        "output_dir": "images"
    },
    "pdf": {
        "extensions": [".pdf"],
        "output_dir": "pdf"
    },
    "word": {
        "extensions": [".doc", ".docx", ".rtf", ".odt"],
        "output_dir": "word"
    },
    "excel": {
        "extensions": [".xls", ".xlsx", ".csv", ".ods"],
        "output_dir": "excel"
    },
    "ppt": {
        "extensions": [".ppt", ".pptx", ".odp"],
        "output_dir": "ppt"
    },
    "ofd": {
        "extensions": [".ofd"],
        "output_dir": "ofd"
    },
    "xml": {
        "extensions": [".xml"],
        "output_dir": "xml"
    }
}

# 安全过滤规则
SYSTEM_FILES = {".ds_store", "thumbs.db", "desktop.ini", ".gitkeep", ".gitignore"}
DANGEROUS_PATTERNS = ["../", "..\\", "/etc/", "/sys/", "/proc/", "c:\\windows", "c:\\system"]

# 限制配置
MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB
MAX_EXTRACTED_SIZE = 300 * 1024 * 1024  # 300MB
MAX_FILE_COUNT = 9999
MAX_DEPTH = 10

# 存储路径（使用相对路径，跟随 CWD）
UPLOAD_DIR = Path("storage/uploads")
EXTRACT_DIR = Path("storage/extracted")
RESULT_DIR = Path("storage/results")


class CleaningService:
    """文件清洗服务"""

    def __init__(self, db: Session):
        self.db = db
        self.repo = CleaningTaskRepository(db)
        self._ensure_directories()

    def _ensure_directories(self):
        """确保存储目录存在"""
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        EXTRACT_DIR.mkdir(parents=True, exist_ok=True)
        RESULT_DIR.mkdir(parents=True, exist_ok=True)

    def _detect_archive_type(self, filename: str) -> Optional[ArchiveType]:
        """检测压缩包类型"""
        ext = Path(filename).suffix.lower()
        if ext == ".zip":
            return ArchiveType.ZIP
        elif ext == ".7z":
            return ArchiveType.SEVENZIP
        elif ext == ".rar":
            return ArchiveType.RAR
        return None

    def _is_safe_path(self, path: str) -> bool:
        """检查路径是否安全"""
        path_lower = path.lower()
        # 检查危险模式
        for pattern in DANGEROUS_PATTERNS:
            if pattern in path_lower:
                return False
        # 检查系统文件
        filename = Path(path).name.lower()
        if filename in SYSTEM_FILES:
            return False
        # 检查隐藏文件
        if filename.startswith("."):
            return False
        return True

    def _match_file_type(self, filename: str, selected_types: List[str]) -> Optional[str]:
        """匹配文件类型"""
        ext = Path(filename).suffix.lower()
        for file_type in selected_types:
            if file_type in TYPE_MAPPING:
                if ext in TYPE_MAPPING[file_type]["extensions"]:
                    return file_type
        return None

    def _fix_zip_filename(self, zinfo: zipfile.ZipInfo) -> str:
        """修复 ZIP 文件名编码问题"""
        filename = zinfo.filename

        # 如果已经设置了 UTF-8 标志，直接使用
        if zinfo.flag_bits & 0x800:
            return filename

        # 否则尝试从 cp437 还原并用中文编码重新解码
        try:
            # 先按 cp437 编码回字节
            filename_bytes = filename.encode('cp437')

            # 尝试常见中文编码，优先 gbk（Windows 常用）
            candidates = []
            for encoding in ['gbk', 'gb18030', 'utf-8']:
                try:
                    decoded = filename_bytes.decode(encoding)
                    # 验证解码结果是否包含中文字符
                    if any('\u4e00' <= c <= '\u9fff' for c in decoded):
                        candidates.append((encoding, decoded))
                except (UnicodeDecodeError, UnicodeEncodeError):
                    continue

            # 如果有多个候选，选择最短的（通常是正确的）
            if candidates:
                # 按长度排序，选择最短的
                candidates.sort(key=lambda x: len(x[1]))
                encoding, decoded = candidates[0]
                print(f"[DEBUG] 文件名编码修复: {filename} -> {decoded} (使用 {encoding})")
                return decoded

            # 如果都失败，返回原始文件名
            return filename
        except Exception as e:
            print(f"[DEBUG] 文件名编码修复失败: {filename}, 错误: {e}")
            return filename

    def _extract_archive(self, archive_path: Path, extract_to: Path, archive_type: ArchiveType) -> int:
        """解压压缩包，返回解压后的总大小"""
        total_size = 0

        if archive_type == ArchiveType.ZIP:
            with zipfile.ZipFile(archive_path, 'r') as zf:
                for zinfo in zf.infolist():
                    # 阶段1: 读取源压缩包 entry 的原始文件名
                    original_name = zinfo.filename

                    # 阶段2: 修复编码后的文件名
                    fixed_name = self._fix_zip_filename(zinfo)

                    print(f"[DEBUG 阶段1] 原始文件名: {original_name}")
                    print(f"[DEBUG 阶段2] 修复后文件名: {fixed_name}")

                    # 使用修复后的文件名解压
                    zinfo.filename = fixed_name
                    zf.extract(zinfo, extract_to)

                    # 阶段3: 检查临时目录中实际落盘的文件名
                    extracted_path = extract_to / fixed_name
                    print(f"[DEBUG 阶段3] 落盘文件路径: {extracted_path}")

                    if extracted_path.is_file():
                        total_size += extracted_path.stat().st_size

        elif archive_type == ArchiveType.SEVENZIP:
            with py7zr.SevenZipFile(archive_path, 'r') as szf:
                szf.extractall(extract_to)
            for root, dirs, files in os.walk(extract_to):
                for file in files:
                    total_size += (Path(root) / file).stat().st_size

        elif archive_type == ArchiveType.RAR:
            with rarfile.RarFile(archive_path, 'r') as rf:
                rf.extractall(extract_to)
            for root, dirs, files in os.walk(extract_to):
                for file in files:
                    total_size += (Path(root) / file).stat().st_size

        return total_size

    def _traverse_and_collect(
        self,
        root_dir: Path,
        selected_types: List[str],
        depth: int = 0
    ) -> Tuple[List[Tuple[Path, str]], int, int]:
        """
        递归遍历并收集匹配的文件
        返回: (匹配文件列表, 总条目数, 跳过数)
        """
        matched_files = []
        total_entries = 0
        skipped_count = 0

        if depth > MAX_DEPTH:
            return matched_files, total_entries, skipped_count

        for item in root_dir.iterdir():
            total_entries += 1

            if total_entries > MAX_FILE_COUNT:
                raise ValidationException(detail=f"文件数量超过限制 {MAX_FILE_COUNT}")

            # 安全检查
            if not self._is_safe_path(str(item)):
                skipped_count += 1
                continue

            if item.is_file():
                file_type = self._match_file_type(item.name, selected_types)
                if file_type:
                    matched_files.append((item, file_type))
                else:
                    skipped_count += 1

            elif item.is_dir():
                sub_matched, sub_total, sub_skipped = self._traverse_and_collect(
                    item, selected_types, depth + 1
                )
                matched_files.extend(sub_matched)
                total_entries += sub_total
                skipped_count += sub_skipped

        return matched_files, total_entries, skipped_count

    def _create_result_archive(
        self,
        matched_files: List[Tuple[Path, str]],
        output_path: Path,
        task_id: int,
        task: CleaningTask
    ) -> Dict[str, int]:
        """
        创建结果压缩包，按类型扁平化输出
        返回: 各类型文件数量统计
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        base_dir = f"清洗后数据{timestamp}"
        matched_by_type = {}

        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
            file_counters = {}  # 用于处理重名文件

            for file_path, file_type in matched_files:
                output_dir = TYPE_MAPPING[file_type]["output_dir"]
                matched_by_type[file_type] = matched_by_type.get(file_type, 0) + 1

                # 处理重名文件
                original_name = file_path.name
                stem = file_path.stem
                suffix = file_path.suffix

                counter_key = f"{file_type}_{original_name}"
                if counter_key in file_counters:
                    file_counters[counter_key] += 1
                    new_name = f"{stem}_{file_counters[counter_key]}{suffix}"
                else:
                    file_counters[counter_key] = 0
                    new_name = original_name

                arcname = f"{base_dir}/{output_dir}/{new_name}"

                print(f"[DEBUG 阶段4] 写入结果 zip 的 arcname: {arcname}")

                # 使用 ZipInfo 并完整设置属性
                zip_info = zipfile.ZipInfo.from_file(file_path, arcname)
                zip_info.flag_bits |= 0x800  # 添加 UTF-8 标志
                with open(file_path, 'rb') as f:
                    zf.writestr(zip_info, f.read(), compress_type=zipfile.ZIP_DEFLATED)

            # 生成 manifest.json 并添加到 zip 包内
            manifest = {
                "task_id": task.id,
                "original_filename": task.original_filename,
                "archive_type": task.archive_type.value,
                "selected_types": task.selected_types,
                "total_entries": task.total_entries,
                "matched_count": len(matched_files),
                "matched_by_type": matched_by_type,
                "skipped_count": task.skipped_count,
                "created_at": task.created_at.isoformat(),
                "finished_at": datetime.now().isoformat()
            }
            manifest_json = json.dumps(manifest, ensure_ascii=False, indent=2)

            # manifest.json 也使用 UTF-8 标志
            manifest_info = zipfile.ZipInfo(f"{base_dir}/manifest.json")
            manifest_info.flag_bits = 0x800
            zf.writestr(manifest_info, manifest_json.encode('utf-8'))

        return matched_by_type

    async def create_task(
        self,
        user_id: int,
        file: UploadFile,
        selected_types: List[str]
    ) -> CleaningTask:
        """创建清洗任务"""
        # 验证文件类型
        archive_type = self._detect_archive_type(file.filename)
        if not archive_type:
            raise ValidationException(detail="不支持的压缩包格式，仅支持 zip/7z/rar")

        # 验证文件大小
        content = await file.read()
        if len(content) > MAX_UPLOAD_SIZE:
            raise ValidationException(detail=f"文件大小超过限制 {MAX_UPLOAD_SIZE // 1024 // 1024}MB")

        # 保存上传文件
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        upload_filename = f"{user_id}_{timestamp}_{file.filename}"
        upload_path = UPLOAD_DIR / upload_filename

        with open(upload_path, 'wb') as f:
            f.write(content)

        # 创建任务记录
        task = CleaningTask(
            user_id=user_id,
            original_filename=file.filename,
            archive_type=archive_type,
            selected_types=selected_types,
            status=CleaningStatus.UPLOADING,
            progress=5  # 初始进度 5%
        )
        task = self.repo.create(task)

        # 启动后台线程处理任务
        thread = threading.Thread(
            target=self._process_task_wrapper,
            args=(task.id, upload_path),
            daemon=True
        )
        thread.start()

        # 立即返回任务（此时状态为 UPLOADING，progress=5）
        return task

    def _process_task_wrapper(self, task_id: int, upload_path: Path):
        """后台任务包装器，捕获异常"""
        try:
            self._process_task(task_id, upload_path)
        except Exception as e:
            # 获取新的 DB session（线程安全）
            from app.db.session import SessionLocal
            db = SessionLocal()
            try:
                repo = CleaningTaskRepository(db)
                task = repo.get_by_id(task_id)
                if task:
                    task.status = CleaningStatus.FAILED
                    task.failed_reason = str(e)
                    task.finished_at = datetime.utcnow()
                    repo.update(task)
                db.commit()
            finally:
                db.close()

    def _process_task(self, task_id: int, upload_path: Path):
        """处理清洗任务"""
        # 获取新的 DB session（线程安全）
        from app.db.session import SessionLocal
        db = SessionLocal()

        try:
            repo = CleaningTaskRepository(db)
            task = repo.get_by_id(task_id)
            if not task:
                return

            # 更新状态为处理中
            task.status = CleaningStatus.PROCESSING
            task.progress = 10
            repo.update(task)
            db.commit()

            # 解压文件
            extract_path = EXTRACT_DIR / f"task_{task_id}"
            extract_path.mkdir(parents=True, exist_ok=True)

            extracted_size = self._extract_archive(upload_path, extract_path, task.archive_type)
            if extracted_size > MAX_EXTRACTED_SIZE:
                raise ValidationException(detail=f"解压后大小超过限制 {MAX_EXTRACTED_SIZE // 1024 // 1024}MB")

            task.progress = 30
            repo.update(task)
            db.commit()

            # 遍历并收集文件
            matched_files, total_entries, skipped_count = self._traverse_and_collect(
                extract_path, task.selected_types
            )

            task.total_entries = total_entries
            task.matched_count = len(matched_files)
            task.skipped_count = skipped_count
            task.progress = 60
            repo.update(task)
            db.commit()

            # 创建结果压缩包
            result_filename = f"cleaned_{task_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.zip"
            result_path = RESULT_DIR / result_filename

            matched_by_type = self._create_result_archive(matched_files, result_path, task_id, task)

            task.matched_by_type = matched_by_type
            task.result_zip_path = str(result_path)
            task.progress = 90
            repo.update(task)
            db.commit()

            # 完成
            task.status = CleaningStatus.DONE
            task.progress = 100
            task.finished_at = datetime.utcnow()
            repo.update(task)
            db.commit()

            # 清理临时文件
            shutil.rmtree(extract_path, ignore_errors=True)

        except Exception as e:
            task = repo.get_by_id(task_id)
            if task:
                task.status = CleaningStatus.FAILED
                task.failed_reason = str(e)
                task.finished_at = datetime.utcnow()
                repo.update(task)
                db.commit()
            raise
        finally:
            db.close()

    def get_user_tasks(self, user_id: int) -> List[CleaningTask]:
        """获取用户的任务列表"""
        return self.repo.get_by_user(user_id)

    def get_task_detail(self, task_id: int, user_id: int) -> CleaningTask:
        """获取任务详情"""
        task = self.repo.get_by_id_and_user(task_id, user_id)
        if not task:
            raise NotFoundException(detail="任务不存在")
        return task

    def retry_task(self, task_id: int, user_id: int) -> CleaningTask:
        """重试失败的任务"""
        task = self.repo.get_by_id_and_user(task_id, user_id)
        if not task:
            raise NotFoundException(detail="任务不存在")

        if task.status != CleaningStatus.FAILED:
            raise ValidationException(detail="只能重试失败的任务")

        # 重置状态
        task.status = CleaningStatus.PROCESSING
        task.progress = 0
        task.failed_reason = None
        task.finished_at = None
        self.repo.update(task)

        # 重新处理
        upload_path = UPLOAD_DIR / f"{task.user_id}_{task.created_at.strftime('%Y%m%d%H%M%S')}_{task.original_filename}"
        if upload_path.exists():
            self._process_task(task_id, upload_path)
        else:
            task.status = CleaningStatus.FAILED
            task.failed_reason = "原始文件已被清理"
            task.finished_at = datetime.utcnow()
            self.repo.update(task)

        return task

    def delete_task(self, task_id: int, user_id: int) -> bool:
        """物理删除任务及所有关联文件"""
        task = self.repo.get_by_id_and_user(task_id, user_id)
        if not task:
            raise NotFoundException(detail="任务不存在")
        return self._hard_delete_task(task)

    def _hard_delete_task(self, task: CleaningTask) -> bool:
        """物理删除：上传文件 + 结果文件 + 临时解压目录 + 数据库记录"""
        try:
            # 删除结果 zip
            if task.result_zip_path:
                result_path = Path(task.result_zip_path)
                if result_path.exists():
                    result_path.unlink()

            # 删除上传文件
            upload_pattern = f"{task.user_id}_*_{task.original_filename}"
            for f in UPLOAD_DIR.glob(upload_pattern):
                f.unlink()

            # 删除临时解压目录
            extract_path = EXTRACT_DIR / f"task_{task.id}"
            if extract_path.exists():
                shutil.rmtree(extract_path, ignore_errors=True)

            # 物理删除数据库记录
            self.db.delete(task)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Delete cleaning task {task.id} failed: {e}")
            return False

    def get_all_tasks(self) -> List[CleaningTask]:
        """获取所有任务（管理员）"""
        return self.repo.get_all_tasks()

    def admin_delete_tasks(self, task_ids: List[int]) -> int:
        """批量物理删除任务（管理员）"""
        deleted_count = 0
        for task_id in task_ids:
            task = self.repo.get_by_id(task_id)
            if task and self._hard_delete_task(task):
                deleted_count += 1
        return deleted_count
