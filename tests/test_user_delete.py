import time

import allure

from lib.assertions import Assertions
from lib.base_case import BaseCase
from lib.my_requests import MyRequests


def get_uri_with_user_id(uri, user_id):
    return f"{uri}{user_id}"


class TestUserDelete(BaseCase):
    register_uri = "/user/"
    login_uri = "/user/login"
    delete_uri = "/user/"
    get_user_uri = "/user/"

    @allure.parent_suite('LearnQA user API')
    @allure.suite('Deleting user')
    @allure.description("This test successfully deletes just created user")
    def test_delete_just_created_user(self):
        # REGISTER
        with allure.step("Creating new user"):
            register_data = self.create_new_user_return_data(register_uri=self.register_uri)
            with allure.step(f'Getting {register_data}'):
                email = register_data['email']
                password = register_data['password']
                user_id = register_data['user_id']

        # LOGIN
        login_data = {
            'email': email,
            'password': password
        }
        with allure.step("Logging in with login data, auth_sid cookie, token"):
            response2 = MyRequests.post(self.login_uri, data=login_data)
            auth_sid = self.get_cookie(response2, "auth_sid")
            token = self.get_header(response2, "x-csrf-token")

        # DELETE
        with allure.step("Trying to delete just created user"):
            response3 = MyRequests.delete(url=get_uri_with_user_id(self.delete_uri, user_id),
                                          headers={"x-csrf-token": token},
                                          cookies={"auth_sid": auth_sid})
        with allure.step("Asserting deletion is successful"):
            Assertions.assert_code_status(response3, 200)

        # TRY TO GET JUST DELETED USER
        with allure.step("Trying to access just deleted user"):
            response4 = MyRequests.get(
                url=get_uri_with_user_id(self.get_user_uri, user_id),
                headers={'x-csrf-token': token},
                cookies={'auth_sid': auth_sid}
            )
        with allure.step("Asserting that it's impossible to get a deleted user"):
            Assertions.assert_code_status(response4, 404)
            Assertions.assert_response_content(response4, "User not found")

    @allure.parent_suite('LearnQA user API')
    @allure.suite('Deleting user')
    @allure.description("This test checks that you can't delete user with id 2")
    def test_negative_delete_user_with_id_2(self):
        # LOGIN
        login_data = {
            'email': 'vinkotov@example.com',
            'password': '1234'
        }
        user_id = "2"
        with allure.step(f"Logging in with login data {login_data}"):
            response2 = MyRequests.post(self.login_uri, data=login_data)
            auth_sid = self.get_cookie(response2, "auth_sid")
            token = self.get_header(response2, "x-csrf-token")

        # DELETE
        with allure.step(f"Trying to delete just created user with user id {user_id}"):
            response3 = MyRequests.delete(url=get_uri_with_user_id(uri=self.delete_uri,
                                                                   user_id=user_id),
                                          headers={"x-csrf-token": token},
                                          cookies={"auth_sid": auth_sid})
        with allure.step("Asserting that deletion was unsuccessful"):
            Assertions.assert_code_status(response3, 400)
            Assertions.assert_response_content(response3, 'Please, do not delete test users with ID 1, 2, 3, 4 or 5.')

        # GET USER AND MAKE SURE IT'S NOT DELETED

        with allure.step(f"Getting user with user id {user_id}, token {token}, cookie {auth_sid}"):
            response4 = MyRequests.get(
                url=get_uri_with_user_id(self.get_user_uri, user_id=user_id),
                headers={'x-csrf-token': token},
                cookies={'auth_sid': auth_sid}
            )
        with allure.step(f"Assert that the user with id {user_id} still exists"):
            expected_fields = ["id", "username", "email", "firstName", "lastName"]
            Assertions.assert_code_status(response4, 200)
            Assertions.assert_json_has_keys(response4, expected_fields)
            Assertions.assert_json_value_by_name(
                response4,
                "id",
                user_id,
                f"This is not user with id {user_id}"
            )

    @allure.parent_suite('LearnQA user API')
    @allure.suite('Deleting user')
    @allure.description("This test checks that you can't delete another user")
    def test_negative_try_delete_another_user(self):
        with allure.step("Getting full user data of my user"):
            full_my_user_data = self.create_new_user_return_data(register_uri=self.register_uri)
        my_user_id = full_my_user_data['user_id']
        with allure.step(f"Getting my user's email and password from full user data {full_my_user_data}"):
            my_user_login_data = {
                'email': full_my_user_data['email'],
                'password': full_my_user_data['password']
            }
        with allure.step("Waiting for 2 seconds..."):
            time.sleep(2)

        # REGISTER NEW USER AND GET THEIR DATA
        with allure.step("Getting full user data of new user"):
            full_user_data = self.create_new_user_return_data(register_uri=self.register_uri)
        with allure.step(f"Getting new user's id from full user data {full_user_data}"):
            new_user_id = full_user_data['user_id']
        with allure.step(f"Getting my user's email and password from full user data {full_user_data}"):
            new_user_login_data = {
                'email': full_user_data['email'],
                'password': full_user_data['password']
            }

        # LOGIN AS AN EXISTING USER AND GET AUTH_SID AND TOKEN
        with allure.step(f"Logging in with my login data {my_user_login_data}"):
            response1 = MyRequests.post(self.login_uri, data=my_user_login_data)
            auth_sid = self.get_cookie(response1, "auth_sid")
            token = self.get_header(response1, "x-csrf-token")

        # TRY AND DELETE THE PREVIOUSLY CREATED USER
        with allure.step(f"Trying to delete the previously created user with user id {new_user_id}"):
            response2 = MyRequests.delete(url=get_uri_with_user_id(uri=self.delete_uri,
                                                                   user_id=new_user_id),
                                          headers={"x-csrf-token": token},
                                          cookies={"auth_sid": auth_sid})
        with allure.step("Assert that you can't delete another user"):
            Assertions.assert_code_status(response2, 400)

        # TRY AND GET NEW USER (THAT SHOULDN'T HAVE BEEN DELETED)

        with allure.step(f"Logging in with new user's login data {new_user_login_data}"):
            response3 = MyRequests.post(self.login_uri, data=new_user_login_data)
            auth_sid = self.get_cookie(response3, "auth_sid")
            token = self.get_header(response3, "x-csrf-token")

        with allure.step("Trying to get new user's full data"):
            response4 = MyRequests.get(
                url=get_uri_with_user_id(self.get_user_uri, new_user_id),
                headers={'x-csrf-token': token},
                cookies={'auth_sid': auth_sid}
            )

        expected_fields = ["id", "username", "email", "firstName", "lastName"]

        with allure.step("Making sure that the new user still exists and the data is correct"):
            Assertions.assert_code_status(response4, 200)
            Assertions.assert_json_has_keys(response4, expected_fields)
            Assertions.assert_json_value_by_name(
            response4,
            "id",
            new_user_id,
            f"This is not user with id {new_user_id}"
        )
