import time

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

    def test_delete_just_created_user(self):
        # REGISTER
        register_data = self.create_new_user_return_data(register_uri=self.register_uri)
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

        # DELETE
        response3 = MyRequests.delete(url=get_uri_with_user_id(self.delete_uri, user_id),
                                      headers={"x-csrf-token": token},
                                      cookies={"auth_sid": auth_sid})
        Assertions.assert_code_status(response3, 200)

        # TRY TO GET JUST DELETED USER
        response4 = MyRequests.get(
            url=get_uri_with_user_id(self.get_user_uri, user_id),
            headers={'x-csrf-token': token},
            cookies={'auth_sid': auth_sid}
        )
        Assertions.assert_code_status(response4, 404)
        Assertions.assert_response_content(response4, "User not found")

    def test_negative_delete_user_with_id_2(self):
        # LOGIN
        login_data = {
            'email': 'vinkotov@example.com',
            'password': '1234'
        }
        user_id = "2"
        response2 = MyRequests.post(self.login_uri, data=login_data)
        auth_sid = self.get_cookie(response2, "auth_sid")
        token = self.get_header(response2, "x-csrf-token")

        # DELETE
        response3 = MyRequests.delete(url=get_uri_with_user_id(uri=self.delete_uri,
                                                               user_id=user_id),
                                      headers={"x-csrf-token": token},
                                      cookies={"auth_sid": auth_sid})
        Assertions.assert_code_status(response3, 400)
        Assertions.assert_response_content(response3, 'Please, do not delete test users with ID 1, 2, 3, 4 or 5.')

        # GET USER AND MAKE SURE IT'S NOT DELETED

        response4 = MyRequests.get(
            url=get_uri_with_user_id(self.get_user_uri, user_id=user_id),
            headers={'x-csrf-token': token},
            cookies={'auth_sid': auth_sid}
        )
        expected_fields = [ "id", "username", "email", "firstName", "lastName"]
        Assertions.assert_code_status(response4, 200)
        Assertions.assert_json_has_keys(response4, expected_fields)
        Assertions.assert_json_value_by_name(
            response4,
            "id",
            user_id,
            f"This is not user with id {user_id}"
        )

    def test_negative_try_delete_another_user(self):
        full_my_user_data = self.create_new_user_return_data(register_uri=self.register_uri)
        my_user_id = full_my_user_data['user_id']
        my_user_login_data = {
            'email': full_my_user_data['email'],
            'password': full_my_user_data['password']
        }
        time.sleep(2)

        # REGISTER NEW USER AND GET THEIR DATA
        full_user_data = self.create_new_user_return_data(register_uri=self.register_uri)
        new_user_id = full_user_data['user_id']
        new_user_login_data = {
            'email': full_user_data['email'],
            'password': full_user_data['password']
        }

        # LOGIN AS AN EXISTING USER AND GET AUTH_SID AND TOKEN
        response1 = MyRequests.post(self.login_uri, data=my_user_login_data)
        auth_sid = self.get_cookie(response1, "auth_sid")
        token = self.get_header(response1, "x-csrf-token")

        # TRY AND DELETE THE PREVIOUSLY CREATED USER
        response2 = MyRequests.delete(url=get_uri_with_user_id(uri=self.delete_uri,
                                                               user_id=new_user_id),
                                      headers={"x-csrf-token": token},
                                      cookies={"auth_sid": auth_sid})

        Assertions.assert_code_status(response2, 400)

        # TRY AND GET NEW USER (THAT SHOULDN'T HAVE BEEN DELETED)

        response3 = MyRequests.post(self.login_uri, data=new_user_login_data)
        auth_sid = self.get_cookie(response3, "auth_sid")
        token = self.get_header(response3, "x-csrf-token")

        response4 = MyRequests.get(
            url=get_uri_with_user_id(self.get_user_uri, new_user_id),
            headers={'x-csrf-token': token},
            cookies={'auth_sid': auth_sid}
        )

        expected_fields = ["id", "username", "email", "firstName", "lastName"]
        Assertions.assert_code_status(response4, 200)
        Assertions.assert_json_has_keys(response4, expected_fields)
        Assertions.assert_json_value_by_name(
            response4,
            "id",
            new_user_id,
            f"This is not user with id {new_user_id}"
        )


