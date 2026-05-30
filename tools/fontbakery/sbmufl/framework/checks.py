from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any, cast

from fontbakery.prelude import FAIL, WARN, Message
from fontbakery.prelude import check as fontbakery_check
from fontbakery.utils import bullet_list

CheckResult = tuple[Any, Message]
CheckIterator = Iterator[CheckResult]


def check(
    *args: Any, **kwargs: Any
) -> Callable[[Callable[..., CheckIterator]], object]:
    return cast(
        Callable[[Callable[..., CheckIterator]], object],
        fontbakery_check(*args, **kwargs),
    )


def fail(code: str, message: str) -> CheckResult:
    return FAIL, Message(code, message)


def warn(code: str, message: str) -> CheckResult:
    return WARN, Message(code, message)


def bullet_list_text(config: Any, items: list[str]) -> str:
    return cast(str, bullet_list(config, items))


def fail_list(code: str, message: str, config: Any, items: list[str]) -> CheckResult:
    return fail(code, f"{message}\n\n{bullet_list_text(config, items)}")


def warn_list(code: str, message: str, config: Any, items: list[str]) -> CheckResult:
    return warn(code, f"{message}\n\n{bullet_list_text(config, items)}")
