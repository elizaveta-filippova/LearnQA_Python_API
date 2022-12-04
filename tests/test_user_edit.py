import random
import time

import pytest
import requests
from lib.base_case import BaseCase
from lib.assertions import Assertions
from lib.helpers import get_dict_wo_key, random_string


def get_url_with_user_id(url, user_id):
    return f"{url}{user_id}"


class TestUserEdit(BaseCase):
    exclude_params = [
        ("no_cookie"),
        ("no_token"),
        ("no cookie and token")
    ]

    register_url = "https://playground.learnqa.ru/api/user/"
    login_url = "https://playground.learnqa.ru/api/user/login"
    get_user_url: str = "https://playground.learnqa.ru/api/user/"
    edit_user_url = "https://playground.learnqa.ru/api/user/"

    def test_edit_just_created_user(self):
        # REGISTER
        register_data = self.prepare_registration_data()
        response1 = requests.post(self.register_url, data=register_data)

        Assertions.assert_code_status(response1, 200)
        Assertions.assert_json_has_key(response1, "id")

        email = register_data['email']
        firstName = register_data['firstName']
        password = register_data['password']
        user_id = self.get_json_value(response1, "id")

        # LOGIN
        login_data = {
            'email': email,
            'password': password
        }
        response2 = requests.post(self.login_url, data=login_data)
        auth_sid = self.get_cookie(response2, "auth_sid")
        token = self.get_header(response2, "x-csrf-token")

        # EDIT
        new_name = "Changed name"

        response3 = requests.put(
            get_url_with_user_id(self.edit_user_url, user_id),
            headers={'x-csrf-token': token},
            cookies={'auth_sid': auth_sid},
            data={'firstName': new_name}
        )

        Assertions.assert_code_status(response3, 200)

        # GET
        response4 = requests.get(
            url=get_url_with_user_id(self.get_user_url, user_id),
            headers={'x-csrf-token': token},
            cookies={'auth_sid': auth_sid}
        )

        Assertions.assert_json_value_by_name(
            response4,
            "firstName",
            new_name,
            "Wrong name of the user after edit"
        )

    @pytest.mark.parametrize('condition', exclude_params)
    def test_edit_data_while_unauthorized(self, condition):
        # REGISTER
        register_data = self.prepare_registration_data()
        response1 = requests.post(self.register_url, data=register_data)

        Assertions.assert_code_status(response1, 200)
        Assertions.assert_json_has_key(response1, "id")

        email = register_data['email']
        password = register_data['password']
        user_id = self.get_json_value(response1, "id")

        # LOGIN (TO GET TOKEN AND AUTH_SID)
        login_data = {
            'email': email,
            'password': password
        }
        response2 = requests.post(self.login_url, data=login_data)
        auth_sid = self.get_cookie(response2, "auth_sid")
        token = self.get_header(response2, "x-csrf-token")

        # EDIT WITHOUT PASSING TOKEN / AUTH_SID / EITHER
        new_name = "Changed name"

        if condition == "no_cookie":
            response2 = requests.put(
                get_url_with_user_id(self.edit_user_url, user_id),
                headers={"x-csrf-token": token},
                data={'firstName': new_name}
            )
        elif condition == "no_token":
            response2 = requests.put(
                get_url_with_user_id(self.edit_user_url, user_id),
                cookies={"auth_sid": auth_sid},
                data={'firstName': new_name}
            )
        else:
            response2 = requests.put(
                get_url_with_user_id(self.edit_user_url, user_id),
                data={'firstName': new_name}
            )

        Assertions.assert_code_status(response2, 400)
        Assertions.assert_response_content(response2, 'Auth token not supplied')

    def test_edit_another_users_data(self):
        my_created_user_data = self.create_new_user_return_data(register_url=self.register_url, return_login_data=True)
        time.sleep(2)

        # REGISTER NEW USER AND GET THEIR ID
        new_user_id = self.create_new_user_return_data(register_url=self.register_url, return_user_id=True)

        # LOGIN AS AN EXISTING USER AND GET AUTH_SID AND TOKEN
        response1 = requests.post(self.login_url, data=my_created_user_data)
        auth_sid = self.get_cookie(response1, "auth_sid")
        token = self.get_header(response1, "x-csrf-token")

        # TRY TO EDIT THE PREVIOUSLY CREATED USER
        new_name = "Changed name"
        response2 = requests.put(
            get_url_with_user_id(self.edit_user_url, new_user_id),
            cookies={"auth_sid": auth_sid},
            headers={"x-csfr-token": token},
            data={'firstName': new_name}
        )

        Assertions.assert_code_status(response2, 400)
        Assertions.assert_response_content(response2, 'Auth token not supplied')

    def test_edit_email_put_wrong_value(self):
        # REGISTER

        register_data = self.create_new_user_return_data(self.register_url)
        email = register_data['email']
        password = register_data['password']
        user_id = register_data['user_id']

        # LOGIN
        login_data = {
            'email': email,
            'password': password
        }
        response2 = requests.post(self.login_url, data=login_data)
        auth_sid = self.get_cookie(response2, "auth_sid")
        token = self.get_header(response2, "x-csrf-token")

        # EDIT
        new_email = self.prepare_registration_data().get('email').replace("@", "")
        response3 = requests.put(
            get_url_with_user_id(self.edit_user_url, user_id),
            headers={'x-csrf-token': token},
            cookies={'auth_sid': auth_sid},
            data={'email': new_email}
        )

        Assertions.assert_code_status(response3, 400)
        Assertions.assert_response_content(response3, 'Invalid email format')

    def test_edit_first_name_put_too_short_value(self):
        # REGISTER

        register_data = self.create_new_user_return_data(self.register_url)
        email = register_data['email']
        password = register_data['password']
        user_id = register_data['user_id']

        # LOGIN
        login_data = {
            'email': email,
            'password': password
        }
        response2 = requests.post(self.login_url, data=login_data)
        auth_sid = self.get_cookie(response2, "auth_sid")
        token = self.get_header(response2, "x-csrf-token")

        # EDIT
        new_first_name = random_string(random.randint(1, 1))
        response3 = requests.put(
            get_url_with_user_id(self.edit_user_url, user_id),
            headers={'x-csrf-token': token},
            cookies={'auth_sid': auth_sid},
            data={'firstName': new_first_name}
        )

        Assertions.assert_code_status(response3, 400)
        Assertions.assert_response_content(response3, '{"error":"Too short value for field firstName"}')
        # или
        Assertions.assert_json_value_by_name(response3,
                                             'error',
                                             "Too short value for field firstName",
                                             "Wrong error message")
