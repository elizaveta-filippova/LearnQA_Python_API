import requests
from lib.base_case import BaseCase
from lib.assertions import Assertions


class TestUserGet(BaseCase):
    user_data = {
        'email': 'vinkotov@example.com',
        'password': '1234'
    }

    def test_get_user_details_not_auth(self):
        response = requests.get("https://playground.learnqa.ru/api/user/2")

        Assertions.assert_json_has_key(response, "username")
        Assertions.assert_json_has_not_key(response, "email")
        Assertions.assert_json_has_not_key(response, "firstName")
        Assertions.assert_json_has_not_key(response, "lastName")

    def test_get_user_details_auth_as_same_user(self):
        response1 = requests.post("https://playground.learnqa.ru/api/user/login", data=self.user_data)
        auth_sid = self.get_cookie(response1, "auth_sid")
        token = self.get_header(response1, "x-csrf-token")
        user_id_from_auth_method = self.get_json_value(response1, "user_id")

        response2 = requests.get(f"https://playground.learnqa.ru/api/user/{user_id_from_auth_method}",
                                 headers={'x-csrf-token': token}, cookies={'auth_sid': auth_sid})
        expected_fields = ["username", "email", "firstName", "lastName"]

        Assertions.assert_json_has_keys(response2, expected_fields)

    def test_get_user_details_auth_as_another_user(self):
        new_user_data = self.prepare_registration_data()
        response1 = requests.post("https://playground.learnqa.ru/api/user/", data=new_user_data) # создаем нового пользователя
        new_user_id = self.get_json_value(response1, "id")

        response2 = requests.post("https://playground.learnqa.ru/api/user/login", data=self.user_data) # логинимся под нашим пользователем
        auth_sid = self.get_cookie(response2, "auth_sid")
        token = self.get_header(response2, "x-csrf-token")

        response3 = requests.get(f"https://playground.learnqa.ru/api/user/{new_user_id}",
                                 headers={'x-csrf-token': token}, cookies={'auth_sid': auth_sid}) # пытаемся получить данные нового пользователя
        expected_field = "username"
        unexpected_fields = ["email", "firstName", "lastName"]

        Assertions.assert_json_has_not_keys(response3, unexpected_fields)
        Assertions.assert_json_has_key(response3, expected_field)





