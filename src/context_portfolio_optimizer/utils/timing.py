# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Timing utilities for ContextFusion."""

import time
from contextlib import contextmanager
from functools import wraps
from typing import Callable, TypeVar

F = TypeVar("F", bound=Callable)


class Timer:
    """Context manager for timing code blocks."""

    def __init__(self, name: str = ""):
        self.name = name
        self.start_time: float = 0.0
        self.elapsed: float = 0.0

    def __enter__(self) -> "Timer":
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, *args: object) -> None:
        self.elapsed = time.perf_counter() - self.start_time

    def __float__(self) -> float:
        return self.elapsed

    def __str__(self) -> str:
        name = f"{self.name}: " if self.name else ""
        return f"{name}{self.elapsed:.4f}s"


@contextmanager
def timed(name: str = ""):
    """Context manager for timing code blocks.

    Args:
        name: Optional name for the timer

    Yields:
        Timer instance
    """
    timer = Timer(name)
    timer.__enter__()
    try:
        yield timer
    finally:
        timer.__exit__(None, None, None)


def timed_function(func: F) -> F:
    """Decorator to time function execution.

    Args:
        func: Function to decorate

    Returns:
        Decorated function
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__}: {elapsed:.4f}s")
        return result

    return wrapper


def format_duration(seconds: float) -> str:
    """Format duration in human-readable form.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string
    """
    if seconds < 0.001:
        return f"{seconds * 1_000_000:.2f}µs"
    elif seconds < 1:
        return f"{seconds * 1_000:.2f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.1f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"
