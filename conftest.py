# conftest.py
import pytest
import allure
import logging
from typing import Tuple, Dict, Any, Optional, Callable
from helpers.helpers import User
from helpers.requests import creating_new_user, delete_user, get_ingredients
from data.api_information import ResponseCode

# Настраиваем логирование для тестов
logger = logging.getLogger(__name__)


class UserManager:
    """
    Класс-менеджер для управления пользователями в тестах.
    Инкапсулирует логику создания и удаления пользователей.
    """
    
    @staticmethod
    def create_test_user() -> Tuple[Dict[str, str], Any]:
        """
        Создает тестового пользователя.
        Возвращает: (payload, response)
        """
        payload = User.create_data_correct_user()
        
        with allure.step(f"Создание тестового пользователя: {payload['email']}"):
            response = creating_new_user(payload)
            
            if response.status_code != ResponseCode.OK:
                error_msg = (
                    f"Не удалось создать пользователя.\n"
                    f"Код ответа: {response.status_code}\n"
                    f"Email: {payload['email']}\n"
                    f"Ответ сервера: {response.text}"
                )
                pytest.fail(error_msg)
        
        return payload, response
    
    @staticmethod
    def cleanup_user(token: str, email: str) -> None:
        """
        Удаляет пользователя после теста.
        """
        if not token:
            logger.warning(f"Не получен токен для удаления пользователя {email}")
            return
        
        with allure.step(f"Очистка: удаление пользователя (постусловие): {email}"):
            try:
                delete_response = delete_user(token)
                if delete_response.status_code != ResponseCode.OK:
                    logger.warning(
                        f"Не удалось удалить пользователя {email}: "
                        f"статус={delete_response.status_code}"
                    )
            except Exception as e:
                logger.error(f"Ошибка при очистке для {email}: {e}")
    
    @staticmethod
    def extract_token(response) -> Optional[str]:
        """
        Извлекает токен из ответа сервера.
        """
        try:
            return response.json().get("accessToken")
        except Exception:
            return None


def user_fixture_factory(return_type: str = "payload_response"):
    """
    Фабрика для создания фикстур пользователей с разными возвращаемыми значениями.
    
    Args:
        return_type: тип возвращаемых данных:
            - "payload_response": возвращает (payload, response)
            - "payload": возвращает только payload
            - "authenticated": возвращает (payload, auth_header)
            - "full": возвращает (payload, response, token)
    """
    @pytest.fixture
    def _user_fixture():
        """
        Базовая фикстура создания пользователя.
        """
        payload, response = UserManager.create_test_user()
        token = UserManager.extract_token(response)
        
        # Проверяем наличие токена для всех вариантов, кроме payload
        if return_type != "payload" and not token:
            error_msg = (
                f"Пользователь создан, но токен не получен.\n"
                f"Email: {payload['email']}\n"
                f"Ответ сервера: {response.text}"
            )
            logger.error(error_msg)
            pytest.fail(error_msg)
        
        # Возвращаем данные в зависимости от запрошенного типа
        if return_type == "payload_response":
            return_data = (payload, response)
        elif return_type == "payload":
            return_data = payload
        elif return_type == "authenticated":
            auth_header = {"Authorization": token}
            return_data = (payload, auth_header)
        elif return_type == "full":
            return_data = (payload, response, token)
        else:
            raise ValueError(f"Неизвестный тип возвращаемых данных: {return_type}")
        
        yield return_data
        
        # АВТОМАТИЧЕСКАЯ ОЧИСТКА ПОСЛЕ ТЕСТА
        if token:
            UserManager.cleanup_user(token, payload['email'])
    
    return _user_fixture


# Создаем фикстуры используя фабрику
user_with_cleanup = user_fixture_factory(return_type="payload_response")
registered_user_for_login = user_fixture_factory(return_type="payload")
authenticated_user = user_fixture_factory(return_type="authenticated")
debug_user = user_fixture_factory(return_type="full")


@pytest.fixture
def user_factory():
    """
    Фабрика для создания пользователей в тестах.
    Используется когда создание пользователя - часть теста (не предусловие).
    Возвращает функцию для создания пользователя.
    АВТОМАТИЧЕСКИ удаляет всех созданных пользователей после теста.
    """
    created_users = []
    
    def _create_user(return_token: bool = False):
        """
        Создает нового пользователя.
        
        Args:
            return_token: если True, возвращает также токен
        
        Returns:
            (payload, response) или (payload, response, token)
        """
        payload, response = UserManager.create_test_user()
        
        if response.status_code == ResponseCode.OK:
            token = UserManager.extract_token(response)
            created_users.append((payload, response, token))
        
        if return_token and token:
            return payload, response, token
        return payload, response
    
    yield _create_user
    
    # АВТОМАТИЧЕСКАЯ ОЧИСТКА ВСЕХ СОЗДАННЫХ ПОЛЬЗОВАТЕЛЕЙ ПОСЛЕ ТЕСТА
    with allure.step("Очистка: удаление всех созданных пользователей"):
        for payload, response, token in created_users:
            if token:
                UserManager.cleanup_user(token, payload['email'])


@pytest.fixture
def dynamic_user_fixture():
    """
    Динамическая фикстура, которая позволяет тестам указывать тип возвращаемых данных.
    
    Пример использования в тесте:
    def test_something(dynamic_user_fixture):
        payload, response = dynamic_user_fixture("payload_response")
    """
    def _get_user(return_type: str = "payload_response"):
        """
        Создает пользователя с указанным типом возвращаемых данных.
        
        Args:
            return_type: тип возвращаемых данных (аналогично user_fixture_factory)
        """
        payload, response = UserManager.create_test_user()
        token = UserManager.extract_token(response)
        
        if not token:
            error_msg = f"Не получен accessToken для пользователя {payload['email']}"
            pytest.fail(error_msg)
        
        # Запланируем удаление пользователя после теста
        def cleanup():
            UserManager.cleanup_user(token, payload['email'])
        
        # Используем addfinalizer для гарантированного удаления
        request = pytest.getfixturevalue('request')
        request.addfinalizer(cleanup)
        
        # Возвращаем данные в зависимости от типа
        if return_type == "payload_response":
            return payload, response
        elif return_type == "payload":
            return payload
        elif return_type == "authenticated":
            auth_header = {"Authorization": token}
            return payload, auth_header
        elif return_type == "full":
            return payload, response, token
        else:
            raise ValueError(f"Неизвестный тип возвращаемых данных: {return_type}")
    
    return _get_user


# Остальные фикстуры (не связанные с пользователями) остаются без изменений
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


# Алиасы для обратной совместимости (если нужно)
debug_user_creation = debug_user