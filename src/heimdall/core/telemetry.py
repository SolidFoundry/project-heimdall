# --- START OF FILE heimdall/core/telemetry.py (复用自py_ai_core) ---

import logging
from fastapi import FastAPI

logger = logging.getLogger(__name__)


def setup_telemetry(app: FastAPI):
    """
    配置和启用 OpenTelemetry Tracing。
    注意：当前版本中此功能已暂时禁用，专注于核心功能。
    """
    logger.info("遥测功能已暂时禁用，专注于核心功能")
    # TODO: 在后续版本中重新启用 OpenTelemetry 功能
    pass


# --- END OF FILE heimdall/core/telemetry.py ---