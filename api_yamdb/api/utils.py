import random


def generate_confirmation_code():
    """
    Генерация случайного кода подтверждения из 6 цифр.
    """
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])
