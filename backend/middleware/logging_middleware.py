import time
import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("banking_ai_platform")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = str(uuid.uuid4())[:8]
        start = time.time()
        response = await call_next(request)
        elapsed_ms = round((time.time() - start) * 1000, 2)
        logger.info(
            f"request_id={request_id} method={request.method} path={request.url.path} "
            f"status={response.status_code} execution_time_ms={elapsed_ms}"
        )
        response.headers["X-Request-ID"] = request_id
        return response
