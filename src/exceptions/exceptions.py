class BotConfigError(Exception):
    """Базовое исключение для работы с конфигурациями ботов"""

    pass


class BotConfigNotFoundError(BotConfigError):
    """Конфигурация не найдена"""

    pass


class BotConfigAlreadyExistsError(BotConfigError):
    """Конфигурация уже существует"""

    pass
