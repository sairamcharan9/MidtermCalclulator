"""
Calculator Configuration Management
=====================================

Loads and validates application configuration from environment variables.
"""

from __future__ import annotations

import os
from typing import Final

from dotenv import load_dotenv

from app.core.exceptions import ConfigurationError


class CalculatorConfig:
    """
    Loads, validates, and provides access to calculator settings from the environment.
    """

    _VALID_ENCODINGS: Final[tuple[str, ...]] = (
        "utf-8", "utf-16", "utf-32", "ascii", "latin-1", "iso-8859-1"
    )
    _MAX_PRECISION: Final[int] = 20

    def __init__(self, env_path: str | None = None) -> None:
        load_dotenv(dotenv_path=env_path, override=True)

        self.log_dir: str = os.getenv("CALCULATOR_LOG_DIR", "logs")
        self.log_file: str = os.getenv("CALCULATOR_LOG_FILE", "calculator.log")
        self.history_dir: str = os.getenv("CALCULATOR_HISTORY_DIR", "data")
        self.history_file: str = os.getenv("CALCULATOR_HISTORY_FILE", "history.csv")

        self.max_history_size: int = self._parse_positive_int(
            os.getenv("CALCULATOR_MAX_HISTORY_SIZE", "1000"), "CALCULATOR_MAX_HISTORY_SIZE"
        )
        self.auto_save: bool = self._parse_bool(
            os.getenv("CALCULATOR_AUTO_SAVE", "true"), "CALCULATOR_AUTO_SAVE"
        )
        self.precision: int = self._parse_non_negative_int(
            os.getenv("CALCULATOR_PRECISION", "2"), "CALCULATOR_PRECISION"
        )
        self.max_input_value: float = self._parse_float(
            os.getenv("CALCULATOR_MAX_INPUT_VALUE", "1e10"), "CALCULATOR_MAX_INPUT_VALUE"
        )
        self.default_encoding: str = os.getenv("CALCULATOR_DEFAULT_ENCODING", "utf-8")

        self.validate()

    def validate(self) -> None:
        if not self.log_dir.strip():
            raise ConfigurationError("CALCULATOR_LOG_DIR must not be empty.")
        if not self.log_file.strip():
            raise ConfigurationError("CALCULATOR_LOG_FILE must not be empty.")
        if not self.history_dir.strip():
            raise ConfigurationError("CALCULATOR_HISTORY_DIR must not be empty.")
        if not self.history_file.strip():
            raise ConfigurationError("CALCULATOR_HISTORY_FILE must not be empty.")
        if self.precision > self._MAX_PRECISION:
            raise ConfigurationError(
                f"CALCULATOR_PRECISION must be <= {self._MAX_PRECISION}, got {self.precision}."
            )
        if self.max_input_value <= 0:
            raise ConfigurationError(
                f"CALCULATOR_MAX_INPUT_VALUE must be positive, got {self.max_input_value}."
            )
        if self.default_encoding.lower() not in self._VALID_ENCODINGS:
            raise ConfigurationError(
                f"Unsupported encoding: '{self.default_encoding}'. Must be one of: "
                f"{', '.join(self._VALID_ENCODINGS)}."
            )

    @staticmethod
    def _parse_bool(value: str, name: str) -> bool:
        normalized_value = value.strip().lower()
        if normalized_value in ("true", "1", "yes"):
            return True
        if normalized_value in ("false", "0", "no"):
            return False
        raise ConfigurationError(f"Invalid boolean value for {name}: '{value}'. Use 'true' or 'false'.")

    @staticmethod
    def _parse_positive_int(value: str, name: str) -> int:
        try:
            num = int(value)
            if num <= 0:
                raise ConfigurationError(f"{name} must be a positive integer, got {num}.")
            return num
        except ValueError:
            raise ConfigurationError(f"Invalid integer value for {name}: '{value}'.")

    @staticmethod
    def _parse_non_negative_int(value: str, name: str) -> int:
        try:
            num = int(value)
            if num < 0:
                raise ConfigurationError(f"{name} must be a non-negative integer, got {num}.")
            return num
        except ValueError:
            raise ConfigurationError(f"Invalid integer value for {name}: '{value}'.")

    @staticmethod
    def _parse_float(value: str, name: str) -> float:
        try:
            return float(value)
        except ValueError:
            raise ConfigurationError(f"Invalid float value for {name}: '{value}'.")

    def __repr__(self) -> str:
        return (
            "CalculatorConfig("
            f"log_dir='{self.log_dir}', "
            f"log_file='{self.log_file}', "
            f"history_dir='{self.history_dir}', "
            f"history_file='{self.history_file}', "
            f"max_history_size={self.max_history_size}, "
            f"auto_save={self.auto_save}, "
            f"precision={self.precision}, "
            f"max_input_value={self.max_input_value}, "
            f"default_encoding='{self.default_encoding}'"
            ")"
        )
