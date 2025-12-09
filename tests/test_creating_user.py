import pytest
import allure
import requests
from helpers.helpers import User, creating_new_user
from data.api_information import ResponseCode, ResponseMessages, Endpoints


class TestCreatingUser:

    @allure.title(
        'При отправке запроса на создание уникального пользователя - код ответа 200 ОК, пользователь создаётся')
    @allure.description('В рамках данного тест-кейса проверяется, '
                        'что при отправке запроса на создание уникального пользователя - код ответа 200 ОК, пользователь создаётся')
    def test_create_unique_user_success(self, user_with_cleanup):
        with allure.step("Отправить POST-запрос на создание пользователя"):
            payload, response = user_with_cleanup
        with allure.step("Пользователь успешно создан"):
            assert response.status_code == ResponseCode.OK
            assert response.json().get("success") == True
            assert response.json().get("accessToken") is not None
            assert response.json().get("refreshToken") is not None
            assert response.json().get("user") is not None
            assert response.json()["user"]["email"] == payload["email"]
            assert response.json()["user"]["name"] == payload["name"]

    @allure.title(
        'При отправке запроса на создание пользователя с данными, которые уже существует в базе данных - код ответа 403 Forbidden, пользователь не создаётся')
    @allure.description('В рамках данного тест-кейса проверяется, '
                        'что при отправке запроса на создание пользователя с данными, которые уже существует в базе данных - код ответа 403 Forbidden, пользователь не создаётся')
    def test_create_existing_user_should_fail(self):
        """
        Независимый тест: создаем пользователя, потом пытаемся создать такого же
        """
        # 1. Создаем уникального пользователя
        payload = User.create_data_correct_user()
        
        with allure.step("Создать первого пользователя"):
            first_response = creating_new_user(payload)
            assert first_response.status_code == ResponseCode.OK
        
        # 2. Пытаемся создать такого же пользователя с теми же данными
        with allure.step("Попытаться создать пользователя с теми же данными"):
            second_response = creating_new_user(payload)
        
        with allure.step("Проверить, что второй пользователь не создан"):
            assert second_response.status_code == ResponseCode.FORBIDDEN
            assert second_response.json().get("success") == False
            assert second_response.json().get("message") == ResponseMessages.USER_ALREADY_EXISTS
        
        # 3. Очистка: пытаемся удалить созданного пользователя
        with allure.step("Очистка: удалить созданного пользователя"):
            try:
                if first_response.status_code == ResponseCode.OK:
                    token = first_response.json().get("accessToken")
                    if token:
                        delete_response = requests.delete(
                            Endpoints.DELETE_USER,
                            headers={"Authorization": f"Bearer {token}"}
                        )
                        if delete_response.status_code != ResponseCode.OK:
                            print(f"Warning: Failed to delete user {payload['email']}")
            except Exception as e:
                print(f"Error during cleanup for {payload['email']}: {e}")

    @allure.title(
        'При отправке запроса на создание пользователя без указания имени - код ответа 403 Forbidden, пользователь не создаётся')
    @allure.description('В рамках данного тест-кейса проверяется, '
                        'что при отправке запроса на создание пользователя без указания имени - код ответа 403 Forbidden, пользователь не создаётся')
    def test_create_user_without_name_should_fail(self, create_new_user):
        with allure.step("Отправить POST-запрос на создание пользователя без имени"):
            payload = User.create_user_without_name()
            response = create_new_user(payload)

        with allure.step("Проверить ошибку отсутствия обязательного поля"):
            assert response.status_code == ResponseCode.FORBIDDEN
            assert response.json().get("success") == False
            assert response.json().get("message") == ResponseMessages.MISSING_FIELDS

    @allure.title(
        'При отправке запроса на создание пользователя без указания email - код ответа 403 Forbidden, пользователь не создаётся')
    @allure.description('В рамках данного тест-кейса проверяется, '
                        'что при отправке запроса на создание пользователя без указания email - код ответа 403 Forbidden, пользователь не создаётся')
    def test_create_user_without_email_should_fail(self, create_new_user):
        with allure.step("Отправить POST-запрос на создание пользователя без email"):
            payload = User.create_user_without_email()
            response = create_new_user(payload)

        with allure.step("Проверить ошибку отсутствия обязательного поля"):
            assert response.status_code == ResponseCode.FORBIDDEN
            assert response.json().get("success") == False
            assert response.json().get("message") == ResponseMessages.MISSING_FIELDS

    @allure.title(
        'При отправке запроса на создание пользователя без указания пароля - код ответа 403 Forbidden, пользователь не создаётся')
    @allure.description('В рамках данного тест-кейса проверяется, '
                        'что при отправке запроса на создание пользователя без указания пароля - код ответа 403 Forbidden, пользователь не создаётся')
    def test_create_user_without_password_should_fail(self, create_new_user):
        with allure.step("Отправить POST-запрос на создание пользователя без пароля"):
            payload = User.create_user_without_password()
            response = create_new_user(payload)

        with allure.step("Проверить ошибку отсутствия обязательного поля"):
            assert response.status_code == ResponseCode.FORBIDDEN
            assert response.json().get("success") == False
            assert response.json().get("message") == ResponseMessages.MISSING_FIELDS