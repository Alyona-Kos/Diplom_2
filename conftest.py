# conftest.py
import pytest
import allure
import logging
from helpers.helpers import User
from helpers.requests import creating_new_user, delete_user, get_ingredients
from data.api_information import ResponseCode

# Настраиваем логирование для тестов
logger = logging.getLogger(__name__)


@pytest.fixture
def user_with_cleanup():
    """
    Фикстура создает пользователя как предусловие для тестов.
    Используется в тестах, где нужно иметь уже созданного пользователя.
    Возвращает: (payload, response)
    АВТОМАТИЧЕСКИ удаляет пользователя после теста.
    """
    payload = User.create_data_correct_user()
    
    with allure.step(f"Создание тестового пользователя (предусловие): {payload['email']}"):
        response = creating_new_user(payload)
        
        if response.status_code != ResponseCode.OK:
            # Подробная информация об ошибке
            error_msg = (
                f"Не удалось создать пользователя как предусловие.\n"
                f"Код ответа: {response.status_code}\n"
                f"Email: {payload['email']}\n"
                f"Ответ сервера: {response.text}"
            )
            pytest.fail(error_msg)
    
    yield payload, response
    
    # АВТОМАТИЧЕСКАЯ ОЧИСТКА ПОСЛЕ ТЕСТА
    with allure.step(f"Очистка: удаление пользователя (постусловие): {payload['email']}"):
        try:
            token = response.json().get("accessToken")
            if token:
                delete_response = delete_user(token)
                if delete_response.status_code != ResponseCode.OK:
                    logger.warning(
                        f"Не удалось удалить пользователя {payload['email']}: "
                        f"статус={delete_response.status_code}"
                    )
        except Exception as e:
            logger.error(f"Ошибка при очистке для {payload['email']}: {e}")


@pytest.fixture
def registered_user_for_login():
    """
    Фикстура создает пользователя как предусловие для тестов логина и создания дубликатов.
    Возвращает payload пользователя.
    АВТОМАТИЧЕСКИ удаляет пользователя после теста.
    """
    payload = User.create_data_correct_user()
    token = None
    
    with allure.step(f"Регистрация пользователя для тестов (предусловие): {payload['email']}"):
        response = creating_new_user(payload)
        
        if response.status_code != ResponseCode.OK:
            # Подробная диагностика ошибки
            error_details = (
                f"Не удалось создать пользователя для тестов.\n"
                f"Код ответа: {response.status_code}\n"
                f"Email: {payload['email']}\n"
                f"Имя: {payload.get('name', 'Не указано')}\n"
                f"Ответ сервера: {response.text}\n"
                f"Заголовки ответа: {dict(response.headers)}"
            )
            logger.error(f"Ошибка создания пользователя: {error_details}")
            pytest.fail(error_details)
        
        # Получаем токен для последующего удаления
        response_data = response.json()
        token = response_data.get("accessToken")
        
        if not token:
            error_msg = (
                f"Пользователь создан, но токен не получен.\n"
                f"Email: {payload['email']}\n"
                f"Ответ сервера: {response.text}"
            )
            logger.error(error_msg)
            pytest.fail(error_msg)
    
    # Передаем данные пользователя тесту
    yield payload
    
    # АВТОМАТИЧЕСКАЯ ОЧИСТКА ПОСЛЕ ТЕСТА
    if token:
        with allure.step(f"Очистка: удаление пользователя (постусловие): {payload['email']}"):
            try:
                delete_response = delete_user(token)
                if delete_response.status_code != ResponseCode.OK:
                    logger.warning(
                        f"Не удалось удалить пользователя {payload['email']}: "
                        f"статус={delete_response.status_code}"
                    )
            except Exception as e:
                logger.error(f"Ошибка при очистке для {payload['email']}: {e}")


@pytest.fixture
def authenticated_user():
    """
    Фикстура создает и авторизует пользователя как предусловие.
    Возвращает: (payload, auth_header)
    АВТОМАТИЧЕСКИ удаляет пользователя после теста.
    """
    payload = User.create_data_correct_user()
    token = None
    
    with allure.step(f"Создание пользователя для авторизации (предусловие): {payload['email']}"):
        response = creating_new_user(payload)
        
        if response.status_code != ResponseCode.OK:
            error_msg = (
                f"Не удалось создать пользователя.\n"
                f"Код ответа: {response.status_code}\n"
                f"Email: {payload['email']}\n"
                f"Ответ сервера: {response.text}"
            )
            pytest.fail(error_msg)
        
        token = response.json().get("accessToken")
        if not token:
            error_msg = f"Не получен accessToken для пользователя {payload['email']}"
            pytest.fail(error_msg)
        
        auth_header = {"Authorization": token}
    
    yield payload, auth_header
    
    # АВТОМАТИЧЕСКАЯ ОЧИСТКА ПОСЛЕ ТЕСТА
    if token:
        with allure.step(f"Очистка: удаление пользователя (постусловие): {payload['email']}"):
            try:
                delete_response = delete_user(token)
                if delete_response.status_code != ResponseCode.OK:
                    logger.warning(
                        f"Не удалось удалить пользователя {payload['email']}: "
                        f"статус={delete_response.status_code}"
                    )
            except Exception as e:
                logger.error(f"Ошибка при очистке для {payload['email']}: {e}")


@pytest.fixture
def user_factory():
    """
    Фабрика для создания пользователей в тестах.
    Используется когда создание пользователя - часть теста (не предусловие).
    Возвращает функцию для создания пользователя.
    АВТОМАТИЧЕСКИ удаляет всех созданных пользователей после теста.
    """
    created_users = []
    
    def _create_user():
        """
        Создает нового пользователя и возвращает (payload, response)
        """
        payload = User.create_data_correct_user()
        
        with allure.step(f"Создание пользователя (часть теста): {payload['email']}"):
            response = creating_new_user(payload)
        
        if response.status_code == ResponseCode.OK:
            created_users.append((payload, response))
        
        return payload, response
    
    yield _create_user
    
    # АВТОМАТИЧЕСКАЯ ОЧИСТКА ВСЕХ СОЗДАННЫХ ПОЛЬЗОВАТЕЛЕЙ ПОСЛЕ ТЕСТА
    with allure.step("Очистка: удаление всех созданных пользователей"):
        for payload, response in created_users:
            try:
                token = response.json().get("accessToken")
                if token:
                    delete_response = delete_user(token)
                    if delete_response.status_code != ResponseCode.OK:
                        logger.warning(
                            f"Не удалось удалить пользователя {payload['email']}: "
                            f"статус={delete_response.status_code}"
                        )
            except Exception as e:
                logger.error(f"Ошибка при очистке для {payload['email']}: {e}")


@pytest.fixture(scope="session")
def available_ingredients():
    """
    Фикстура сессии: получает ингредиенты один раз для всех тестов.
    Это подготовка тестового окружения, а не предусловие конкретного теста.
    """
    with allure.step("Получение списка ингредиентов для тестов"):
        response = get_ingredients()
        
        if response.status_code != ResponseCode.OK:
            error_msg = (
                f"Не удалось получить ингредиенты.\n"
                f"Код ответа: {response.status_code}\n"
                f"Ответ сервера: {response.text}"
            )
            pytest.fail(error_msg)
        
        ingredients_data = response.json()["data"]
        
        if len(ingredients_data) < 2:
            pytest.skip(
                f"Недостаточно ингредиентов в базе для выполнения тестов.\n"
                f"Требуется: 2, доступно: {len(ingredients_data)}"
            )
        
        return ingredients_data


@pytest.fixture
def valid_ingredient_ids(available_ingredients):
    """
    Фикстура возвращает валидные ID ингредиентов для создания заказа.
    Это подготовка тестовых данных, а не предусловие.
    """
    # Берем первые 2 ингредиента из доступных
    return [available_ingredients[0]["_id"], available_ingredients[1]["_id"]]


@pytest.fixture
def order_payload(valid_ingredient_ids):
    """
    Фикстура создает payload для заказа с валидными ингредиентами.
    Это подготовка тестовых данных, а не предусловие.
    """
    return {"ingredients": valid_ingredient_ids}


@pytest.fixture
def invalid_order_payloads():
    """
    Фикстура возвращает набор невалидных payload для негативных тестов.
    Это подготовка тестовых данных, а не предусловие.
    """
    from helpers.helpers import Ingredients
    
    return [
        (Ingredients.incorrect_ingredients_data_without_filling, "Пустой список ингредиентов"),
        (Ingredients.incorrect_ingredients_data_hash, "Невалидные хэши ингредиентов")
    ]


@pytest.fixture
def user_data_generator():
    """
    Генератор тестовых данных пользователя.
    Возвращает функции для создания разных типов данных пользователя.
    """
    class UserDataGenerator:
        @staticmethod
        def valid_user():
            return User.create_data_correct_user()
        
        @staticmethod
        def without_email():
            return User.create_user_without_email()
        
        @staticmethod
        def without_password():
            return User.create_user_without_password()
        
        @staticmethod
        def without_name():
            return User.create_user_without_name()
        
        @staticmethod
        def invalid_login_credentials():
            return User.create_invalid_login_credentials()
    
    return UserDataGenerator()


@pytest.fixture(autouse=True)
def test_isolation():
    """
    Автоматически применяемая фикстура для изоляции тестов.
    Гарантирует, что тесты не зависят друг от друга.
    """
    # Действия перед каждым тестом
    with allure.step("Подготовка тестового окружения"):
        pass
    
    yield
    
    # Действия после каждого теста
    with allure.step("Восстановление состояния после теста"):
        pass


@pytest.fixture(scope="session")
def clean_test_environment():
    """
    Фикстура сессии для подготовки тестового окружения.
    Может использоваться для предварительной очистки БД перед всеми тестами.
    """
    with allure.step("Подготовка тестового окружения (сессия)"):
        # Здесь можно добавить вызов API для очистки тестовых данных
        pass
    
    yield
    
    with allure.step("Финальная очистка тестового окружения (сессия)"):
        # Пост-обработка если нужно
        pass


@pytest.fixture
def debug_user_creation():
    """
    Вспомогательная фикстура для отладки создания пользователя.
    Создает пользователя и выводит детальную информацию.
    """
    payload = User.create_data_correct_user()
    
    print(f"\n{'='*60}")
    print("DEBUG: Создание тестового пользователя")
    print(f"{'='*60}")
    print(f"Email: {payload['email']}")
    print(f"Name: {payload['name']}")
    print(f"Password: {payload['password'][:10]}...")
    print(f"{'-'*60}")
    
    response = creating_new_user(payload)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    print(f"{'='*60}\n")
    
    if response.status_code == ResponseCode.OK:
        token = response.json().get("accessToken")
        yield payload, response, token
    else:
        yield payload, response, None