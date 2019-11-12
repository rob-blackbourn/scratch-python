"""A CPU Monitor service"""

import asyncio
from asyncio import Event, Queue
from typing import Dict, List, Optional, Tuple

from .cpumon2 import cpu_percents, meminfo

class CPUMonService:
    """A CPU Monitor service"""

    def __init__(
            self,
            sample_duration: float,
            poll_duration: float
    ) -> None:
        self._sample_duration = sample_duration
        self._poll_duration = poll_duration
        self._listeners: List[Queue] = []
        self._cancellation_event = Event()

    def stop(self) -> None:
        self._cancellation_event.set()

    async def start(self):
        """Start the service"""
        print('starting')
        sample = await cpu_percents(self._sample_duration)
        memory = await meminfo()

        try:
            while not self._cancellation_event.is_set():
                await self._notify_listeners(sample, memory)
                try:
                    await asyncio.wait_for(
                        self._cancellation_event.wait(),
                        timeout=self._poll_duration
                    )
                except asyncio.TimeoutError:
                    sample = await cpu_percents(self._sample_duration)
                    memory = await meminfo()
        except Exception as error:
            print(error)
        print('stopped')

    def add_listener(self) -> Queue:
        """Add a listener"""
        listener: Queue = Queue()
        self._listeners.append(listener)
        return listener

    def remove_listener(self, listener: Queue) -> None:
        """Remove a listener"""
        self._listeners.remove(listener)

    async def _notify_listeners(
            self,
            sample: Dict[str, float],
            memory: Dict[str, Tuple[float, Optional[str]]]
    ) -> None:
        for listener in self._listeners:
            await listener.put({'sample': sample, 'memory': memory})
