import os

from httpx import Request
from limits import parse
from limits.storage import MemoryStorage
from limits.strategies import FixedWindowRateLimiter
from slowapi.util import get_remote_address
from strawberry.extensions import SchemaExtension

RATE_LIMITING_ENABLED = os.getenv("RATE_LIMITING_ENABLED", "true").lower() == "true"

LIMITS = {
    "query": parse("120/minute"),
    "mutation": parse("30/minute"),
}

storage = MemoryStorage()
moving_window = FixedWindowRateLimiter(storage)


class RateLimitError(Exception):
    def __init__(self, operation_type: str, limit: str, retry_after: float):
        self.operation_type = operation_type
        self.limit = limit
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded for {operation_type}: {limit}")


def get_client_key(request: Request) -> str:
    return request.headers.get("X-User-Id", get_remote_address(request))


class RateLimitExtension(SchemaExtension):
    async def on_execute(self) -> None:
        if not RATE_LIMITING_ENABLED:
            return
        request: Request = self.execution_context.context.request
        client_key = get_client_key(request)

        operation = self.execution_context.operation_type

        limit = LIMITS.get(operation.value)
        if limit:
            limit_str = f"{limit.amount}/{limit.GRANULARITY.name}"
            limit_key = f"{operation.value}:{client_key}"

            if not moving_window.hit(limit, limit_key):
                remaining = moving_window.get_window_stats(limit, limit_key)
                raise RateLimitError(
                    operation_type=operation.value,
                    limit=limit_str,
                    retry_after=remaining.reset_time,
                )
