from unittest import mock

import pytest

from botte_http_client import (
    AuthError,
    BotteHttpClient,
    Error404,
    ParamNotFoundInAwsParamStore,
)


class TestBotteHttpClient:
    def setup_method(self):
        self.text = "Hello world from botte http client pytests!"

    def test_happy_flow(self):
        client = BotteHttpClient()
        response = client.send_message(self.text)
        assert response.data["text"] == self.text

    def test_auth_error(self):
        client = BotteHttpClient(botte_be_api_auth_token="XXX")
        with pytest.raises(AuthError):
            client.send_message(self.text)

    def test_base_url_error(self):
        client = BotteHttpClient()
        with pytest.raises(Error404):
            client.send_message(
                self.text,
                base_url="https://5t325uqwq7.execute-api.eu-south-1.amazonaws.com/XXX",
            )

    def test_param_api_auth_token_not_found_in_param_store(self):
        with mock.patch(
            "botte_http_client.http_client.BOTTE_BE_API_AUTHORIZER_TOKEN_PATH_IN_PARAM_STORE",
            "/XXX",
        ):
            client = BotteHttpClient()
            with pytest.raises(ParamNotFoundInAwsParamStore):
                client.send_message(self.text)
