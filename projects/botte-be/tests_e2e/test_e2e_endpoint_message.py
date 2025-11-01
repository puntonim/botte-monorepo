import botte_http_client
import pytest


class TestE2eEndpointMessage:
    def setup_method(self):
        self.data = {
            "text": "Hello from (botte-monorepo) botte-be e2e tests for endpoint message",
            "sender_app": "E2E_TESTS_IN_BOTTE_BE",  # `sender_app` is optional.
        }

    def test_happy_flow(self):
        client = botte_http_client.BotteHttpClient()
        response = client.send_message(**self.data)
        # response.data is like:
        # {
        #     "message_id": 34268,
        #     "from": {
        #         "id": 6570886232,
        #         "is_bot": True,
        #         "first_name": "Botte BOT",
        #         "username": "realbottebot",
        #     },
        #     "chat": {
        #         "id": 2137200685,
        #         "first_name": "Paolo",
        #         "username": "puntonim",
        #         "type": "private",
        #     },
        #     "date": 1761929375,
        #     "text": "Hello from (botte-monorepo) Botte BE e2e tests for endpoint message",
        # }
        assert response.data["text"] == self.data["text"]

    def test_no_auth(self):
        client = botte_http_client.BotteHttpClient(botte_be_api_auth_token="XXX")
        with pytest.raises(botte_http_client.AuthError):
            client.send_message(**self.data)

    # There is no way to test the raising of an exception.
    # Maybe I can add a custom HTTP header, read it in the Lambda source code and
    #  raise an exception.
    # @pytest.mark.skip(
    #     reason="Don't always run this as it causes the sending of an email"
    # )
    # def test_lambda_to_raise_exception_and_email_sent(self):
    #     pass
