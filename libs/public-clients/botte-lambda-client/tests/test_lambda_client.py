from unittest import mock

import pytest

import botte_lambda_client


class TestBotteLambdaClient:
    def test_happy_flow(self):
        text = "Hello world from (botte-monorepo) botte-lambda-client sync pytests!"
        client = botte_lambda_client.BotteLambdaClient()
        response, status_code = client.send_message(text)
        assert response["text"] == text
        assert status_code == 200

    def test_async(self):
        text = "Hello world from (botte-monorepo) botte-lambda-client async pytests!"
        client = botte_lambda_client.BotteLambdaClient()
        response, status_code = client.send_message(text, do_invoke_sync=False)
        assert response is None
        assert status_code == 202

    def test_lambda_name_error(self):
        text = "Hello world from (botte-monorepo) botte-lambda-client sync pytests!"
        with mock.patch(
            "botte_lambda_client.lambda_client.LAMBDA_NAME",
            "XXX",
        ):
            client = botte_lambda_client.BotteLambdaClient()
            with pytest.raises(botte_lambda_client.BotteLambdaNotFound):
                client.send_message(text)
