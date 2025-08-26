# # src/sentry_config.py
# import sentry_sdk
# from sentry_sdk.integrations.fastapi import FastApiIntegration
# from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
# from loguru import logger
#
# # from sentry_sdk.integrations.redis import RedisIntegration
# from sentry_sdk.integrations.logging import LoggingIntegration
#
# from src.config import settings
#
# _sentry_initialized = False
#
#
# def init_sentry():
#     global _sentry_initialized
#     if _sentry_initialized:
#         logger.warning("Sentry already initialized")
#         return
#
#     """Инициализация Sentry"""
#     if not settings.sentry.sentry_dsn:
#         logger.warning("Sentry DSN not configured, skipping Sentry initialization")
#         return
#
#     sentry_sdk.init(
#         dsn=settings.sentry.sentry_dsn,
#         integrations=[
#             FastApiIntegration(transaction_style="endpoint"),
#             SqlalchemyIntegration(),
#             # RedisIntegration(),
#             LoggingIntegration(
#                 level=None,
#                 event_level=None,
#             ),
#         ],
#         auto_enabling_integrations=False,
#         traces_sample_rate=settings.sentry.sentry_traces_sample_rate,
#         profiles_sample_rate=1.0,
#         environment=settings.sentry.sentry_environment,
#         attach_stacktrace=True,
#         send_default_pii=False,
#         before_send_transaction=lambda event, hint: (
#             None if event["transaction"] == "GET /health" else event
#         ),
#     )
#
#     logger.success(f"Sentry initialized with environment: {settings.sentry.sentry_environment}")
