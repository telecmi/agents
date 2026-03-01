#
# Copyright (c) 2024-2026, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

"""Event models and data structures for OpenAI Realtime API communication."""

import warnings

from piopiy.services.openai.realtime.events import *

with warnings.catch_warnings():
    warnings.simplefilter("always")
    warnings.warn(
        "Types in piopiy.services.openai_realtime.events are deprecated. "
        "Please use the equivalent types from "
        "piopiy.services.openai.realtime.events instead.",
        DeprecationWarning,
        stacklevel=2,
    )
