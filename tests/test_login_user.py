# tests/test_login_user.py
import allure
import pytest
from data.api_information import ResponseCode, ResponseMessages
from helpers.helpers import User
from helpers.requests import login_user


class TestLoginUser:

    @allure.title('Логин существующего пользователя - успешно')
    @allure.description('Проверка успешного логина существующего пользователя')
    def test_login_with_existing_user_success(self, registered_user_for_login):
        payload = registered_user_for_login
        
        with allure.step("Подготовить данные для логина"):
            login_payload = {
                "email": payload["email"],
                "password": payload["password"]
            }
        
        with allure.step("Отправить запрос на логин пользователя"):
            login_response = login_user(login_payload)
        
        with allure.step("Проверить успешный вход"):
            assert login_response.status_code == ResponseCode.OK, (
                f"Ожидался код {ResponseCode.OK}, получен {login_response.status_code}. "
                f"Ответ: {login_response.text}"
            )
            
            response_data = login_response.json()
            assert response_data.get("success") == True, "Флаг success должен быть True"
            assert "accessToken" in response_data, "В ответе должен быть accessToken"
            assert "refreshToken" in response_data, "В ответе должен быть refreshToken"
            assert response_data.get("user") is not None, "В ответе должен быть объект user"
            
            user_data = response_data["user"]
            assert user_data.get("email") == payload["email"], "Email должен совпадать"
            assert user_data.get("name") == payload["name"], "Name должен совпадать"

    @allure.title('Логин с невалидными данными - ошибка 401')
    @allure.description('Проверка ошибки при логине с неверными данными (согласно документации API)')
    def test_login_with_invalid_credentials_should_fail(self):
        invalid_credentials = User.create_invalid_login_credentials()
        
        with allure.step("Попытка логина с невалидными данными"):
            login_response = login_user(invalid_credentials)
        
        with allure.step("Проверить, что логин не удался"):
            # Согласно документации: если логин или пароль неверные → 401 Unauthorized
            assert login_response.status_code == ResponseCode.UNAUTHORIZED, (
                f"Ожидался код {ResponseCode.UNAUTHORIZED}, получен {login_response.status_code}"
            )
            
            response_data = login_response.json()
            assert response_data.get("success") == False, "Флаг success должен быть False"
            assert response_data.get("message") == ResponseMessages.INVALID_CREDENTIALS

    @allure.title('Логин без email - ошибка 401')
    @allure.description('Проверка ошибки при логине без email (согласно документации API)')
    def test_login_without_email_should_fail(self):
        """
        Согласно документации: если нет одного из полей → 401 Unauthorized
        """
        payload = User.create_user_without_email()
        
        with allure.step("Попытка логина без email"):
            login_response = login_user(payload)
        
        with allure.step("Проверить ошибку"):
            assert login_response.status_code == ResponseCode.UNAUTHORIZED, (
                f"Ожидался код {ResponseCode.UNAUTHORIZED}, получен {login_response.status_code}"
            )
            
            response_data = login_response.json()
            assert response_data.get("success") == False, "Флаг success должен быть False"
            assert response_data.get("message") == ResponseMessages.INVALID_CREDENTIALS

    @allure.title('Логин без пароля - ошибка 401')
    @allure.description('Проверка ошибки при логине без пароля (согласно документации API)')
    def test_login_without_password_should_fail(self):
        """
        Согласно документации: если нет одного из полей → 401 Unauthorized
        """
        payload = User.create_user_without_password()
        
        with allure.step("Попытка логина без пароля"):
            login_response = login_user(payload)
        
        with allure.step("Проверить ошибку"):
            assert login_response.status_code == ResponseCode.UNAUTHORIZED, (
                f"Ожидался код {ResponseCode.UNAUTHORIZED}, получен {login_response.status_code}"
            )
            
            response_data = login_response.json()
            assert response_data.get("success") == False, "Флаг success должен быть False"
            assert response_data.get("message") == ResponseMessages.INVALID_CREDENTIALS