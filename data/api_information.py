class Endpoints:
    BASE_URL = "https://stellarburgers.education-services.ru"
    
    # Аутентификация и пользователи
    CREATING_USER = f"{BASE_URL}/api/auth/register"       # Создание пользователя
    LOGIN_USER = f"{BASE_URL}/api/auth/login"             # Авторизация
    LOGOUT_USER = f"{BASE_URL}/api/auth/logout"           # Выход из системы
    TOKEN_USER = f"{BASE_URL}/api/auth/token"             # Обновление токена
    DELETE_USER = f"{BASE_URL}/api/auth/user"             # Удаление пользователя 
    
    # Заказы и ингредиенты
    GET_INGREDIENTS = f"{BASE_URL}/api/ingredients"       # Получение ингредиентов
    CREATE_ORDER = f"{BASE_URL}/api/orders"               # Создание заказа
    
    # Дополнительные эндпоинты (если понадобятся)
    # USER_PROFILE = f"{BASE_URL}/api/auth/user"          # Профиль пользователя (GET/PATCH)
    # PASSWORD_RESET = f"{BASE_URL}/api/password-reset"   # Сброс пароля
    # GET_USER_ORDERS = f"{BASE_URL}/api/orders"          # Заказы пользователя (GET)
    # GET_ALL_ORDERS = f"{BASE_URL}/api/orders/all"       # Все заказы (GET)


class ResponseCode:
    OK = 200                      # Успешно
    CREATED = 201                 # Создано
    BAD_REQUEST = 400             # Неверный запрос
    UNAUTHORIZED = 401            # Не авторизован
    FORBIDDEN = 403               # Запрещено
    NOT_FOUND = 404               # Не найдено
    INTERNAL_SERVER_ERROR = 500   # Внутренняя ошибка сервера


class ResponseMessages:
    # Создание пользователя
    USER_CREATED_SUCCESS = "User created successfully"
    USER_ALREADY_EXISTS = "User already exists"
    MISSING_FIELDS = "Email, password and name are required fields"
    
    # Авторизация
    INVALID_CREDENTIALS = "email or password are incorrect"
    
    # Заказы
    ORDER_MISSING_INGREDIENTS = "Ingredient ids must be provided"
    ORDER_INVALID_HASH = "Internal Server Error"
    ORDER_UNAUTHORIZED = "You should be authorised"
    
    # Профиль пользователя (для будущих тестов)
    USER_UNAUTHORIZED = "You should be authorised"
    EMAIL_ALREADY_EXISTS = "User with such email already exists"