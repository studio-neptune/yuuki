"""
Yuuki_Libs
(c) Neptune Studio.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator, Callable

from ..client import AsyncLineClient, LineClientError
from ..events.registry import Dispatcher
from ..model import Operation

logger = logging.getLogger(__name__)


class Polling:
    """Long-poll feed of operations with revision tracking and backoff."""

    def __init__(
        self,
        client: AsyncLineClient,
        *,
        revision: int | None = None,
        count: int = 50,
        backoff_start: float = 1.0,
        backoff_max: float = 30.0,
        guard: Callable[[], bool] | None = None,
    ) -> None:
        self.client = client
        self.revision = revision
        self.count = count
        self.backoff_start = backoff_start
        self.backoff_max = backoff_max
        self.guard = guard

    async def __aiter__(self) -> AsyncIterator[Operation]:
        assert self.revision is not None, "Revision is not initialized"
        backoff = self.backoff_start
        while self.guard is None or self.guard():
            try:
                operations = await self.client.fetch_operations(
                    self.revision, self.count
                )
                backoff = self.backoff_start
            except LineClientError:
                logger.exception("Polling failed, retrying in %.1fs", backoff)
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, self.backoff_max)
                continue
            for operation in operations:
                if operation.revision is not None:
                    self.revision = max(self.revision, operation.revision)
                yield operation

    async def run(self, dispatcher: Dispatcher) -> None:
        """Poll and dispatch until the client disconnects."""
        assert self.revision is not None
        async for operation in self:
            await dispatcher.dispatch(operation)
