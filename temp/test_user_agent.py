from json import JSONDecodeError

import pytest
import requests

from test_data.user_agent import user_agents_tuple_list, response_jsons_list


class TestUserAgent:
    user_agents = user_agents_tuple_list

    @pytest.mark.parametrize('user_agent', user_agents)
    def test_user_agent(self, user_agent):
        url = "https://playground.learnqa.ru/ajax/api/user_agent_check"
        headers = {"User-Agent": user_agent[0]}
        response = requests.get(url=url, headers=headers)
        try:
            response_dict = response.json()
        except JSONDecodeError:
            assert False, f"Response is not in JSON format, response text is '{response.text}'"

        expected_response = {}
        for dict in response_jsons_list:
            if dict.get('user_agent') == user_agent[0]:
                expected_response = dict

        assert response_dict['user_agent'] == expected_response['user_agent'], f"The actual user-agent value " \
                                                                               f"is not equal to the expected one " \
                                                                               f"({user_agent})"
        assert response_dict['platform'] == expected_response['platform'], f"The actual platform parameter value " \
                                                                            "is not equal to the expected one"
        assert response_dict['browser'] == expected_response['browser'], f"The actual browser parameter value " \
                                                                            "is not equal to the expected one"
        assert response_dict['device'] == expected_response['device'], f"The actual device parameter value " \
                                                                            "is not equal to the expected one"



