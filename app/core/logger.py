import logging

from app.core.config import settings


def configure_logger():
    try:
        import colorlog

        handler = colorlog.StreamHandler()
        handler.setFormatter(
            colorlog.ColoredFormatter(
                fmt="%(log_color)s[%(asctime)s.%(msecs)03d] %(module)20s:%(lineno)-3d %(levelname)8s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "bold_red",
                },
            )
        )

        logger = logging.getLogger()
        logger.setLevel(settings.log_level)
        logger.handlers.clear()
        logger.addHandler(handler)

    except ImportError:
        logging.basicConfig(
            level=settings.log_level,
            datefmt="%Y-%m-%d %H:%M:%S",
            format="[%(asctime)s.%(msecs)03d] %(module)20s:%(lineno)-3d %(levelname)8s - %(message)s",
        )
