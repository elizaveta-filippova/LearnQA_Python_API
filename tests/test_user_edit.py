import random
import time

import pytest
from lib.my_requests import MyRequests
from lib.base_case import BaseCase
from lib.assertions import Assertions
from lib.helpers import random_string


def get_uri_with_user_id(uri, user_id):
    return f"{uri}{user_id}"


class TestUserEdit(BaseCase):
    exclude_params = [
        ("no_cookie"),
        ("no_token"),
        ("no cookie and token")
    ]

    register_uri = "/user/"
    login_uri = "/user/login"
    get_user_uri = "/user/"
    edit_user_uri = "/user/"

    def test_edit_just_created_user(self):
        # REGISTER
        register_data = self.prepare_registration_data()
        response1 = MyRequests.post(self.register_uri, data=register_data)

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
        response2 = MyRequests.post(self.login_uri, data=login_data)
        auth_sid = self.get_cookie(response2, "auth_sid")
        token = self.get_header(response2, "x-csrf-token")

        # EDIT
        new_name = "Changed name"

        response3 = MyRequests.put(
            get_uri_with_user_id(self.edit_user_uri, user_id),
            headers={'x-csrf-token': token},
            cookies={'auth_sid': auth_sid},
            data={'firstName': new_name}
        )

        Assertions.assert_code_status(response3, 200)

        # GET
        response4 = MyRequests.get(
            url=get_uri_with_user_id(self.get_user_uri, user_id),
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
        response1 = MyRequests.post(self.register_uri, data=register_data)

        Assertions.assert_code_status(response1, 200)
        Assertions.assert_json_has_key(response1, "id")

        email = register_data['email']
        password = register_data['password']
        user_id = self.get_json_value(response1, "id")
        old_name = register_data['firstName']

        # LOGIN (TO GET TOKEN AND AUTH_SID)
        login_data = {
            'email': email,
            'password': password
        }
        response2 = MyRequests.post(self.login_uri, data=login_data)
        auth_sid = self.get_cookie(response2, "auth_sid")
        token = self.get_header(response2, "x-csrf-token")

        # EDIT WITHOUT PASSING TOKEN / AUTH_SID / EITHER
        new_name = "Changed name"

        if condition == "no_cookie":
            response2 = MyRequests.put(
                get_uri_with_user_id(self.edit_user_uri, user_id),
                headers={"x-csrf-token": token},
                data={'firstName': new_name}
            )
        elif condition == "no_token":
            response2 = MyRequests.put(
                get_uri_with_user_id(self.edit_user_uri, user_id),
                cookies={"auth_sid": auth_sid},
                data={'firstName': new_name}
            )
        else:
            response2 = MyRequests.put(
                get_uri_with_user_id(self.edit_user_uri, user_id),
                data={'firstName': new_name}
            )

        Assertions.assert_code_status(response2, 400)
        Assertions.assert_response_content(response2, 'Auth token not supplied')

        # GET USER, CHECK THAT FIRST NAME HASN'T BEEN EDITED
        response4 = MyRequests.get(
            url=get_uri_with_user_id(self.get_user_uri, user_id),
            headers={'x-csrf-token': token},
            cookies={'auth_sid': auth_sid}
        )

        Assertions.assert_json_value_by_name(
            response4,
            "firstName",
            old_name,
            "First name shouldn't have been changed"
        )

    def test_edit_another_users_data(self):
        user_login_data = self.create_new_user_return_data(register_uri=self.register_uri, return_login_data=True)
        time.sleep(2)

        # REGISTER NEW USER AND GET THEIR DATA
        full_user_data = self.create_new_user_return_data(register_uri=self.register_uri)
        user_id = full_user_data['user_id']
        old_name = full_user_data['firstName']
        email = full_user_data['email']
        password = full_user_data['password']
        new_user_login_data = {
            'email': email,
            'password': password
        }

        # LOGIN AS AN EXISTING USER AND GET AUTH_SID AND TOKEN
        response1 = MyRequests.post(self.login_uri, data=user_login_data)
        auth_sid = self.get_cookie(response1, "auth_sid")
        token = self.get_header(response1, "x-csrf-token")

        # TRY TO EDIT THE PREVIOUSLY CREATED USER
        new_name = "Changed name"
        response2 = MyRequests.put(
            get_uri_with_user_id(self.edit_user_uri, user_id),
            cookies={"auth_sid": auth_sid},
            headers={"x-csfr-token": token},
            data={'firstName': new_name}
        )

        Assertions.assert_code_status(response2, 400)
        Assertions.assert_response_content(response2, 'Auth token not supplied')

        # LOGIN AS PREVIOUSLY CREATED USER, GET DATA AND CHECK THAT FIRST NAME HASN'T BEEN EDITED

        response3 = MyRequests.post(self.login_uri, data=new_user_login_data)
        auth_sid = self.get_cookie(response3, "auth_sid")
        token = self.get_header(response3, "x-csrf-token")

        response4 = MyRequests.get(
            url=get_uri_with_user_id(self.get_user_uri, user_id),
            headers={'x-csrf-token': token},
            cookies={'auth_sid': auth_sid}
        )

        Assertions.assert_json_value_by_name(
            response4,
            "firstName",
            old_name,
            "First name shouldn't have been changed"
        )

    def test_edit_email_put_wrong_value(self):
        # REGISTER

        register_data = self.create_new_user_return_data(self.register_uri)
        email = register_data['email']
        password = register_data['password']
        user_id = register_data['user_id']

        # LOGIN
        login_data = {
            'email': email,
            'password': password
        }
        response2 = MyRequests.post(self.login_uri, data=login_data)
        auth_sid = self.get_cookie(response2, "auth_sid")
        token = self.get_header(response2, "x-csrf-token")

        # EDIT
        new_email = self.prepare_registration_data().get('email').replace("@", "")
        response3 = MyRequests.put(
            get_uri_with_user_id(self.edit_user_uri, user_id),
            headers={'x-csrf-token': token},
            cookies={'auth_sid': auth_sid},
            data={'email': new_email}
        )

        Assertions.assert_code_status(response3, 400)
        Assertions.assert_response_content(response3, 'Invalid email format')

        # GET USER, CHECK THAT EMAIL HASN'T BEEN EDITED
        response4 = MyRequests.get(
            url=get_uri_with_user_id(self.get_user_uri, user_id),
            headers={'x-csrf-token': token},
            cookies={'auth_sid': auth_sid}
        )
        Assertions.assert_json_value_by_name(
            response4,
            "email",
            email,
            "Email shouldn't have been changed"
        )

    def test_edit_first_name_put_too_short_value(self):
        # REGISTER

        register_data = self.create_new_user_return_data(self.register_uri)
        email = register_data['email']
        password = register_data['password']
        user_id = register_data['user_id']
        first_name = register_data['firstName']

        # LOGIN
        login_data = {
            'email': email,
            'password': password
        }
        response2 = MyRequests.post(self.login_uri, data=login_data)
        auth_sid = self.get_cookie(response2, "auth_sid")
        token = self.get_header(response2, "x-csrf-token")

        # EDIT
        new_first_name = random_string(random.randint(1, 1))
        response3 = MyRequests.put(
            get_uri_with_user_id(self.edit_user_uri, user_id),
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

        # GET USER, CHECK THAT FIRST NAME HASN'T BEEN EDITED
        response4 = MyRequests.get(
            url=get_uri_with_user_id(self.get_user_uri, user_id),
            headers={'x-csrf-token': token},
            cookies={'auth_sid': auth_sid}
        )

        Assertions.assert_json_value_by_name(
            response4,
            "firstName",
            first_name,
            "First name shouldn't have been changed"
        )
