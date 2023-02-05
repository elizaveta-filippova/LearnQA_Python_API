import allure
import random
import time

import pytest
from lib.my_requests import MyRequests
from lib.base_case import BaseCase
from lib.assertions import Assertions
from lib.helpers import random_string


def get_uri_with_user_id(uri, user_id):
    return f"{uri}{user_id}"


@allure.parent_suite('LearnQA user API')
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

    @allure.parent_suite('LearnQA user API')
    @allure.suite('Editing user')
    @allure.description('This test successfully edits just created user')
    @pytest.mark.positive
    def test_edit_just_created_user(self):
        # REGISTER

        register_data = self.prepare_registration_data()
        with allure.step(f"Creating new user with register data {register_data}"):
            response1 = MyRequests.post(self.register_uri, data=register_data)
        with allure.step("Assert that user has been created"):
            Assertions.assert_code_status(response1, 200)
            Assertions.assert_json_has_key(response1, "id")

        email = register_data['email']
        firstName = register_data['firstName']
        password = register_data['password']
        user_id = self.get_json_value(response1, "id")

        # LOGIN
        with allure.step('Preparing login data'):
            login_data = {
                'email': email,
                'password': password
            }
        with allure.step(f"Logging in with login data {login_data}, getting cookie and token"):
            response2 = MyRequests.post(self.login_uri, data=login_data)
            auth_sid = self.get_cookie(response2, "auth_sid")
            token = self.get_header(response2, "x-csrf-token")

        # EDIT
        new_name = "Changed name"
        with allure.step(f"Editing the user's name: instead of {firstName} set {new_name}"):
            response3 = MyRequests.put(
                get_uri_with_user_id(self.edit_user_uri, user_id),
                headers={'x-csrf-token': token},
                cookies={'auth_sid': auth_sid},
                data={'firstName': new_name}
            )
        with allure.step("Asserting that edition went successfully"):
            Assertions.assert_code_status(response3, 200)

        # GET
        with allure.step("Getting user's data and checking whether the user's name is changed"):
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
    @allure.parent_suite('LearnQA user API')
    @allure.suite('Editing user')
    @allure.description("This test unsuccessfully tries to edit user's data while unauthorized")
    @pytest.mark.negative
    def test_edit_data_while_unauthorized(self, condition):
        # REGISTER
        register_data = self.prepare_registration_data()
        with allure.step(f"Creating new user with register data {register_data}"):
            response1 = MyRequests.post(self.register_uri, data=register_data)
        with allure.step("Assert that user has been created"):
            Assertions.assert_code_status(response1, 200)
            Assertions.assert_json_has_key(response1, "id")

        email = register_data['email']
        password = register_data['password']
        user_id = self.get_json_value(response1, "id")
        old_name = register_data['firstName']

        # LOGIN (TO GET TOKEN AND AUTH_SID)
        with allure.step('Preparing login data'):
            login_data = {
                'email': email,
                'password': password
            }
        with allure.step(f"Logging in with login data {login_data}, getting cookie and token"):
            response2 = MyRequests.post(self.login_uri, data=login_data)
            auth_sid = self.get_cookie(response2, "auth_sid")
            token = self.get_header(response2, "x-csrf-token")

        # EDIT WITHOUT PASSING TOKEN / AUTH_SID / EITHER
        new_name = "Changed name"
        with allure.step(f"Trying to edit the user's name: instead of {old_name} set {new_name} "
                         f"without either cookie or token or both"):

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
        with allure.step("Assert that edition was unsuccessful"):
            Assertions.assert_code_status(response2, 400)
            Assertions.assert_response_content(response2, 'Auth token not supplied')

        # GET USER, CHECK THAT FIRST NAME HASN'T BEEN EDITED
        with allure.step(f"Get user with user_id {user_id}"):
            response4 = MyRequests.get(
                url=get_uri_with_user_id(self.get_user_uri, user_id),
                headers={'x-csrf-token': token},
                cookies={'auth_sid': auth_sid}
        )

        with allure.step(f"Assert that old name {old_name} hasn't changed"):
            Assertions.assert_json_value_by_name(
                response4,
                "firstName",
                old_name,
                "First name shouldn't have been changed"
        )

    @allure.parent_suite('LearnQA user API')
    @allure.suite('Editing user')
    @allure.description("This test unsuccessfully tries to edit another user's data")
    @pytest.mark.negative
    def test_edit_another_users_data(self):
        with allure.step("Creating new user and get login data"):
            user_login_data = self.create_new_user_return_data(register_uri=self.register_uri, return_login_data=True)
        with allure.step("Waiting for 2 seconds..."):
            time.sleep(2)

        # REGISTER NEW USER AND GET THEIR DATA
        with allure.step("Creating another user"):
            full_user_data = self.create_new_user_return_data(register_uri=self.register_uri)
        user_id = full_user_data['user_id']
        old_name = full_user_data['firstName']
        email = full_user_data['email']
        password = full_user_data['password']
        with allure.step("Creating getting new user's login data"):
            new_user_login_data = {
            'email': email,
            'password': password
        }

        # LOGIN AS AN EXISTING USER AND GET AUTH_SID AND TOKEN
        with allure.step("Logging in as the first user's data"):
            response1 = MyRequests.post(self.login_uri, data=user_login_data)
            auth_sid = self.get_cookie(response1, "auth_sid")
            token = self.get_header(response1, "x-csrf-token")

        # TRY TO EDIT THE PREVIOUSLY CREATED USER
        with allure.step(f"Trying to edit the second user's name {old_name}"):
            new_name = "Changed name"
            response2 = MyRequests.put(
            get_uri_with_user_id(self.edit_user_uri, user_id),
                cookies={"auth_sid": auth_sid},
                headers={"x-csfr-token": token},
                data={'firstName': new_name}
        )
        with allure.step("Asserting that the name of another user's can't be edited"):
            Assertions.assert_code_status(response2, 400)
            Assertions.assert_response_content(response2, 'Auth token not supplied')

        # LOGIN AS PREVIOUSLY CREATED USER, GET DATA AND CHECK THAT FIRST NAME HASN'T BEEN EDITED
        with allure.step(f"Logging in with the second user's (id login data {new_user_login_data}"):
            response3 = MyRequests.post(self.login_uri, data=new_user_login_data)
            auth_sid = self.get_cookie(response3, "auth_sid")
            token = self.get_header(response3, "x-csrf-token")
        with allure.step("Logging in as the first user and getting their data"):
            response4 = MyRequests.get(
                url=get_uri_with_user_id(self.get_user_uri, user_id),
                headers={'x-csrf-token': token},
                cookies={'auth_sid': auth_sid}
            )
        with allure.step("Asserting that the first name of the second user hasn't been edited"):
            Assertions.assert_json_value_by_name(
                response4,
                "firstName",
                old_name,
                "First name shouldn't have been changed"
            )

    @allure.parent_suite('LearnQA user API')
    @allure.suite('Editing user')
    @allure.description("This test unsuccessfully tries to change user's email putting unsupported value")
    @pytest.mark.negative
    def test_edit_email_put_wrong_value(self):
        # REGISTER
        register_data = self.create_new_user_return_data(self.register_uri)
        with allure.step(f"Registering new user and getting their register data {register_data}"):
            email = register_data['email']
            password = register_data['password']
            user_id = register_data['user_id']

        # LOGIN
        login_data = {
            'email': email,
            'password': password
        }
        with allure.step(f"Logging in as the newly created user with id {user_id} and login data {login_data}"):
            response2 = MyRequests.post(self.login_uri, data=login_data)
            auth_sid = self.get_cookie(response2, "auth_sid")
            token = self.get_header(response2, "x-csrf-token")

        # EDIT
        new_email = self.prepare_registration_data().get('email').replace("@", "")
        with allure.step(f"Trying to edit the user by replacing {email} with {new_email}"):
            response3 = MyRequests.put(
                get_uri_with_user_id(self.edit_user_uri, user_id),
                headers={'x-csrf-token': token},
                cookies={'auth_sid': auth_sid},
                data={'email': new_email}
        )
        with allure.step("Asserting that you can't use email without '@' symbol"):
            Assertions.assert_code_status(response3, 400)
            Assertions.assert_response_content(response3, 'Invalid email format')

        # GET USER, CHECK THAT EMAIL HASN'T BEEN EDITED
        with allure.step(f"Getting the created user with id {user_id}"):
            response4 = MyRequests.get(
                url=get_uri_with_user_id(self.get_user_uri, user_id),
                headers={'x-csrf-token': token},
                cookies={'auth_sid': auth_sid}
        )
        with allure.step("Asserting that email hasn't been changed"):
            Assertions.assert_json_value_by_name(
                response4,
                "email",
                email,
                "Email shouldn't have been changed"
            )

    @allure.parent_suite('LearnQA user API')
    @allure.suite('Editing user')
    @allure.description("This test unsuccessfully tries to change user's first name putting a value that's too short")
    @pytest.mark.negative
    def test_edit_first_name_put_too_short_value(self):
        # REGISTER
        with allure.step("Creating a new user"):
            register_data = self.create_new_user_return_data(self.register_uri)
        with allure.step(f"Getting user's data from register data {register_data}"):
            email = register_data['email']
            password = register_data['password']
            user_id = register_data['user_id']
            first_name = register_data['firstName']

        # LOGIN
        with allure.step("Getting login data"):
            login_data = {
                'email': email,
                'password': password
            }
        with allure.step(f"Logging in as user with user with id {user_id} and login data {login_data}"):
            response2 = MyRequests.post(self.login_uri, data=login_data)
        auth_sid = self.get_cookie(response2, "auth_sid")
        token = self.get_header(response2, "x-csrf-token")

        # EDIT
        new_first_name = random_string(random.randint(1, 1))
        with allure.step(f"Trying to edit the user by replacing first name {first_name} "
                         f"with new first name {new_first_name}"):
            response3 = MyRequests.put(
                get_uri_with_user_id(self.edit_user_uri, user_id),
                headers={'x-csrf-token': token},
                cookies={'auth_sid': auth_sid},
                data={'firstName': new_first_name}
            )

        with allure.step("Asserting that you can't put a name that's too short"):
            Assertions.assert_code_status(response3, 400)
            Assertions.assert_response_content(response3, '{"error":"Too short value for field firstName"}')
        # или
            Assertions.assert_json_value_by_name(response3,
                                             'error',
                                             "Too short value for field firstName",
                                             "Wrong error message")

        # GET USER, CHECK THAT FIRST NAME HASN'T BEEN EDITED
        with allure.step(f"Logging in with user with user_id {user_id} again"):
            response4 = MyRequests.get(
                url=get_uri_with_user_id(self.get_user_uri, user_id),
                headers={'x-csrf-token': token},
                cookies={'auth_sid': auth_sid}
            )
        with allure.step("Asserting that username hasn't been changed"):
            Assertions.assert_json_value_by_name(
                response4,
                "firstName",
                first_name,
                "First name shouldn't have been changed"
            )
