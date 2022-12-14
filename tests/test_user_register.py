import pytest
import random

from lib.my_requests import MyRequests
from lib.base_case import BaseCase
from lib.assertions import Assertions
from lib.helpers import get_dict_wo_key, random_string


class TestUserRegister(BaseCase):
    uri = "/user/"
    email = "vinkotov@example.com"
    exclude_data = [
        ("password"),
        ("username"),
        ("firstName"),
        ("lastName"),
        ("email")
    ]

    def test_create_user_successfully(self):
        data = self.prepare_registration_data()

        response = MyRequests.post(url=self.uri, data=data)

        Assertions.assert_code_status(response, 200)
        Assertions.assert_json_has_key(response, "id")

    def test_create_user_with_existing_email(self):
        data = self.prepare_registration_data(self.email)
        response = MyRequests.post(url=self.uri, data=data)

        Assertions.assert_code_status(response, 400)
        Assertions.assert_response_content(response, f"Users with email '{self.email}' already exists")

    def test_create_user_with_email_without_at_symbol(self):
        email = self.email.replace("@", "")
        data = self.prepare_registration_data(email)
        response = MyRequests.post(url=self.uri, data=data)

        Assertions.assert_code_status(response, 400)
        Assertions.assert_response_content(response, "Invalid email format")

    @pytest.mark.parametrize('excluded_data', exclude_data)
    def test_create_user_with_missing_data(self, excluded_data):
        key_to_exclude = ''.join(list(map(' '.join, excluded_data)))  # достаем ключ в формате sting из tuple
        data = get_dict_wo_key(self.prepare_registration_data(),
                               key_to_exclude)  # исключаем из сгенерированного словаря нужный ключ
        response = MyRequests.post(self.uri, data=data)

        Assertions.assert_code_status(response, 400)
        Assertions.assert_response_content(response, f"The following required params are missed: {key_to_exclude}")

    def test_create_user_with_one_symbol_username(self):
        username = random_string(random.randint(1, 1))
        data = self.prepare_registration_data(username=username)
        response = MyRequests.post(self.uri, data=data)

        Assertions.assert_code_status(response, 400)
        Assertions.assert_response_content(response, f"The value of 'username' field is too short")

    def test_create_user_with_too_long_username(self):
        username = random_string(random.randint(251, 1000))
        data = self.prepare_registration_data(username=username)
        response = MyRequests.post(self.uri, data=data)

        Assertions.assert_code_status(response, 400)
        Assertions.assert_response_content(response, f"The value of 'username' field is too long")
