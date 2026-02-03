"""Async task wrapper for DB/network calls."""

import logging
from typing import Callable, Any, Optional
from PySide6.QtCore import QObject, QThread, Signal, QRunnable, QThreadPool

logger = logging.getLogger(__name__)


class WorkerSignals(QObject):
    """Signals for worker threads."""
    finished = Signal()
    error = Signal(str)
    result = Signal(object)
    progress = Signal(int)


class AsyncWorker(QRunnable):
    """Async worker for background tasks."""
    
    def __init__(self, fn: Callable, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
    
    def run(self):
        """Execute the function."""
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.signals.result.emit(result)
        except Exception as e:
            logger.error(f"Error in async worker: {e}")
            self.signals.error.emit(str(e))
        finally:
            self.signals.finished.emit()


class AsyncTaskManager:
    """Manages async tasks."""
    
    def __init__(self):
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(4)
    
    def execute(self, fn: Callable, *args, **kwargs) -> WorkerSignals:
        """Execute a function asynchronously."""
        worker = AsyncWorker(fn, *args, **kwargs)
        self.thread_pool.start(worker)
        return worker.signals


# Global instance
async_task_manager = AsyncTaskManager()

