#
# Copyright (c) 2024-2026, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

"""Event-based notifier implementation using asyncio Event primitives."""

import warnings

from piopiy.utils.sync.event_notifier import EventNotifier

with warnings.catch_warnings():
    warnings.simplefilter("always")
    warnings.warn(
        "Package piopiy.sync is deprecated, use piopiy.utils.sync instead.",
        DeprecationWarning,
        stacklevel=2,
    )
