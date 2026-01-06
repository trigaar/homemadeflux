from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Optional

from home_made_flux.core.logic import ScheduleDecision


@dataclass
class SchedulerResult:
    decision: ScheduleDecision
    applied: bool
    timestamp: datetime
    message: str


class Scheduler:
    """
    Periodically evaluates and applies Night Light state.

    The tick callable must return a SchedulerResult. An optional callback can
    consume the result for UI updates.
    """

    def __init__(
        self,
        interval_minutes: int,
        tick: Callable[[], SchedulerResult],
        callback: Optional[Callable[[SchedulerResult], None]] = None,
    ) -> None:
        self.interval_minutes = interval_minutes
        self.tick = tick
        self.callback = callback
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        while not self._stop_event.is_set():
            result = self.tick()
            if self.callback:
                self.callback(result)
            time.sleep(max(self.interval_minutes * 60, 1))

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2)

    def trigger_once(self) -> SchedulerResult:
        result = self.tick()
        if self.callback:
            self.callback(result)
        return result
