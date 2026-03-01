#
# Copyright (c) 2024-2026, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

"""Custom frames for AWS Nova Sonic LLM service."""

import warnings

from piopiy.services.aws.nova_sonic.frames import *

with warnings.catch_warnings():
    warnings.simplefilter("always")
    warnings.warn(
        "Types in piopiy.services.aws_nova_sonic.frames are deprecated. "
        "Please use the equivalent types from "
        "piopiy.services.aws.nova_sonic.frames instead.",
        DeprecationWarning,
        stacklevel=2,
    )
