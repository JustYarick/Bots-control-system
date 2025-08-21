class FeatureFlagAlreadyExistsError(Exception):
    """Исключение для случая, когда feature flag уже существует"""

    pass


class FeatureFlagNotFoundError(Exception):
    """Исключение для случая, когда feature flag не найден"""

    pass
