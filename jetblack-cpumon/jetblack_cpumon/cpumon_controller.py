"""The controller for CPM monitor"""

import asyncio
import json
import logging
from typing import AsyncIterator, Dict, Optional

import pkg_resources

from bareasgi import (
    Application,
    Scope,
    Info,
    RouteMatches,
    Content,
    HttpResponse,
    text_writer
)

from .cpumon_service import CPUMonService

LOGGER = logging.getLogger(__name__)


class CPUMonController:
    """A controller"""

    def __init__(self):
        self._listener_count = 0
        self._service: Optional[CPUMonService] = None
        self._service_task: Optional[asyncio.Task] = None

    def add_routes(self, app: Application) -> None:
        app.http_router.add({'GET'}, '/', self.get_page)
        app.http_router.add({'GET'}, '/cpu', self.get_samples)

    async def get_samples(
            self,
            _scope: Scope,
            _info: Info,
            _matches: RouteMatches,
            _content: Content
    ) -> HttpResponse:
        headers = [
            (b'cache-control', b'no-cache'),
            (b'content-type', b'text/event-stream'),
            (b'connection', b'keep-alive')
        ]
        return 200, headers, self._send_samples()

    async def get_page(
            self,
            _scope: Scope,
            _info: Info,
            _matches: RouteMatches,
            _content: Content
    ) -> HttpResponse:
        filename = pkg_resources.resource_filename(__name__, "cpumon.html")
        with open(filename) as file_ptr:
            html = file_ptr.read()
        headers = [
            (b'content-type', b'text/html')
        ]
        return 200, headers, text_writer(html)

    async def _acquire_service(self) -> CPUMonService:
        if self._service is None:
            self._service = CPUMonService(1.0, 1.0)
        if self._listener_count == 0:
            self._service_task = asyncio.create_task(self._service.start())
        self._listener_count += 1
        return self._service

    async def _release_service(self) -> None:
        self._listener_count -= 1
        if self._listener_count == 0 and self._service is not None:
            self._service.stop()
        if self._service_task is not None:
            await self._service_task
        self._service = None
        self._service_task = None

    async def _send_samples(self) -> AsyncIterator[bytes]:
        service = await self._acquire_service()
        try:
            listener = service.add_listener()
            is_cancelled = False
            while not is_cancelled:
                try:
                    sample: Dict[str, float] = await listener.get()
                    LOGGER.debug('Sending event')
                    yield f'data: {json.dumps(sample)}\n\n\n'.encode('utf-8')
                    # Defeat buffering by giving the server a nudge.
                    yield ':\n\n\n'.encode('utf-8')
                except asyncio.CancelledError:
                    LOGGER.debug('Cancelled')
                    is_cancelled = True
                except:  # pylint: disable=bare-except
                    LOGGER.exception('Failed')
            service.remove_listener(listener)
        finally:
            await self._release_service()
