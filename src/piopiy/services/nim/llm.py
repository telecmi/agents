#
# Copyright (c) 2024-2026, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

"""NVIDIA NIM API service implementation.

This module provides a service for interacting with NVIDIA's NIM (NVIDIA Inference
Microservice) API while maintaining compatibility with the OpenAI-style interface.

.. deprecated:: 0.0.96
    This module is deprecated. Please NvidiaLLMService from
    piopiy.services.nvidia.llm instead.
"""

import warnings

from piopiy.services.nvidia.llm import NvidiaLLMService

with warnings.catch_warnings():
    warnings.simplefilter("always")
    warnings.warn(
        "NimLLMService from piopiy.services.nim.llm is deprecated. "
        "Please use NvidiaLLMService from piopiy.services.nvidia.llm instead.",
        DeprecationWarning,
        stacklevel=2,
    )

NimLLMService = NvidiaLLMService
