from unittest import mock

import pytest

import botte_lambda_client


class TestBotteLambdaClient:
    def setup_method(self):
        self.text = "Hello world from botte lambda client pytests!"

    def test_happy_flow(self):
        client = botte_lambda_client.BotteLambdaClient()
        response, status_code = client.send_message(self.text)
        assert response["text"] == self.text
        assert status_code == 200

    def test_lambda_name_error(self):
        with mock.patch(
            "botte_lambda_client.lambda_client.LAMBDA_NAME",
            "XXX",
        ):
            client = botte_lambda_client.BotteLambdaClient()
            with pytest.raises(botte_lambda_client.BotteLambdaNotFound):
                client.send_message(self.text)
