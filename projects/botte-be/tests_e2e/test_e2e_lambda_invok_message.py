import botte_lambda_client


class TestE2eLambdaInvokMessage:
    """
    Goal: test the direct Lambda invocation interface.
    """

    def setup_method(self):
        self.data = {
            "text": "Hello from (botte-monorepo) botte-be e2e tests for Lambda direct sync invocation message",
            "sender_app": "E2E_TESTS_IN_BOTTE_BE",  # `sender_app` is optional.
        }

    def test_happy_flow(self):
        client = botte_lambda_client.BotteLambdaClient()
        response, status_code = client.send_message(**self.data)
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
        assert response["text"] == self.data["text"]

    def test_async(self):
        client = botte_lambda_client.BotteLambdaClient()
        response, status_code = client.send_message(
            text=self.data["text"].replace("sync", "async"),
            sender_app=self.data["sender_app"],
            do_invoke_sync=False,
        )
        assert response is None
        assert status_code == 202

    # There is no way to test the raising of an exception.
    # Maybe I can add an extra param in the payload, read it in the Lambda source code
    #  and raise an exception.
    # @pytest.mark.skip(
    #     reason="Don't always run this as it causes the sending of an email"
    # )
    # def test_lambda_to_raise_exception_and_email_sent(self):
    #     pass
