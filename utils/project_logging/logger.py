import os
import sys
from distutils.util import strtobool
from typing import Union

from loguru import logger


def get_loguru_config(
    use_default_prod_configuration: bool = strtobool(
        os.getenv("LOGGING_DEFAULT_PROD_CONF", "TRUE")
    ),
    level: Union[None, str, int] = os.getenv("LOGGING_LEVEL", "INFO"),
    extra: bool = True,
) -> dict:
    """
    Возвращает словарь с к конфигурацией логера Loguru, в зависимости от среды эксплуатации и доп. параметров.

    :param use_default_prod_configuration: Автоматически применяются настройки для боевого режима: Вывод в json формат; ERROR и CRITICAL логи выводятся в stderr. Если True - Все остальные параметры (кроме level) игнорируются
    :param level: уровень логирования
    :param extra:  будет ли в вывод добавляться словарь с extra параметрами
    :param notify_with_telegram: Надо ли отправлять уведомления об ошибках через телегу. Если да, то должны быть определены переменные окружения BOT_TOKEN и SUBSCRIBER_CHAT_ID
    :return:
    """

    if use_default_prod_configuration:

        config = {
            "handlers": [
                {
                    "sink": sys.stderr,
                    "format": "",
                    "serialize": True,
                    "level": "ERROR",
                },
                {
                    "sink": sys.stdout,
                    "format": "",
                    "serialize": True,
                    "level": level,
                    "filter": _stdout_filter,
                },
            ]
        }
    else:

        extra_vars_substring = " |{extra}" if extra else ""

        config = {
            "handlers": [
                {
                    "sink": sys.stdout,
                    "level": level,
                    "format": "<level>{level: <8}</level>|<cyan>{name:<12}</cyan>:<cyan>{function:<24}</cyan>:<cyan>{line}</cyan> - <level>{message:>32}</level>"
                    + extra_vars_substring,
                },
            ],
        }

    return config


def _stdout_filter(record):
    return record["level"].no <= logger.level("WARNING").no
