from app.core.config import settings


def setup_telemetry():
    if settings.SENTRY_DSN:
        try:
            import sentry_sdk
            sentry_sdk.init(
                dsn=settings.SENTRY_DSN,
                traces_sample_rate=1.0 if settings.DEBUG else 0.1,
            )
        except ImportError:
            pass