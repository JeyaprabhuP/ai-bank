import time
import logging

logger = logging.getLogger("banking_ai_platform")


class BaseAgent:
    name = "BaseAgent"

    def run(self, *args, **kwargs):
        start = time.time()
        try:
            result = self._execute(*args, **kwargs)
            elapsed = round((time.time() - start) * 1000, 2)
            logger.info(f"agent={self.name} status=success execution_time_ms={elapsed}")
            return result
        except Exception as e:
            elapsed = round((time.time() - start) * 1000, 2)
            logger.error(f"agent={self.name} status=error execution_time_ms={elapsed} error={e}")
            raise

    def _execute(self, *args, **kwargs):
        raise NotImplementedError
