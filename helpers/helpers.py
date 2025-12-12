import time
import uuid
from faker import Faker
import requests
from data.api_information import Endpoints, ResponseCode, ResponseMessages


class User:
    @staticmethod
    def create_data_correct_user():
        """
        Создает данные для корректного пользователя с гарантированно уникальным email
        """
        faker = Faker('ru_RU')
        timestamp = int(time.time() * 1000)
        unique_id = str(uuid.uuid4())[:8]  # Берем первые 8 символов UUID для уникальности
        base_email = faker.email().replace('@', f'.{timestamp}.{unique_id}@')
        data = {
            "email": f"test.user.{timestamp}.{unique_id}@{base_email.split('@')[1]}",
            "password": faker.password(),
            "name": faker.first_name()
        }
        return data

    @staticmethod
    def create_user_without_email():
        """
        Создает данные пользователя без email (для негативных тестов)
        """
        faker = Faker('ru_RU')
        data = {
            "password": faker.password(),
            "name": faker.first_name()
        }
        return data

    @staticmethod
    def create_user_without_password():
        """
        Создает данные пользователя без пароля (для негативных тестов)
        """
        faker = Faker('ru_RU')
        timestamp = int(time.time() * 1000)
        unique_id = str(uuid.uuid4())[:8]
        base_email = faker.email().replace('@', f'.{timestamp}.{unique_id}@')
        data = {
            "email": f"test.user.{timestamp}.{unique_id}@{base_email.split('@')[1]}",
            "name": faker.first_name()
        }
        return data

    @staticmethod
    def create_user_without_name():
        """
        Создает данные пользователя без имени (для негативных тестов)
        """
        faker = Faker('ru_RU')
        timestamp = int(time.time() * 1000)
        unique_id = str(uuid.uuid4())[:8]
        base_email = faker.email().replace('@', f'.{timestamp}.{unique_id}@')
        data = {
            "email": f"test.user.{timestamp}.{unique_id}@{base_email.split('@')[1]}",
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
        timestamp = int(time.time() * 1000)
        unique_id = str(uuid.uuid4())[:8]
        base_email = faker.email().replace('@', f'.{timestamp}.{unique_id}@')
        data = {
            "email": f"invalid.{timestamp}.{unique_id}@{base_email.split('@')[1]}",
            "password": faker.password()
        }
        return data

    @staticmethod
    def test_validate_user_created(response):
        """
        Проверяет, что пользователь успешно создан
        """
        return (response.status_code == ResponseCode.OK
                and response.json().get("success") is True)

    @staticmethod
    def test_validate_user_already_exists(response):
        """
        Проверяет, что пользователь уже существует
        """
        return (response.status_code in (ResponseCode.FORBIDDEN, ResponseCode.BAD_REQUEST)
                and response.json().get("message") == ResponseMessages.USER_ALREADY_EXISTS)


class Ingredients:
    """
    Класс для работы с данными ингредиентов
    """
    
    # Статические данные для тестов
    correct_ingredients_data = {
        "ingredients": ["61c0c5a71d1f82001bdaaa6d", "61c0c5a71d1f82001bdaaa72", "61c0c5a71d1f82001bdaaa72"]
    }

    incorrect_ingredients_data_hash = {
        "ingredients": ["123123123123", "Pushkin"]
    }

    incorrect_ingredients_data_without_filling = {
        "ingredients": []
    }
    
    @staticmethod
    def get_available_ingredients():
        """
        Получить доступные ингредиенты из API
        """
        response = requests.get(Endpoints.GET_INGREDIENTS)
        return response
    
    @staticmethod
    def get_valid_ingredient_ids(count=2):
        """
        Получить валидные ID ингредиентов
        """
        response = Ingredients.get_available_ingredients()
        if response.status_code == ResponseCode.OK:
            ingredients = response.json()["data"]
            if len(ingredients) >= count:
                return [ingredient["_id"] for ingredient in ingredients[:count]]
        return None