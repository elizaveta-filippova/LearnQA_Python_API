import allure
import pytest
import random

from lib.my_requests import MyRequests
from lib.base_case import BaseCase
from lib.assertions import Assertions
from lib.helpers import get_dict_wo_key, random_string


@allure.parent_suite('LearnQA user API')
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

    @allure.parent_suite('LearnQA user API')
    @allure.suite('Registering user')
    @allure.description("This test successfully creates user with registration data")
    def test_create_user_successfully(self):
        data = self.prepare_registration_data()
        with allure.step(f"Trying to register user with data {data}"):
            response = MyRequests.post(url=self.uri, data=data)
        with allure.step(f"Asserting that creating user with data {data} was successful"):
            Assertions.assert_code_status(response, 200)
            Assertions.assert_json_has_key(response, "id")

    @allure.parent_suite('LearnQA user API')
    @allure.suite('Registering user')
    @allure.description("This test unsuccessfully creates user with an existing email")
    def test_create_user_with_existing_email(self):
        with allure.step(f"Preparing registration data with an existing email {self.email}"):
            data = self.prepare_registration_data(self.email)
        with allure.step(f"Trying to register user with an existing email {self.email}"):
            response = MyRequests.post(url=self.uri, data=data)
        with allure.step(f"Asserting that creating user with {data} was unusuccessful"):
            Assertions.assert_code_status(response, 400)
            Assertions.assert_response_content(response, f"Users with email '{self.email}' already exists")

    @allure.parent_suite('LearnQA user API')
    @allure.suite('Registering user')
    @allure.description("This test unsuccessfully tries to create user without '@' symbol")
    def test_create_user_with_email_without_at_symbol(self):
        with allure.step("Removing '@' symbol from email"):
            email = self.email.replace("@", "")
        with allure.step("Preparing registration data with previously created email"):
            data = self.prepare_registration_data(email)
        with allure.step(f"Trying to register user with data {data} previously created email {email}"):
            response = MyRequests.post(url=self.uri, data=data)
        with allure.step(f"Asserting that creating user with {data} was unusuccessful"):
            Assertions.assert_code_status(response, 400)
            Assertions.assert_response_content(response, "Invalid email format")

    @allure.parent_suite('LearnQA user API')
    @allure.suite('Registering user')
    @allure.description("This test unsuccessfully tries to create user with missing data")
    @pytest.mark.parametrize('excluded_data', exclude_data)
    def test_create_user_with_missing_data(self, excluded_data):
        with allure.step("Generating key to exclude"):
            key_to_exclude = ''.join(list(map(' '.join, excluded_data)))  # достаем ключ в формате sting из tuple
        with allure.step(f"Preparing registration data without the key {key_to_exclude}"):
            data = get_dict_wo_key(self.prepare_registration_data(),
                                   key_to_exclude)  # исключаем из сгенерированного словаря нужный ключ
        with allure.step(f"Trying to register user without {key_to_exclude}"):
            response = MyRequests.post(self.uri, data=data)
        with allure.step(f"Asserting that creating user with {data} was unusuccessful"):
            Assertions.assert_code_status(response, 400)
            Assertions.assert_response_content(response, f"The following required params are missed: {key_to_exclude}")

    @allure.parent_suite('LearnQA user API')
    @allure.suite('Registering user')
    @allure.description("This test unsuccessfully tries to create user with one symbol username")
    def test_create_user_with_one_symbol_username(self):
        with allure.step("Generating username"):
            username = random_string(random.randint(1, 1))
        with allure.step(f"Preparing registration data with one symbol '{username}'"):
            data = self.prepare_registration_data(username=username)
        with allure.step(f"Trying to register user with username '{username}'"):
            response = MyRequests.post(self.uri, data=data)
        with allure.step("Asserting that creating user was unusuccessful"):
            Assertions.assert_code_status(response, 400)
            Assertions.assert_response_content(response, f"The value of 'username' field is too short")

    @allure.parent_suite('LearnQA user API')
    @allure.suite('Registering user')
    @allure.description("This test unsuccessfully tries to create user with username that's too long")
    def test_create_user_with_too_long_username(self):
        with allure.step("Generating username"):
            username = random_string(random.randint(251, 1000))
        with allure.step(f"Preparing registration data with too long username {username}"):
            data = self.prepare_registration_data(username=username)
        with allure.step("Trying to register user"):
            response = MyRequests.post(self.uri, data=data)
        with allure.step("Asserting that creating user was unusuccessful"):
            Assertions.assert_code_status(response, 400)
            Assertions.assert_response_content(response, f"The value of 'username' field is too long")
