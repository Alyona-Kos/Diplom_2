import allure
import pytest
import requests
from data.api_information import Endpoints, ResponseCode, ResponseMessages
from helpers.helpers import Ingredients


class TestCreateOrder:

    @allure.title('При отправке запроса на создание заказа авторизованным пользователем - код ответа 200 ОК, заказ создаётся')
    @allure.description('В рамках данного тест-кейса проверяется, '
                        'что при отправке запроса на создание заказа авторизованным пользователем - заказ успешно создаётся')
    def test_create_order_with_auth_is_created_success(self, user_with_cleanup):
        payload, user_response = user_with_cleanup
        token = user_response.json()["accessToken"]  # Токен уже содержит "Bearer "
        
        with allure.step("Отправить GET-запрос для получения списка ингредиентов"):
            ingredients_response = requests.get(Endpoints.GET_INGREDIENTS)
        
        assert ingredients_response.status_code == ResponseCode.OK
        real_ingredients = ingredients_response.json()["data"]
        
        # КРИТИЧЕСКАЯ ПРОВЕРКА
        assert len(real_ingredients) >= 2, "Недостаточно ингредиентов в базе для выполнения теста"
        
        real_ingredient_ids = [real_ingredients[0]["_id"], real_ingredients[1]["_id"]]
        order_payload = {"ingredients": real_ingredient_ids}
        
        with allure.step("Отправить POST-запрос на создание заказа"):
            # Токен УЖЕ содержит "Bearer ", поэтому используем как есть
            response = requests.post(
                Endpoints.CREATE_ORDER,
                json=order_payload,
                headers={"Authorization": token}  # Просто token, без добавления "Bearer "
            )
        
        assert response.status_code == ResponseCode.OK
        assert response.json().get("success") == True

    @allure.title(
        'При отправке запроса на создание заказа НЕавторизованным пользователем - код ответа 200 ОК, заказ создаётся')
    @allure.description('В рамках данного тест-кейса проверяется, '
                        'что при отправке запроса на создание заказа НЕавторизованным пользователем - заказ успешно создаётся')
    def test_create_order_without_auth_is_created(self):
        with allure.step("Отправить GET-запрос для получения списка ингредиентов"):
            ingredients_response = requests.get(Endpoints.GET_INGREDIENTS)
        
        assert ingredients_response.status_code == ResponseCode.OK
        real_ingredients = ingredients_response.json()["data"]
        
        # КРИТИЧЕСКАЯ ПРОВЕРКА
        assert len(real_ingredients) >= 2, "Недостаточно ингредиентов в базе для выполнения теста"
        
        real_ingredient_ids = [real_ingredients[0]["_id"], real_ingredients[1]["_id"]]
        order_payload = {"ingredients": real_ingredient_ids}

        with allure.step("Отправить POST-запрос на создание заказа"):
            response = requests.post(Endpoints.CREATE_ORDER, json=order_payload)

        assert response.status_code == ResponseCode.OK
        assert response.json().get("success") == True

    @allure.title(
        'При отправке запроса на создание заказа с ингредиентами - код ответа 200 ОК, заказ создаётся')
    @allure.description('В рамках данного тест-кейса проверяется, '
                        'что при отправке запроса на создание заказа с ингредиентами - заказ успешно создаётся')
    def test_create_order_with_ingredients_is_created(self):
        with allure.step("Отправить GET-запрос для получения списка ингредиентов"):
            ingredients_response = requests.get(Endpoints.GET_INGREDIENTS)
        
        assert ingredients_response.status_code == ResponseCode.OK
        real_ingredients = ingredients_response.json()["data"]
        
        # КРИТИЧЕСКАЯ ПРОВЕРКА
        assert len(real_ingredients) >= 2, "Недостаточно ингредиентов в базе для выполнения теста"
        
        real_ingredient_ids = [real_ingredients[0]["_id"], real_ingredients[1]["_id"]]
        order_payload = {"ingredients": real_ingredient_ids}
        
        with allure.step("Отправить POST-запрос на создание заказа"):
            response = requests.post(Endpoints.CREATE_ORDER, json=order_payload)
        
        assert response.status_code == ResponseCode.OK
        assert response.json().get("success") == True

    @allure.title(
        'При отправке запроса на создание заказа без ингредиентов - код ответа 400 Bad Request, заказ не создаётся')
    @allure.description('В рамках данного тест-кейса проверяется, '
                        'что при отправке запроса на создание заказа без ингредиентов - заказ не создаётся')
    def test_create_order_without_ingredients_should_fail(self):
        with allure.step("Отправить POST-запрос на создание заказа"):
            response = requests.post(Endpoints.CREATE_ORDER, 
                                     json=Ingredients.incorrect_ingredients_data_without_filling)
        
        assert response.status_code == ResponseCode.BAD_REQUEST
        assert response.json().get("message") == ResponseMessages.ORDER_MISSING_INGREDIENTS

    @allure.title(
        'При отправке запроса на создание заказа с невалидным хэшем - код ответа 500, заказ не создаётся')
    @allure.description('В рамках данного тест-кейса проверяется, '
                        'что при отправке запроса на создание заказа без ингредиентов - заказ не создаётся')
    def test_create_order_with_invalid_ingredients_should_fail(self):
        with allure.step("Отправить POST-запрос на создание заказа"):
            response = requests.post(Endpoints.CREATE_ORDER,
                                     json=Ingredients.incorrect_ingredients_data_hash)
        
        assert response.status_code == ResponseCode.INTERNAL_SERVER_ERROR
        assert "Internal Server Error" in response.text