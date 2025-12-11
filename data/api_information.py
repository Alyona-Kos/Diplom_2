# api_information.py

class Endpoints:
    BASE_URL = "https://stellarburgers.education-services.ru"
    
    # Аутентификация и пользователи
    CREATING_USER = f"{BASE_URL}/api/auth/register"
    LOGIN_USER = f"{BASE_URL}/api/auth/login"
    LOGOUT_USER = f"{BASE_URL}/api/auth/logout"
    TOKEN_USER = f"{BASE_URL}/api/auth/token"
    DELETE_USER = f"{BASE_URL}/api/auth/user"
    
    # Заказы и ингредиенты
    GET_INGREDIENTS = f"{BASE_URL}/api/ingredients"
    CREATE_ORDER = f"{BASE_URL}/api/orders"


class ResponseCode:
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500


class ResponseMessages:
    # Создание пользователя
    USER_CREATED_SUCCESS = "User created successfully"
    USER_ALREADY_EXISTS = "User already exists"
    MISSING_FIELDS = "Email, password and name are required fields"  # Для создания пользователя
    
    # Авторизация
    INVALID_CREDENTIALS = "email or password are incorrect"  # Для логина (включая отсутствие полей)
    
    # Заказы
    ORDER_MISSING_INGREDIENTS = "Ingredient ids must be provided"
    ORDER_INVALID_HASH = "Internal Server Error"
    ORDER_UNAUTHORIZED = "You should be authorised"
    
    # Профиль пользователя
    USER_UNAUTHORIZED = "You should be authorised"
    EMAIL_ALREADY_EXISTS = "User with such email already exists"