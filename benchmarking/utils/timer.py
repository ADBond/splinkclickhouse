import time
from dataclasses import dataclass
from typing import Optional

import pandas as pd


@dataclass
class TimePoint:
    time: float
    label: str
    time_index: Optional[int] = None


class Timer:
    def __init__(self, name: str, data: str):
        self.name = name
        self.data = data
        self.timings: list[TimePoint] = []
        self.append_time("timer_initialised")

    def append_time(self, label: str):
        t = time.time()
        self.timings.append(TimePoint(t, label))

    @property
    def time_diffs(self):
        initial_time = self.timings[0].time
        time_diffs = []
        total = 0
        for i, time_point in enumerate(self.timings):
            time = time_point.time
            label = time_point.label
            time_diff = time - initial_time
            time_for_step = TimePoint(time_diff, label, i)
            time_diffs.append(time_for_step)
            total += time_diff
            initial_time = time
        time_diffs.append(TimePoint(total, "__total", -1))
        return time_diffs

    def summarise_times(self):
        total = 0
        for time_point in self.time_diffs:
            time = time_point.time
            label = time_point.label
            print(f"{time:.2f} s for step: {label}")  # noqa: T201
        total = sum(time_point.time for time_point in self.time_diffs)
        print(f"{total:.2f} s total time\n")  # noqa: T201

    @property
    def labels(self):
        return {t.label for t in self.timings}

    @property
    def records(self) -> list[dict]:
        return [
            {
                "label": time_point.label,
                "time": time_point.time,
                "name": self.name,
                "data": self.data,
                "time_index": time_point.time_index,
            }
            for time_point in self.time_diffs
        ]


class MultiTimer:
    def __init__(self, timers: list[Timer]):
        self.timers = timers
        if not all(timer.labels == self.timers[0].labels for timer in self.timers):
            raise ValueError(
                "Can't make a MultiTimer with Timers with different labels"
            )

    @property
    def records(self) -> list[dict]:
        return [r for timer in self.timers for r in timer.records]

    @property
    def timing_frame(self) -> pd.DataFrame:
        df = pd.DataFrame(self.records)
        df.sort_values(by=["time_index", "name"], inplace=True)
        return df
