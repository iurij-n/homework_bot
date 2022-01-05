class MyError(Exception):
    '''Пользовательское исключение'''

    def __init__(self, *args):
        self.message = args[0] if args else None
    def __str__(self):
        if self.message:
            return f"Ошибка: {self.message}"
        else:
            return f"Ошибка: число меньше пяти."





def somefunction(value):
    print('функция начала работать')
    if value < 5:
        raise MyError('Аргкмент меньше положеного')
    else:
        print('В функцию передано - ', value)


try:
    somefunction(3)
except MyError as e:
    print('Исключение поймано. ', e)