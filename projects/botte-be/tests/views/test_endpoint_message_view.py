import json
from unittest import mock

from aws_utils.aws_testfactories.api_gateway_event_to_lambda_factory import (
    ApiGatewayV2EventToLambdaFactory,
)
from aws_utils.aws_testfactories.lambda_context_factory import (
    LambdaContextFactory,
)

from botte_be.views.endpoint_message_view import APIGatewayProxyEventV2, lambda_handler


class TestEndpointMessageView:
    def setup_method(self):
        self.context = LambdaContextFactory().make()
        self.text = "Hello world from botte-be pytests!"

    def test_happy_flow(self):
        response = lambda_handler(
            ApiGatewayV2EventToLambdaFactory.make_for_post_request(
                path="/message",
                body_dict={"text": self.text},
            ),
            self.context,
        )
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["text"] == self.text

    def test_missing_text(self):
        response = lambda_handler(
            ApiGatewayV2EventToLambdaFactory.make_for_post_request(
                path="/message",
                body_dict={"textXXX": self.text},
            ),
            self.context,
        )
        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert body == "Body parameter 'text' required"

    def test_body_json_error(self):
        response = lambda_handler(
            ApiGatewayV2EventToLambdaFactory.make_for_post_request(
                path="/message",
                body_json='"XXX',
            ),
            self.context,
        )
        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert body == "Body must be JSON encoded"

    def test_authorization_redacted(self):
        """
        The goal is to make sure that the `event` arg received by `lambda_handler()`
         has any sensitive info redacted, as the event is logged to CloudWatch.
        In this case the sensitive info is the HTTP header `authorization`, which is
         required because this Lambda uses the `tokenAuthorizer` (see serverless.yml).
        """
        # Note: I tried the same spying strategy with `lambda_handler` but it doesn't
        #  work, as we have to invoke lambda_handler() directly here in the test.
        #  So we just use anything in the src code that gets the `event` as arg,
        #  in this case the line: `api_event = APIGatewayProxyEventV2(event)`.
        with mock.patch(
            "botte_be.views.endpoint_message_view.APIGatewayProxyEventV2",
            wraps=APIGatewayProxyEventV2,
        ) as mock_obj:
            response = lambda_handler(
                ApiGatewayV2EventToLambdaFactory.make_for_post_request(
                    path="/message",
                    body_dict={"text": self.text},
                    headers={"authorization": "myauth"},
                ),
                self.context,
            )

        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["text"] == self.text
        assert mock_obj.call_args[0][0]["headers"]["authorization"] == "m**REDACTED**"
