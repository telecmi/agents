#
# Copyright (c) 2024–2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

import sys

from piopiy.services import DeprecatedModuleProxy

from typing import cast
from types import ModuleType
from .tts import *

sys.modules[__name__] = cast(ModuleType, DeprecatedModuleProxy(globals(), "kokoro", "kokoro.[tts]"))
