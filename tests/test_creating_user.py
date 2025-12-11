# tests/test_creating_user.py
import allure
import pytest
from data.api_information import ResponseCode, ResponseMessages
from helpers.helpers import User
from helpers.requests import creating_new_user


class TestCreateUser:

    @allure.title('Создание уникального пользователя - успешно')
    @allure.description('Проверка успешного создания уникального пользователя с валидными данными')
    def test_create_unique_user_success(self, user_factory):
        """
        Тест создает пользователя и проверяет успешность создания.
        Использует user_factory, так как создание пользователя - часть теста.
        Очистка выполняется автоматически в фикстуре user_factory.
        """
        # ЧАСТЬ ТЕСТА: Создание пользователя через фабрику
        payload, response = user_factory()
        
        with allure.step("Проверить, что код ответа 200 ОК"):
            assert response.status_code == ResponseCode.OK, (
                f"Ожидался код {ResponseCode.OK}, получен {response.status_code}"
            )
        
        with allure.step("Проверить структуру ответа"):
            response_data = response.json()
            assert response_data.get("success") is True, "Флаг success должен быть True"
            assert "accessToken" in response_data, "В ответе должен быть accessToken"
            assert "refreshToken" in response_data, "В ответе должен быть refreshToken"
            assert "user" in response_data, "В ответе должен быть объект user"
        
        with allure.step("Проверить данные пользователя в ответе"):
            user_data = response_data["user"]
            assert user_data.get("email") == payload["email"], "Email должен совпадать"
            assert user_data.get("name") == payload["name"], "Name должен совпадать"
        
        # Очистка выполняется автоматически в фикстуре user_factory

    @allure.title('Создание пользователя без email - ошибка 403')
    @allure.description('Проверка ошибки при создании пользователя без email (согласно документации API)')
    def test_create_user_without_email_should_fail(self):
        """
        Тест атомарен: создает данные без email и проверяет ошибку.
        Не требует очистки, так как пользователь не создается.
        """
        payload = User.create_user_without_email()
        
        with allure.step("Попытка создания пользователя без email"):
            response = creating_new_user(payload)
        
        # Согласно документации: если нет одного из полей → 403 Forbidden
        assert response.status_code == ResponseCode.FORBIDDEN, (
            f"Ожидался код {ResponseCode.FORBIDDEN}, получен {response.status_code}"
        )
        assert response.json().get("success") == False, "Флаг success должен быть False"
        assert response.json().get("message") == ResponseMessages.MISSING_FIELDS

    @allure.title('Создание пользователя без пароля - ошибка 403')
    @allure.description('Проверка ошибки при создании пользователя без пароля (согласно документации API)')
    def test_create_user_without_password_should_fail(self):
        """
        Тест атомарен: создает данные без пароля и проверяет ошибку.
        Не требует очистки, так как пользователь не создается.
        """
        payload = User.create_user_without_password()
        
        with allure.step("Попытка создания пользователя без пароля"):
            response = creating_new_user(payload)
        
        # Согласно документации: если нет одного из полей → 403 Forbidden
        assert response.status_code == ResponseCode.FORBIDDEN, (
            f"Ожидался код {ResponseCode.FORBIDDEN}, получен {response.status_code}"
        )
        assert response.json().get("success") == False, "Флаг success должен быть False"
        assert response.json().get("message") == ResponseMessages.MISSING_FIELDS

    @allure.title('Создание пользователя без имени - ошибка 403')
    @allure.description('Проверка ошибки при создании пользователя без имени (согласно документации API)')
    def test_create_user_without_name_should_fail(self):
        """
        Тест атомарен: создает данные без имени и проверяет ошибку.
        Не требует очистки, так как пользователь не создается.
        """
        payload = User.create_user_without_name()
        
        with allure.step("Попытка создания пользователя без имени"):
            response = creating_new_user(payload)
        
        # Согласно документации: если нет одного из полей → 403 Forbidden
        assert response.status_code == ResponseCode.FORBIDDEN, (
            f"Ожидался код {ResponseCode.FORBIDDEN}, получен {response.status_code}"
        )
        assert response.json().get("success") == False, "Флаг success должен быть False"
        assert response.json().get("message") == ResponseMessages.MISSING_FIELDS

    @allure.title('Создание уже существующего пользователя - ошибка 403')
    @allure.description('Проверка ошибки при создании уже существующего пользователя (согласно документации API)')
    def test_create_existing_user_should_fail(self, registered_user_for_login):
        """
        Тест использует фикстуру registered_user_for_login, которая:
        1. Создает пользователя как предусловие
        2. Автоматически удаляет его после теста
        
        Затем тест пытается создать пользователя с таким же email.
        """
        # ПРЕДУСЛОВИЕ: Пользователь уже создан фикстурой registered_user_for_login
        existing_user_payload = registered_user_for_login
        
        # ТЕСТ: Попытка создания пользователя с существующим email
        duplicate_payload = {
            "email": existing_user_payload["email"],  # Тот же email
            "password": "different_password",
            "name": "Different Name"
        }
        
        with allure.step("Попытка создания пользователя с существующим email"):
            second_response = creating_new_user(duplicate_payload)
        
        # Согласно документации: если пользователь существует → 403 Forbidden
        assert second_response.status_code == ResponseCode.FORBIDDEN, (
            f"Ожидался код {ResponseCode.FORBIDDEN}, получен {second_response.status_code}"
        )
        assert second_response.json().get("success") == False, "Флаг success должен быть False"
        assert second_response.json().get("message") == ResponseMessages.USER_ALREADY_EXISTS
        
       