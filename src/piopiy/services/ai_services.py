#
# Copyright (c) 2024-2026, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

"""Deprecated AI services module.

This module is deprecated. Import services directly from their respective modules:
- piopiy.services.ai_service
- piopiy.services.image_service
- piopiy.services.llm_service
- piopiy.services.stt_service
- piopiy.services.tts_service
- piopiy.services.vision_service
"""

import sys

from piopiy.services import DeprecatedModuleProxy

from .ai_service import *
from .image_service import *
from .llm_service import *
from .stt_service import *
from .tts_service import *
from .vision_service import *

sys.modules[__name__] = DeprecatedModuleProxy(
    globals(),
    "ai_services",
    "[ai_service,image_service,llm_service,stt_service,tts_service,vision_service]",
)
