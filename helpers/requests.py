import requests
from data.api_information import Endpoints


def creating_new_user(payload):
    response = requests.post(Endpoints.CREATING_USER,json=payload)
    return response

def login_user(payload):
    response = requests.post(Endpoints.LOGIN_USER, json=payload)
    return response

def create_order(payload, access_token=None):
    """Создание заказа"""
    headers = {}
    if access_token:
        # Токен УЖЕ содержит "Bearer ", поэтому используем как есть
        headers["Authorization"] = access_token
    response = requests.post(Endpoints.CREATE_ORDER, json=payload, headers=headers)
    return response


def get_ingredients():
    response = requests.get(Endpoints.GET_INGREDIENTS)
    return response

def delete_user(access_token):
    """Удаление пользователя"""
    headers = {"Authorization": access_token}
    response = requests.delete(Endpoints.DELETE_USER, headers=headers)
    return response