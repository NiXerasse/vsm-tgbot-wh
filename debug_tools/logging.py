import asyncio
from contextlib import asynccontextmanager, contextmanager
from functools import wraps
from typing import Callable

from logger.logger import logger


def log_func(msg: str):
    def decorator(func: Callable):
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            logger.warning(f'Starting {msg}')
            result = func(*args, **kwargs)
            logger.warning(f'Finished {msg}')

            return result

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger.warning(f'Starting {msg}')
            result = await func(*args, **kwargs)
            logger.warning(f'Finished {msg}')

            return result

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator

@asynccontextmanager
async def async_log_context(msg: str, data=None, data_descr=None, warning=False):
    _p = logger.warning if warning else logger.info
    _p(f'Starting {msg}')
    if data is not None:
        _p(f'{data_descr}: {data}')
    try:
        yield
    except:
        raise
    _p(f'Finished {msg}')

@contextmanager
def log_context(msg: str, data=None, data_descr=None, warning=False):
    _p = logger.warning if warning else logger.info
    _p(f'Starting {msg}')
    if data is not None:
        _p(f'{data_descr}: {data}')
    try:
        yield
    except:
        raise
    _p(f'Finished {msg}')
