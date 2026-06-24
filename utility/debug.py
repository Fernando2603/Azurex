import functools
import time
from collections.abc import Callable

from config import DEBUG_RUNTIME, DEBUG_VERBOSE

# later, kinda hard to implement, printing everywhere just gonna break the performance
if DEBUG_VERBOSE:

  def debug(message: str) -> None:
    print(message)

else:

  def debug(message: str) -> None:  # pyright: ignore[reportUnusedParameter]
    pass


def runtime[**P, R](func: Callable[P, R]) -> Callable[P, R]:
  if not DEBUG_RUNTIME:
    return func

  @functools.wraps(func)
  def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
    start = time.perf_counter_ns()

    try:
      return func(*args, **kwargs)

    except BaseException as e:
      raise e

    finally:
      duration = time.perf_counter_ns() - start
      minutes, rem = divmod(duration, 60_000_000_000)
      seconds, rem = divmod(rem, 1_000_000_000)
      millis, nanos = divmod(rem, 1_000_000)

      parts: list[str] = []

      if minutes:
        parts.append(f"{minutes}m")

      if seconds or minutes:
        parts.append(f"{seconds}s")

      parts.append(f"{millis}ms")
      parts.append(f"{nanos:06d}ns")

      print(f"[{func.__name__}] took {' '.join(parts)}")

  return wrapper
