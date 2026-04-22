"""
全局速率限制注册表

提供进程级别的共享速率限制器，确保跨任务（跨线程、跨 event loop）的并发控制。

设计要点：
- 使用 threading.Semaphore 而非 asyncio.Semaphore，因为每个识别任务
  在独立线程 + 独立 event loop 中运行，asyncio.Semaphore 无法跨 event loop 共享
- 单例模式，进程级别唯一
- configure() 仅在并发数变化时重建信号量
- 配置 max_concurrency=2 表示最多 2 个请求同时发出，其余排队等待
"""
import threading
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class RateLimitRegistry:
    """全局速率限制注册表（单例，线程安全）"""

    _instance: Optional['RateLimitRegistry'] = None
    _init_lock = threading.Lock()

    def __new__(cls):
        with cls._init_lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._semaphore: Optional[threading.Semaphore] = None
        self._max_concurrency: int = 1
        self._config_lock = threading.Lock()
        self._initialized = True

    def configure(self, max_concurrency: int):
        """
        配置全局并发限制。
        仅在并发数实际变化时重建信号量，避免丢失排队状态。
        """
        with self._config_lock:
            if max_concurrency < 1:
                max_concurrency = 1
            if self._semaphore is not None and self._max_concurrency == max_concurrency:
                return
            self._max_concurrency = max_concurrency
            self._semaphore = threading.Semaphore(max_concurrency)
            logger.info(f"[RateLimit] 并发限制已配置: max_concurrency={max_concurrency}")

    def _ensure_semaphore(self):
        """确保信号量已初始化"""
        if self._semaphore is None:
            with self._config_lock:
                if self._semaphore is None:
                    self._semaphore = threading.Semaphore(self._max_concurrency)

    async def execute_with_limit(self, coro):
        """
        在速率限制下执行协程。
        acquire 阻塞当前线程直到有空位，执行完毕后 release 让排队的线程继续。
        """
        self._ensure_semaphore()
        self._semaphore.acquire()
        try:
            return await coro
        finally:
            self._semaphore.release()


# 全局单例实例
rate_limit_registry = RateLimitRegistry()
