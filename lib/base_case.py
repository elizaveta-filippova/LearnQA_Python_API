import json.decoder
import allure

from datetime import datetime
from requests import Response
from lib.assertions import Assertions
from lib.my_requests import MyRequests


class BaseCase:

    @allure.step("Getting cookie")
    def get_cookie(self, response: Response, cookie_name):
        assert cookie_name in response.cookies, f"Cannot find cookie with name {cookie_name} " \
                                                f"in the last response"
        with allure.step("Getting cookie"):
            return response.cookies[cookie_name]

    @allure.step("Getting header")
    def get_header(self, response: Response, header_name):
        assert header_name in response.headers, f"Cannot find header with name {header_name} " \
                                                f"in the last response"
        with allure.step("Getting header"):
            return response.headers[header_name]

    @allure.step("Getting JSON value")
    def get_json_value(self, response: Response, name):
        try:
            response_as_dict = response.json()
        except json.decoder.JSONDecodeError:
            assert False, f"Response is not in JSON format, response text is {response.text}"

        assert name in response_as_dict, f"Response JSON doesn't have key '{name}'"
        with allure.step("Getting JSON value"):
            return response_as_dict[name]

    @allure.step("Preparing registration data")
    def prepare_registration_data(self, email=None, username=None):
        if email is None:
            base_part = "learnqa"
            domain = "example.com"
            random_part = datetime.now().strftime("%m%d%Y%H%M%S")
            email = f"{base_part}{random_part}@{domain}"
        if username is None:
            username = "learnqa"
        keys = ['password', 'username', 'firstName', 'lastName', 'email']
        values = ['123', username, 'learnqa', 'learnqa', email]

        return {key: value for key, value in zip(keys, values)}

    @allure.step("Creating new user and returning data")
    def create_new_user_return_data(self, register_uri, return_login_data: bool = None,
                                    return_user_id: bool = None):
        """Returns login data, user_id, or full user data including user_id if no parameter specified."""
        register_data = self.prepare_registration_data()
        response = MyRequests.post(register_uri, data=register_data)

        Assertions.assert_code_status(response, 200)
        Assertions.assert_json_has_key(response, "id")

        if return_login_data:
            with allure.step('Getting email and password'):
                return {
                    'email': register_data['email'],
                    'password': register_data['password']
                }

        if return_user_id:
            with allure.step('Getting user id'):
                return self.get_json_value(response, "id")

        else:
            with allure.step("Getting full user data"):
                return {
                    'email': register_data['email'],
                    'password': register_data['password'],
                    'username': register_data['username'],
                    'firstName': register_data['firstName'],
                    'lastName': register_data['lastName'],
                    'user_id': self.get_json_value(response, "id")
                }
