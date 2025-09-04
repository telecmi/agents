# piopiy/services/opensource/kokoro/__init__.py

from .tts import *   # load KokoroTTSService and others into namespace

import sys
from piopiy.services import DeprecatedModuleProxy

# Wrap this module in a proxy so you can warn about deprecated paths
sys.modules[__name__] = DeprecatedModuleProxy(globals(), "kokoro", "kokoro.tts")