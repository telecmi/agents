#
# Copyright (c) 2024-2026, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

import sys

from piopiy.services import DeprecatedModuleProxy

from .video import *

sys.modules[__name__] = DeprecatedModuleProxy(globals(), "simli", "simli.video")
