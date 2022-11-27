import pytest
import requests
import random
from lib.base_case import BaseCase
from lib.assertions import Assertions
from datetime import datetime

from lib.helpers import get_dict_wo_key, random_string


class TestUserRegister(BaseCase):
    url = "https://playground.learnqa.ru/api/user/"

    exclude_data = [
        ("password"),
        ("username"),
        ("firstName"),
        ("lastName"),
        ("email")
    ]

    def setup(self):
        base_part = "learnqa"
        domain = "example.com"
        random_part = datetime.now().strftime("%m%d%Y%H%M%S")
        self.email = f"{base_part}{random_part}@{domain}"
        self.username = "learnqa"

    def generate_data(self, email=None, username=None):
        keys = ['password', 'username', 'firstName', 'lastName', 'email']
        values = ['123', f'{self.username if not username else username}', 'learnqa', 'learnqa',
                  f'{self.email if not email else email}']

        return {key: value for key, value in zip(keys, values)}

    def test_create_user_successfully(self):
        data = self.generate_data()

        response = requests.post(url=self.url, data=data)

        Assertions.assert_code_status(response, 200)
        Assertions.assert_json_has_key(response, "id")

    def test_create_user_with_existing_email(self):
        email = 'vinkotov@example.com'

        data = self.generate_data(email)
        response = requests.post(url=self.url, data=data)

        Assertions.assert_code_status(response, 400)
        Assertions.assert_response_content(response, f"Users with email '{email}' already exists")

    def test_create_user_with_email_without_at_symbol(self):
        email = self.email.replace("@", "")
        data = self.generate_data(email)
        response = requests.post(url=self.url, data=data)

        Assertions.assert_code_status(response, 400)
        Assertions.assert_response_content(response, "Invalid email format")

    @pytest.mark.parametrize('excluded_data', exclude_data)
    def test_create_user_with_missing_data(self, excluded_data):
        key_to_exclude = ''.join(list(map(' '.join, excluded_data)))  # достаем ключ в формате sting из tuple
        data = get_dict_wo_key(self.generate_data(),
                               key_to_exclude)  # исключаем из сгенерированного словаря нужный ключ
        response = requests.post(self.url, data=data)

        Assertions.assert_code_status(response, 400)
        Assertions.assert_response_content(response, f"The following required params are missed: {key_to_exclude}")

    def test_create_user_with_one_symbol_username(self):
        username = random_string(random.randint(1, 1))
        data = self.generate_data(username=username)
        response = requests.post(self.url, data=data)

        Assertions.assert_code_status(response, 400)
        Assertions.assert_response_content(response, f"The value of 'username' field is too short")

    def test_create_user_with_too_long_username(self):
        username = random_string(random.randint(250, 1000))
        data = self.generate_data(username=username)
        response = requests.post(self.url, data=data)

        Assertions.assert_code_status(response, 400)
        Assertions.assert_response_content(response, f"The value of 'username' field is too long")
