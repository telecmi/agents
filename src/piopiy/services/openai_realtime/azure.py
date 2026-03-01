#
# Copyright (c) 2024-2026, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

"""Azure OpenAI Realtime LLM service implementation."""

import warnings

from piopiy.services.azure.realtime.llm import *

with warnings.catch_warnings():
    warnings.simplefilter("always")
    warnings.warn(
        "Types in piopiy.services.openai_realtime.azure are deprecated. "
        "Please use the equivalent types from "
        "piopiy.services.azure.realtime.llm instead.",
        DeprecationWarning,
        stacklevel=2,
    )
