import allure
import pytest
import requests
from data.api_information import Endpoints, ResponseCode, ResponseMessages
from helpers.helpers import User  # Исправлен импорт - из helpers.helpers

class TestLoginUser:

    @allure.title(
        'При отправке запроса на авторизацию пользователя в веб-сервисе - код ответа 200 ОК, пользователь логинится')
    @allure.description('В рамках данного тест-кейса проверяется, '
                        'что при отправке запроса на авторизацию пользователя в веб-сервисе - код ответа 200 ОК, пользователь логинится')
    def test_login_with_existing_user_success(self, user_with_cleanup):
        with allure.step("Отправить запрос на создание пользователя"):
            payload, create_response = user_with_cleanup

        with allure.step("Подготовить данные для логина"):
            login_payload = {
                "email": payload["email"],
                "password": payload["password"]
            }

        with allure.step("Отправить запрос на логин пользователя в веб-сервисе"):
            login_response = requests.post(Endpoints.LOGIN_USER, json=login_payload)

        with allure.step("Проверить успешный вход"):
            assert login_response.status_code == ResponseCode.OK
            assert login_response.json().get("success") == True
            assert "accessToken" in login_response.json()
            assert "refreshToken" in login_response.json()
            assert login_response.json().get("user") is not None
            assert login_response.json()["user"]["email"] == payload["email"]
            assert login_response.json()["user"]["name"] == payload["name"]

    @allure.title(
        'При отправке запроса на авторизацию пользователя в веб-сервисе с невалидными данными - код ответа 401 Unauthorized, пользователь не логинится')
    @allure.description('В рамках данного тест-кейса проверяется, '
                        'что при отправке запроса на авторизацию пользователя в веб-сервисе с невалидными данными - код ответа 401 Unauthorized, пользователь не логинится')
    def test_login_with_invalid_credentials_should_fail(self):
        # Использование нового метода для создания невалидных данных для логина
        invalid_payload = User.create_invalid_login_credentials()
        
        with allure.step("Отправить запрос на логин пользователя с невалидными данными"):
            response = requests.post(Endpoints.LOGIN_USER, json=invalid_payload)
            
        with allure.step("Проверить, что код ответа соответствует 401 Unauthorized"):
            assert response.status_code == ResponseCode.UNAUTHORIZED
            assert response.json().get("success") == False
            assert response.json().get("message") == ResponseMessages.INVALID_CREDENTIALS