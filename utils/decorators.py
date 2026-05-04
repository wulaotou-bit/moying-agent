"""
墨影装饰器库
工业级自动重试装饰器
"""
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log,
    retry_if_exception_type,
    RetryError
)
from utils.logger import log
import openai

# 可重试的异常类型（只重试网络/IO/API异常，不重试语法错误等）
RETRYABLE_EXCEPTIONS = (
    ConnectionError,
    TimeoutError,
    IOError,
    OSError,
    openai.APIError,
    openai.APIConnectionError,
    openai.RateLimitError,
    openai.APITimeoutError
)

def auto_retry(func):
    """
    工业级自动重试装饰器
    特性：3次重试 + 指数退避 + 详细日志 + 异常分类
    适用：AI调用、网络请求、爬虫、文件读写
    """
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(RETRYABLE_EXCEPTIONS),
        before_sleep=before_sleep_log(log, log.level("WARNING")),
        reraise=True
    )
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RetryError as e:
            log.critical(f"❌ 【{func.__name__}】重试3次全部失败！终止执行")
            log.critical(f"失败原因: {str(e.last_attempt.exception())}")
            raise
        except Exception as e:
            log.error(f"⚠️ 【{func.__name__}】执行失败: {str(e)}")
            raise
    return wrapper