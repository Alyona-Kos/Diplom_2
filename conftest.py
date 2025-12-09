# conftest.py
import pytest
import requests
import allure
from helpers.helpers import User, creating_new_user, delete_user
from data.api_information import Endpoints, ResponseCode

@pytest.fixture
def user_with_cleanup():
    """
    Фикстура создает уникального пользователя и гарантирует его удаление после теста
    """
    # Генерируем уникальные данные
    payload = User.create_data_correct_user()
    
    with allure.step(f"Создание тестового пользователя: {payload['email']}"):
        response = creating_new_user(payload)
    
    yield payload, response
    
    # Удаление пользователя в блоке finally
    with allure.step(f"Очистка: удаление пользователя {payload['email']}"):
        try:
            # Пытаемся получить токен для удаления
            if response.status_code == ResponseCode.OK:
                token = response.json().get("accessToken")
                if token:
                    delete_response = delete_user(token)
                    if delete_response.status_code != ResponseCode.OK:
                        print(f"Warning: Failed to delete user {payload['email']}")
        except Exception as e:
            print(f"Error during cleanup for {payload['email']}: {e}")

@pytest.fixture
def create_new_user():
    """
    Фикстура для простого создания пользователя без cleanup
    """
    def _create_user(payload):
        return creating_new_user(payload)
    return _create_user