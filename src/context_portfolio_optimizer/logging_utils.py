# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Logging utilities for ContextFusion."""

import logging
import sys
from typing import Any

from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme

# Custom theme for rich output
CUSTOM_THEME = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "red bold",
    "critical": "red bold reverse",
    "success": "green",
    "debug": "dim",
})

console = Console(theme=CUSTOM_THEME)


def setup_logging(
    level: int = logging.INFO,
    use_rich: bool = True,
    log_file: str | None = None,
) -> logging.Logger:
    """Set up logging for ContextFusion.

    Args:
        level: Logging level
        use_rich: Whether to use rich formatting
        log_file: Optional file to log to

    Returns:
        Configured logger
    """
    logger = logging.getLogger("context_portfolio_optimizer")
    logger.setLevel(level)
    logger.handlers = []  # Clear existing handlers

    if use_rich:
        handler: logging.Handler = RichHandler(
            console=console,
            rich_tracebacks=True,
            show_time=True,
            show_path=False,
        )
        formatter = logging.Formatter("%(message)s")
    else:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    handler.setLevel(level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        )
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name, defaults to root CPO logger

    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(f"context_portfolio_optimizer.{name}")
    return logging.getLogger("context_portfolio_optimizer")


class ProgressLogger:
    """Context manager for logging progress."""

    def __init__(self, message: str, logger: logging.Logger | None = None):
        self.message = message
        self.logger = logger or get_logger()
        self.start_time: float | None = None

    def __enter__(self) -> "ProgressLogger":
        import time

        self.start_time = time.time()
        self.logger.info(f"Starting: {self.message}")
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        import time

        elapsed = time.time() - (self.start_time or 0)
        if exc_type:
            self.logger.error(f"Failed: {self.message} ({elapsed:.2f}s)")
        else:
            self.logger.info(f"Completed: {self.message} ({elapsed:.2f}s)")

    def log_step(self, step: str) -> None:
        """Log a step within the progress."""
        self.logger.debug(f"  → {step}")
