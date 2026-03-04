"""
Logging Module
==============

Provides a centralized logger factory for the calculator application.

All modules obtain their logger via ``get_logger(name)`` so that the
entire application shares a consistent format, file handler, and log
level hierarchy.

Logger hierarchy
----------------
- ``calculator``          — root app logger
- ``calculator.history``  — LoggingObserver (existing)
- ``calculator.config``   — CalculatorConfig startup events
- ``calculator.repl``     — REPL command processing, errors, undo/redo
- ``calculator.memento``  — Undo/redo state transitions
"""

from __future__ import annotations

import logging
import os

# ---------------------------------------------------------------------------
# Module-level sentinel so we configure the root handler only once
# ---------------------------------------------------------------------------
_configured = False

_DEFAULT_LOG_DIR = "logs"
_DEFAULT_LOG_FILE = "calculator.log"
_DEFAULT_ENCODING = "utf-8"
_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_logging(
    log_dir: str = _DEFAULT_LOG_DIR,
    log_file: str = _DEFAULT_LOG_FILE,
    encoding: str = _DEFAULT_ENCODING,
    level: int = logging.DEBUG,
) -> None:
    """Configure the root ``calculator`` logger.

    Sets up a ``FileHandler`` and a ``StreamHandler`` (WARNING+) on the
    ``calculator`` parent logger.  Child loggers (``calculator.repl``,
    ``calculator.history``, etc.) inherit this configuration automatically.

    Safe to call multiple times — subsequent calls are no-ops unless
    *force* is used via ``reconfigure_logging()``.

    Args:
        log_dir: Directory where the log file is created.
        log_file: Name of the log file.
        encoding: File encoding for the log file.
        level: Minimum log level written to the file (default ``DEBUG``).
    """
    global _configured
    if _configured:
        return

    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, log_file)

    root = logging.getLogger("calculator")
    root.setLevel(level)

    formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)

    # File handler — captures DEBUG and above
    file_handler = logging.FileHandler(log_path, encoding=encoding)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    # Stream handler — only WARNING and above go to console
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.WARNING)
    stream_handler.setFormatter(formatter)
    root.addHandler(stream_handler)

    _configured = True


def reconfigure_logging(
    log_dir: str = _DEFAULT_LOG_DIR,
    log_file: str = _DEFAULT_LOG_FILE,
    encoding: str = _DEFAULT_ENCODING,
    level: int = logging.DEBUG,
) -> None:
    """Force-reconfigure the root ``calculator`` logger.

    Removes any existing handlers and re-applies configuration.  Useful
    when the ``CalculatorConfig`` has loaded a different log path.

    Args:
        log_dir: Directory where the log file is created.
        log_file: Name of the log file.
        encoding: File encoding for the log file.
        level: Minimum log level written to the file.
    """
    global _configured
    root = logging.getLogger("calculator")
    for handler in root.handlers[:]:
        handler.close()
        root.removeHandler(handler)
    _configured = False
    configure_logging(log_dir=log_dir, log_file=log_file, encoding=encoding, level=level)


def get_logger(name: str) -> logging.Logger:
    """Return a child logger under the ``calculator`` namespace.

    Args:
        name: Sub-logger name, e.g. ``"repl"`` → ``calculator.repl``.

    Returns:
        A ``logging.Logger`` instance.
    """
    return logging.getLogger(f"calculator.{name}")
