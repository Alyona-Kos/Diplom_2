# tests/test_creating_order.py
import allure
import pytest
from data.api_information import ResponseCode, ResponseMessages
from helpers.helpers import Ingredients
from helpers.requests import create_order


class TestCreateOrder:

    @allure.title('Создание заказа авторизованным пользователем - успешно')
    @allure.description('Проверка успешного создания заказа авторизованным пользователем')
    def test_create_order_with_auth_is_created_success(
        self, 
        authenticated_user, 
        order_payload
    ):
        _, auth_header = authenticated_user
        
        with allure.step("Создание заказа с авторизацией"):
            response = create_order(order_payload, auth_header["Authorization"])
        
        assert response.status_code == ResponseCode.OK, (
            f"Ожидался код {ResponseCode.OK}, получен {response.status_code}"
        )
        assert response.json().get("success") is True, "Флаг success должен быть True"
        
        order_data = response.json().get("order")
        assert order_data is not None, "В ответе должен быть объект order"
        assert "number" in order_data, "В заказе должен быть номер"
        assert "name" in order_data, "В заказе должно быть название"

    @allure.title('Создание заказа неавторизованным пользователем - успешно')
    @allure.description('Проверка успешного создания заказа неавторизованным пользователем')
    def test_create_order_without_auth_is_created(self, order_payload):
        with allure.step("Создание заказа без авторизации"):
            response = create_order(order_payload)
        
        assert response.status_code == ResponseCode.OK, (
            f"Ожидался код {ResponseCode.OK}, получен {response.status_code}"
        )
        assert response.json().get("success") is True, "Флаг success должен быть True"

    @allure.title('Создание заказа без ингредиентов - ошибка 400')
    @allure.description('Проверка ошибки при создании заказа без ингредиентов')
    def test_create_order_without_ingredients_should_fail(self):
        payload = Ingredients.incorrect_ingredients_data_without_filling
        
        with allure.step("Попытка создания заказа без ингредиентов"):
            response = create_order(payload)
        
        assert response.status_code == ResponseCode.BAD_REQUEST, (
            f"Ожидался код {ResponseCode.BAD_REQUEST}, получен {response.status_code}"
        )
        assert response.json().get("message") == ResponseMessages.ORDER_MISSING_INGREDIENTS

    @allure.title('Создание заказа с невалидными хэшами ингредиентов - ошибка 500')
    @allure.description('Проверка ошибки при создании заказа с невалидными хэшами')
    def test_create_order_with_invalid_ingredients_should_fail(self):
        payload = Ingredients.incorrect_ingredients_data_hash
        
        with allure.step("Попытка создания заказа с невалидными хэшами"):
            response = create_order(payload)
        
        assert response.status_code == ResponseCode.INTERNAL_SERVER_ERROR, (
            f"Ожидался код {ResponseCode.INTERNAL_SERVER_ERROR}, "
            f"получен {response.status_code}"
        )
        assert "Internal Server Error" in response.text