"""Timing and profiling utilities for OpenVTO."""

from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Callable, TypeVar

T = TypeVar("T")


@dataclass
class TimingResult:
    """Result from a timed operation.

    Attributes:
        name: Name/label of the operation.
        duration_ms: Duration in milliseconds.
        start_time: Start timestamp.
        end_time: End timestamp.
    """

    name: str
    duration_ms: float
    start_time: float
    end_time: float

    @property
    def duration_seconds(self) -> float:
        """Duration in seconds."""
        return self.duration_ms / 1000


@dataclass
class PipelineTimings:
    """Accumulated timings for a pipeline run.

    Attributes:
        steps: List of timing results for each step.
        total_ms: Total duration in milliseconds.
    """

    steps: list[TimingResult] = field(default_factory=list)
    total_ms: float = 0.0

    def add(self, result: TimingResult) -> None:
        """Add a timing result."""
        self.steps.append(result)
        self.total_ms += result.duration_ms

    def get(self, name: str) -> TimingResult | None:
        """Get timing result by name."""
        for step in self.steps:
            if step.name == name:
                return step
        return None

    def summary(self) -> dict[str, float]:
        """Get summary dict of step name -> duration_ms."""
        return {step.name: step.duration_ms for step in self.steps}

    def __str__(self) -> str:
        """Format timings as string."""
        lines = [f"Total: {self.total_ms:.1f}ms"]
        for step in self.steps:
            pct = (step.duration_ms / self.total_ms * 100) if self.total_ms > 0 else 0
            lines.append(f"  {step.name}: {step.duration_ms:.1f}ms ({pct:.1f}%)")
        return "\n".join(lines)


class Timer:
    """Simple timer for measuring elapsed time.

    Example:
        >>> timer = Timer()
        >>> timer.start()
        >>> # ... do work ...
        >>> elapsed = timer.stop()
        >>> print(f"Took {elapsed:.1f}ms")
    """

    def __init__(self) -> None:
        self._start_time: float | None = None
        self._end_time: float | None = None

    def start(self) -> "Timer":
        """Start the timer."""
        self._start_time = time.perf_counter()
        self._end_time = None
        return self

    def stop(self) -> float:
        """Stop the timer and return elapsed milliseconds."""
        if self._start_time is None:
            raise RuntimeError("Timer was not started")
        self._end_time = time.perf_counter()
        return self.elapsed_ms

    @property
    def elapsed_ms(self) -> float:
        """Get elapsed time in milliseconds."""
        if self._start_time is None:
            return 0.0
        end = self._end_time or time.perf_counter()
        return (end - self._start_time) * 1000

    @property
    def elapsed_seconds(self) -> float:
        """Get elapsed time in seconds."""
        return self.elapsed_ms / 1000

    def result(self, name: str) -> TimingResult:
        """Get timing result object."""
        if self._start_time is None or self._end_time is None:
            raise RuntimeError("Timer was not started/stopped")
        return TimingResult(
            name=name,
            duration_ms=self.elapsed_ms,
            start_time=self._start_time,
            end_time=self._end_time,
        )


@contextmanager
def timed(name: str = "operation"):
    """Context manager for timing a block of code.

    Args:
        name: Name/label for the operation.

    Yields:
        TimingResult that will be populated on exit.

    Example:
        >>> with timed("image_generation") as t:
        ...     generate_image()
        >>> print(f"Took {t.duration_ms:.1f}ms")
    """
    result = TimingResult(
        name=name,
        duration_ms=0.0,
        start_time=time.perf_counter(),
        end_time=0.0,
    )
    try:
        yield result
    finally:
        result.end_time = time.perf_counter()
        result.duration_ms = (result.end_time - result.start_time) * 1000


def measure(func: Callable[..., T]) -> Callable[..., tuple[T, float]]:
    """Decorator to measure function execution time.

    Args:
        func: Function to measure.

    Returns:
        Wrapped function that returns (result, elapsed_ms).

    Example:
        >>> @measure
        ... def slow_function():
        ...     time.sleep(0.1)
        ...     return "done"
        >>> result, elapsed = slow_function()
        >>> print(f"Result: {result}, took {elapsed:.1f}ms")
    """

    def wrapper(*args, **kwargs) -> tuple[T, float]:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed_ms = (time.perf_counter() - start) * 1000
        return result, elapsed_ms

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


def format_duration(ms: float) -> str:
    """Format duration in human-readable form.

    Args:
        ms: Duration in milliseconds.

    Returns:
        Formatted string (e.g., "1.5s", "250ms", "2m 30s").
    """
    if ms < 1000:
        return f"{ms:.0f}ms"
    elif ms < 60000:
        return f"{ms / 1000:.1f}s"
    else:
        minutes = int(ms // 60000)
        seconds = (ms % 60000) / 1000
        return f"{minutes}m {seconds:.0f}s"


class Profiler:
    """Simple profiler for tracking multiple operations.

    Example:
        >>> profiler = Profiler()
        >>> with profiler.track("step1"):
        ...     do_step1()
        >>> with profiler.track("step2"):
        ...     do_step2()
        >>> print(profiler.report())
    """

    def __init__(self) -> None:
        self._timings = PipelineTimings()

    @contextmanager
    def track(self, name: str):
        """Track timing for a named operation."""
        with timed(name) as result:
            yield result
        self._timings.add(result)

    @property
    def timings(self) -> PipelineTimings:
        """Get accumulated timings."""
        return self._timings

    def report(self) -> str:
        """Get formatted timing report."""
        return str(self._timings)

    def reset(self) -> None:
        """Reset all timings."""
        self._timings = PipelineTimings()
