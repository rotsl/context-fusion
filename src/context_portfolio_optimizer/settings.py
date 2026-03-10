# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Settings and configuration for ContextFusion."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .constants import (
    DEFAULT_CACHE_DIR,
    DEFAULT_EXAMPLES_BUDGET,
    DEFAULT_INSTRUCTIONS_BUDGET,
    DEFAULT_MEMORY_BUDGET,
    DEFAULT_OUTPUT_RESERVE,
    DEFAULT_RETRIEVAL_BUDGET,
    DEFAULT_TELEMETRY_DIR,
    DEFAULT_TOOL_TRACE_BUDGET,
    DEFAULT_TOTAL_BUDGET,
)
from .exceptions import ConfigurationError


@dataclass
class BudgetSettings:
    """Token budget settings."""

    instructions: int = DEFAULT_INSTRUCTIONS_BUDGET
    retrieval: int = DEFAULT_RETRIEVAL_BUDGET
    memory: int = DEFAULT_MEMORY_BUDGET
    examples: int = DEFAULT_EXAMPLES_BUDGET
    tool_trace: int = DEFAULT_TOOL_TRACE_BUDGET
    output_reserve: int = DEFAULT_OUTPUT_RESERVE

    @classmethod
    def from_total(cls, total: int) -> "BudgetSettings":
        """Create budget settings from total budget.

        Args:
            total: Total token budget

        Returns:
            BudgetSettings with proportional allocation
        """
        ratio = total / DEFAULT_TOTAL_BUDGET
        return cls(
            instructions=int(DEFAULT_INSTRUCTIONS_BUDGET * ratio),
            retrieval=int(DEFAULT_RETRIEVAL_BUDGET * ratio),
            memory=int(DEFAULT_MEMORY_BUDGET * ratio),
            examples=int(DEFAULT_EXAMPLES_BUDGET * ratio),
            tool_trace=int(DEFAULT_TOOL_TRACE_BUDGET * ratio),
            output_reserve=int(DEFAULT_OUTPUT_RESERVE * ratio),
        )


@dataclass
class ScoringSettings:
    """Scoring model settings."""

    utility_weights: dict[str, float] = field(default_factory=lambda: {
        "retrieval": 0.25,
        "trust": 0.20,
        "freshness": 0.15,
        "structure": 0.15,
        "diversity": 0.15,
        "token_cost": -0.10,
    })
    risk_weights: dict[str, float] = field(default_factory=lambda: {
        "hallucination_proxy": 0.40,
        "staleness": 0.35,
        "privacy": 0.25,
    })
    reward_weights: dict[str, float] = field(default_factory=lambda: {
        "alpha": 1.0,
        "beta": 0.1,
        "gamma": 0.01,
        "delta": 0.5,
    })


@dataclass
class ProviderSettings:
    """LLM provider settings."""

    name: str = "mock"
    api_key: str | None = None
    base_url: str | None = None
    model: str = "default"
    timeout: int = 60
    max_retries: int = 3


@dataclass
class Settings:
    """Main settings class."""

    # Paths
    cache_dir: str = DEFAULT_CACHE_DIR
    memory_dir: str = DEFAULT_MEMORY_DIR
    telemetry_dir: str = DEFAULT_TELEMETRY_DIR

    # Budget
    budget: BudgetSettings = field(default_factory=BudgetSettings)

    # Scoring
    scoring: ScoringSettings = field(default_factory=ScoringSettings)

    # Provider
    provider: ProviderSettings = field(default_factory=ProviderSettings)

    # Features
    enable_telemetry: bool = True
    enable_ablations: bool = True
    enable_compression: bool = True

    # Logging
    log_level: str = "INFO"
    log_file: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Settings":
        """Create settings from dictionary.

        Args:
            data: Configuration dictionary

        Returns:
            Settings instance
        """
        settings = cls()

        if "paths" in data:
            paths = data["paths"]
            settings.cache_dir = paths.get("cache_dir", DEFAULT_CACHE_DIR)
            settings.memory_dir = paths.get("memory_dir", DEFAULT_MEMORY_DIR)
            settings.telemetry_dir = paths.get("telemetry_dir", DEFAULT_TELEMETRY_DIR)

        if "budget" in data:
            budget_data = data["budget"]
            if "total" in budget_data:
                settings.budget = BudgetSettings.from_total(budget_data["total"])
            else:
                settings.budget = BudgetSettings(
                    instructions=budget_data.get("instructions", DEFAULT_INSTRUCTIONS_BUDGET),
                    retrieval=budget_data.get("retrieval", DEFAULT_RETRIEVAL_BUDGET),
                    memory=budget_data.get("memory", DEFAULT_MEMORY_BUDGET),
                    examples=budget_data.get("examples", DEFAULT_EXAMPLES_BUDGET),
                    tool_trace=budget_data.get("tool_trace", DEFAULT_TOOL_TRACE_BUDGET),
                    output_reserve=budget_data.get("output_reserve", DEFAULT_OUTPUT_RESERVE),
                )

        if "scoring" in data:
            scoring_data = data["scoring"]
            settings.scoring = ScoringSettings(
                utility_weights=scoring_data.get("utility_weights", {}),
                risk_weights=scoring_data.get("risk_weights", {}),
                reward_weights=scoring_data.get("reward_weights", {}),
            )

        if "provider" in data:
            provider_data = data["provider"]
            settings.provider = ProviderSettings(
                name=provider_data.get("name", "mock"),
                api_key=provider_data.get("api_key"),
                base_url=provider_data.get("base_url"),
                model=provider_data.get("model", "default"),
                timeout=provider_data.get("timeout", 60),
                max_retries=provider_data.get("max_retries", 3),
            )

        if "features" in data:
            features = data["features"]
            settings.enable_telemetry = features.get("enable_telemetry", True)
            settings.enable_ablations = features.get("enable_ablations", True)
            settings.enable_compression = features.get("enable_compression", True)

        if "logging" in data:
            logging_data = data["logging"]
            settings.log_level = logging_data.get("level", "INFO")
            settings.log_file = logging_data.get("file")

        return settings

    @classmethod
    def from_yaml(cls, path: str | Path) -> "Settings":
        """Load settings from YAML file.

        Args:
            path: Path to YAML file

        Returns:
            Settings instance

        Raises:
            ConfigurationError: If file cannot be loaded
        """
        path = Path(path)
        if not path.exists():
            raise ConfigurationError(f"Config file not found: {path}")

        try:
            with open(path, "r") as f:
                data = yaml.safe_load(f)
            return cls.from_dict(data or {})
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in config file: {e}")

    @classmethod
    def from_env(cls) -> "Settings":
        """Load settings from environment variables.

        Returns:
            Settings instance
        """
        settings = cls()

        # Paths
        settings.cache_dir = os.getenv("CPO_CACHE_DIR", DEFAULT_CACHE_DIR)
        settings.memory_dir = os.getenv("CPO_MEMORY_DIR", DEFAULT_MEMORY_DIR)
        settings.telemetry_dir = os.getenv("CPO_TELEMETRY_DIR", DEFAULT_TELEMETRY_DIR)

        # Provider
        settings.provider.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        settings.provider.name = os.getenv("CPO_PROVIDER", "mock")
        settings.provider.model = os.getenv("CPO_MODEL", "default")

        # Logging
        settings.log_level = os.getenv("CPO_LOG_LEVEL", "INFO")

        return settings

    @classmethod
    def load(cls, config_path: str | Path | None = None) -> "Settings":
        """Load settings from config file and environment.

        Args:
            config_path: Optional path to config file

        Returns:
            Settings instance
        """
        # Start with defaults
        settings = cls()

        # Load from config file if provided or found
        if config_path:
            settings = cls.from_yaml(config_path)
        elif Path("configs/default.yaml").exists():
            settings = cls.from_yaml("configs/default.yaml")

        # Override with environment variables
        env_settings = cls.from_env()

        # Merge environment settings
        settings.cache_dir = env_settings.cache_dir
        settings.memory_dir = env_settings.memory_dir
        settings.telemetry_dir = env_settings.telemetry_dir
        if env_settings.provider.api_key:
            settings.provider.api_key = env_settings.provider.api_key
        if env_settings.provider.name != "mock":
            settings.provider.name = env_settings.provider.name
        settings.log_level = env_settings.log_level

        return settings

    @property
    def memory_path(self) -> Path:
        """Path to memory directory."""
        return Path(self.memory_dir)

    @property
    def cache_path(self) -> Path:
        """Path to cache directory."""
        return Path(self.cache_dir)

    @property
    def telemetry_path(self) -> Path:
        """Path to telemetry directory."""
        return Path(self.telemetry_dir)


# Global settings instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get global settings instance.

    Returns:
        Settings instance
    """
    global _settings
    if _settings is None:
        _settings = Settings.load()
    return _settings


def set_settings(settings: Settings) -> None:
    """Set global settings instance.

    Args:
        settings: Settings to set
    """
    global _settings
    _settings = settings
