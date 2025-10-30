import requests


class TestE2eEndpointMessage:
    def test_happy_flow(self, base_url, http_auth_header):
        url = f"{base_url}/message"
        body = {
            "text": "Hello from (botte-monorepo) Botte BE e2e tests for endpoint message",
            "sender_app": "E2E_TESTS_IN_BOTTE_BE",  # `sender_app` is optional.
        }
        response = requests.post(url, json=body, headers=http_auth_header)
        response.raise_for_status()
        assert response.json()
        # {
        #     "message_id": 157,
        #     "from": {
        #         "id": 6570886232,
        #         "is_bot": True,
        #         "first_name": "Botte",
        #         "username": "realbottebot",
        #     },
        #     "chat": {
        #         "id": 2137200685,
        #         "first_name": "Paolo",
        #         "username": "punto...",
        #         "type": "private",
        #     },
        #     "date": 1698760722,
        #     "text": "Hello from Botte tests e2e",
        # }
        assert response.json()["text"] == body["text"]

    def test_no_auth(self, base_url):
        url = f"{base_url}/message"
        body = {"text": "Hello from Botte tests e2e"}
        headers = {"Authorization": "XXX"}
        response = requests.post(url, json=body, headers=headers)
        assert response.status_code == 403

    # There is no way to test the raising of an exception.
    # Maybe I can add a custom HTTP header, read it in the Lambda source code and
    #  raise an exception.
    # @pytest.mark.skip(
    #     reason="Don't always run this as it causes the sending of an email"
    # )
    # def test_lambda_to_raise_exception_and_email_sent(
    #     self, base_url, auth_header
    # ):
    #     pass
