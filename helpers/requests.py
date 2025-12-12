# helpers/requests.py
import requests
import logging
from data.api_information import Endpoints

# Настраиваем логирование
logger = logging.getLogger(__name__)


def creating_new_user(payload):
    """Создание нового пользователя с обработкой ошибок"""
    try:
        logger.debug(f"Создание пользователя с email: {payload.get('email')}")
        response = requests.post(Endpoints.CREATING_USER, json=payload)
        
        # Логируем результат
        if response.status_code >= 400:
            logger.warning(
                f"Ошибка при создании пользователя {payload.get('email')}: "
                f"статус={response.status_code}, ответ={response.text}"
            )
        else:
            logger.debug(f"Пользователь {payload.get('email')} успешно создан")
        
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Сетевая ошибка при создании пользователя: {e}")
        # Создаем mock response с ошибкой для корректной работы тестов
        from unittest.mock import Mock
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = f"Network error: {str(e)}"
        return mock_response


def login_user(payload):
    """Авторизация пользователя с обработкой ошибок"""
    try:
        logger.debug(f"Авторизация пользователя: {payload.get('email')}")
        response = requests.post(Endpoints.LOGIN_USER, json=payload)
        
        if response.status_code >= 400:
            logger.warning(
                f"Ошибка авторизации для {payload.get('email')}: "
                f"статус={response.status_code}, ответ={response.text}"
            )
        
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Сетевая ошибка при авторизации: {e}")
        from unittest.mock import Mock
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = f"Network error: {str(e)}"
        return mock_response


def create_order(payload, access_token=None):
    """Создание заказа с обработкой ошибок"""
    try:
        headers = {}
        if access_token:
            # Токен УЖЕ содержит "Bearer ", поэтому используем как есть
            headers["Authorization"] = access_token
            logger.debug(f"Создание заказа с токеном: {access_token[:20]}...")
        else:
            logger.debug("Создание заказа без авторизации")
        
        response = requests.post(Endpoints.CREATE_ORDER, json=payload, headers=headers)
        
        if response.status_code >= 400:
            logger.warning(
                f"Ошибка при создании заказа: "
                f"статус={response.status_code}, ответ={response.text[:100]}"
            )
        
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Сетевая ошибка при создании заказа: {e}")
        from unittest.mock import Mock
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = f"Network error: {str(e)}"
        return mock_response


def get_ingredients():
    """Получение списка ингредиентов с обработкой ошибок"""
    try:
        logger.debug("Получение списка ингредиентов")
        response = requests.get(Endpoints.GET_INGREDIENTS)
        
        if response.status_code >= 400:
            logger.warning(
                f"Ошибка при получении ингредиентов: "
                f"статус={response.status_code}, ответ={response.text}"
            )
        
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Сетевая ошибка при получении ингредиентов: {e}")
        from unittest.mock import Mock
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = f"Network error: {str(e)}"
        return mock_response


def delete_user(access_token):
    """Удаление пользователя с обработкой ошибок"""
    try:
        if not access_token:
            logger.error("Попытка удаления пользователя без токена")
            from unittest.mock import Mock
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.text = "No access token provided"
            return mock_response
        
        headers = {"Authorization": access_token}
        logger.debug(f"Удаление пользователя с токеном: {access_token[:20]}...")
        
        response = requests.delete(Endpoints.DELETE_USER, headers=headers)
        
        if response.status_code >= 400:
            logger.warning(
                f"Ошибка при удалении пользователя: "
                f"статус={response.status_code}, ответ={response.text}"
            )
        else:
            logger.debug("Пользователь успешно удален")
        
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Сетевая ошибка при удалении пользователя: {e}")
        from unittest.mock import Mock
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = f"Network error: {str(e)}"
        return mock_response


# Дополнительные функции для удобства
def get_user_profile(access_token):
    """Получение профиля пользователя"""
    try:
        headers = {"Authorization": access_token}
        logger.debug(f"Получение профиля пользователя")
        response = requests.get(Endpoints.GET_USER_PROFILE, headers=headers)
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Сетевая ошибка при получении профиля: {e}")
        from unittest.mock import Mock
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = f"Network error: {str(e)}"
        return mock_response


def update_user_profile(payload, access_token):
    """Обновление профиля пользователя"""
    try:
        headers = {"Authorization": access_token}
        logger.debug(f"Обновление профиля пользователя")
        response = requests.patch(Endpoints.UPDATE_USER_PROFILE, json=payload, headers=headers)
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Сетевая ошибка при обновлении профиля: {e}")
        from unittest.mock import Mock
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = f"Network error: {str(e)}"
        return mock_response