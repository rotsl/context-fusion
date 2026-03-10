# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""ContextFusion - Context Portfolio Optimizer for LLMs.

A framework for optimizing LLM context usage across heterogeneous data sources.
"""

from .orchestration.runner import PipelineRunner
from .version import VERSION, __version__

__all__ = ["VERSION", "__version__", "PipelineRunner"]
