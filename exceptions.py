class GetAPIAnswerError(Exception):
    """Ошибка при получении ответа API."""

    pass


class CheckResponseError(Exception):
    """Ошибка проверки ответа API."""

    pass


class ParseStatusError(Exception):
    """Ошибка извлечения данных их ответа API."""

    pass


class EmptyDictError(Exception):
    """API вернул пустой словарь."""

    pass


class KeyHomeworksError(Exception):
    """В словаре нет ключа homeworks."""

    pass


class TypeDictError(Exception):
    """Неверный тип словаря."""

    pass


class TimestampError(Exception):
    """Не удалось получить временную метку."""

    pass


class HomeworkTypeError(Exception):
    """Элемент списка не словарь."""

    pass
