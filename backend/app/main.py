from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.responses import error_response
from app.api.v1 import api_router
from app.db.session import engine, SessionLocal
from app.models.base import BaseModel

# 创建数据库表
BaseModel.metadata.create_all(bind=engine)


def recover_stuck_tasks():
    """恢复卡在 processing/uploading 状态的任务（服务重启后）"""
    from pathlib import Path
    from app.models.recognition_task import RecognitionTask, TaskStatus

    db = SessionLocal()
    try:
        stuck = db.query(RecognitionTask).filter(
            RecognitionTask.status.in_([TaskStatus.PROCESSING, TaskStatus.UPLOADING]),
            RecognitionTask.deleted_at.is_(None)
        ).all()

        if not stuck:
            return

        print(f"[启动恢复] 发现 {len(stuck)} 个卡住的任务，逐个重新处理...")

        for task in stuck:
            file_path = Path(task.file_path) if task.file_path else None
            if not file_path or not file_path.exists():
                # 文件不存在，标记失败
                task.status = TaskStatus.FAILED
                task.error_message = "服务重启后文件不存在，无法恢复"
                task.progress = 100
                db.commit()
                print(f"  任务 {task.id} ({task.original_filename}): 文件不存在，标记失败")
                continue

            # 重置为 uploading 状态，启动后台线程重新处理
            task.status = TaskStatus.UPLOADING
            task.progress = 5
            task.error_message = None
            db.commit()

            from app.services.task_processor import TaskProcessor
            TaskProcessor.start_processing(task.id, file_path)
            print(f"  任务 {task.id} ({task.original_filename}): 已重新提交处理")

    except Exception as e:
        print(f"[启动恢复] 恢复卡住任务失败: {e}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时恢复卡住的任务
    recover_stuck_tasks()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if hasattr(exc, "status_code"):
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(error=str(exc.detail))
        )
    return JSONResponse(
        status_code=500,
        content=error_response(error="服务器内部错误")
    )

# 路由
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "Invoice Platform API"}


@app.get("/health")
def health():
    return {"status": "ok"}
