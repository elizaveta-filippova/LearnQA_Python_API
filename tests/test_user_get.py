import allure

from lib.base_case import MyRequests
from lib.base_case import BaseCase
from lib.assertions import Assertions


class TestUserGet(BaseCase):
    user_data = {
        'email': 'vinkotov@example.com',
        'password': '1234'
    }

    @allure.parent_suite('LearnQA user API')
    @allure.suite('Getting user')
    @allure.description('This test successfully gets an existing user')
    def test_get_user_details_not_auth(self):
        with allure.step("Trying to get user with id 2"):
            response = MyRequests.get("/user/2")
        with allure.step(f"Asserting that getting user with id 2 was successful"):
            Assertions.assert_json_has_key(response, "username")
            Assertions.assert_json_has_not_key(response, "email")
            Assertions.assert_json_has_not_key(response, "firstName")
            Assertions.assert_json_has_not_key(response, "lastName")

    @allure.parent_suite('LearnQA user API')
    @allure.suite('Getting user')
    @allure.description('This test allows logged in user to get their own data')
    def test_get_user_details_auth_as_same_user(self):
        with allure.step(f"Logging in with user data {self.user_data}"):
            response1 = MyRequests.post("/user/login", data=self.user_data)
        auth_sid = self.get_cookie(response1, "auth_sid")
        token = self.get_header(response1, "x-csrf-token")
        with allure.step(f"Getting user id from auth method"):
            user_id_from_auth_method = self.get_json_value(response1, "user_id")
        with allure.step(f"Logging in with user data with {user_id_from_auth_method}, {token}, {'suth_sid'}"):
            response2 = MyRequests.get(f"/user/{user_id_from_auth_method}",
                                       headers={'x-csrf-token': token}, cookies={'auth_sid': auth_sid})
        expected_fields = ["username", "email", "firstName", "lastName"]

        Assertions.assert_json_has_keys(response2, expected_fields)

    @allure.suite('Getting user')
    @allure.parent_suite('LearnQA user API')
    @allure.suite('Getting user')
    @allure.description("This test doesn't allow logged in user to get another user's data")
    def test_get_user_details_auth_as_another_user(self):
        with allure.step("Preparing new user's data"):
            new_user_data = self.prepare_registration_data()
        with allure.step(f'Creating new user with data {new_user_data}'):
            response1 = MyRequests.post("/user/",
                                        data=new_user_data)  # создаем нового пользователя
        with allure.step("Getting new user's id"):
            new_user_id = self.get_json_value(response1, "id")

        with allure.step(f"Logging in as our user with {self.user_data}"):
            response2 = MyRequests.post("/user/login",
                                        data=self.user_data)  # логинимся под нашим пользователем
            auth_sid = self.get_cookie(response2, "auth_sid")
            token = self.get_header(response2, "x-csrf-token")

        with allure.step(f"Trying to access user with id {new_user_id}'s data"):
            response3 = MyRequests.get(f"/user/{new_user_id}",
                                       headers={'x-csrf-token': token},
                                       cookies={'auth_sid': auth_sid})  # пытаемся получить данные нового пользователя
        expected_field = "username"
        unexpected_fields = ["email", "firstName", "lastName"]
        with allure.step(f"Assert that we can get {expected_field} but can't get {unexpected_fields}"):
            Assertions.assert_json_has_not_keys(response3, unexpected_fields)
            Assertions.assert_json_has_key(response3, expected_field)
