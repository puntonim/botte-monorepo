import json

from aws_utils.aws_testfactories.lambda_context_factory import (
    LambdaContextFactory,
)

from botte_be.views.message_view import lambda_handler


class TestMessageView:
    def setup_method(self):
        self.context = LambdaContextFactory().make()
        self.payload = dict(
            text="Hello world from botte-be pytests!", sender_app="BOTTE_BE_PYTESTS"
        )

    def test_happy_flow(self):
        response = lambda_handler(
            self.payload,
            self.context,
        )
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["text"] == self.payload["text"]

    def test_missing_text(self):
        response = lambda_handler(
            dict(sender_app="BOTTE_BE_PYTESTS"),
            self.context,
        )
        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert body == "Payload parameter 'text' required"
