# helpers.py
from faker import Faker
import requests
from data.api_information import Endpoints, ResponseCode, ResponseMessages

class User:
    @staticmethod
    def create_data_correct_user():
        faker = Faker('ru_RU')
        data = {
            "email": faker.email(),
            "password": faker.password(),
            "name": faker.first_name()
        }
        return data

    @staticmethod
    def create_user_without_email():
        faker = Faker('ru_RU')
        data = {
            "password": faker.password(),
            "name": faker.first_name()
        }
        return data

    @staticmethod
    def create_user_without_password():
        faker = Faker('ru_RU')
        data = {
            "email": faker.email(),
            "name": faker.first_name()
        }
        return data

    @staticmethod
    def create_user_without_name():
        faker = Faker('ru_RU')
        data = {
            "email": faker.email(),
            "password": faker.password(),
        }
        return data

    @staticmethod
    def create_invalid_login_credentials():
        """
        Создает данные для невалидного входа (случайные email и пароль)
        Эти данные гарантированно не соответствуют существующему пользователю
        """
        faker = Faker('ru_RU')
        data = {
            "email": faker.email(),
            "password": faker.password()
        }
        return data

    @staticmethod
    def test_validate_user_created(response):
        return (response.status_code == ResponseCode.OK
                and response.json().get("success") is True)

    @staticmethod
    def test_validate_user_already_exists(response):
        return (response.status_code in (ResponseCode.FORBIDDEN, ResponseCode.BAD_REQUEST)
                and response.json().get("message") == ResponseMessages.USER_ALREADY_EXISTS)


class Ingredients:
    correct_ingredients_data = {
        "ingredients": ["61c0c5a71d1f82001bdaaa6d", "61c0c5a71d1f82001bdaaa72", "61c0c5a71d1f82001bdaaa72"]
    }

    incorrect_ingredients_data_hash = {
        "ingredients": ["123123123123", "Pushkin"]
    }

    incorrect_ingredients_data_without_filling = {
        "ingredients": []
    }


# Функции для работы с API
def creating_new_user(payload):
    """Создание нового пользователя"""
    response = requests.post(Endpoints.CREATING_USER, json=payload)
    return response


def login_user(payload):
    """Авторизация пользователя"""
    response = requests.post(Endpoints.LOGIN_USER, json=payload)
    return response


def create_order(payload, access_token=None):
    """Создание заказа"""
    headers = {}
    if access_token:
        # Токен УЖЕ содержит "Bearer ", поэтому используем как есть
        headers["Authorization"] = access_token
    response = requests.post(Endpoints.CREATE_ORDER, json=payload, headers=headers)
    return response


def get_ingredients():
    """Получение списка ингредиентов"""
    response = requests.get(Endpoints.GET_INGREDIENTS)
    return response


def delete_user(access_token):
    """Удаление пользователя"""
    # Токен УЖЕ содержит "Bearer ", поэтому используем как есть
    headers = {"Authorization": access_token}
    response = requests.delete(Endpoints.DELETE_USER, headers=headers)
    return response