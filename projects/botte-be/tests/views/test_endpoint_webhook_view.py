from unittest import mock

from aws_utils.aws_testfactories.api_gateway_event_to_lambda_factory import (
    ApiGatewayV2EventToLambdaFactory,
)
from aws_utils.aws_testfactories.lambda_context_factory import (
    LambdaContextFactory,
)

from botte_be.views import endpoint_webhook_view
from botte_be.views.endpoint_webhook_view import (
    APIGatewayProxyEventV2,
    UnknownChatId,
    lambda_handler,
)


class TestEndpointWebhookView:
    def setup_method(self):
        # IMP: set the cached bot to None, or it will behave unpredictably.
        endpoint_webhook_view.bot = None

        self.context = LambdaContextFactory().make()
        self.echo_body = {
            "update_id": 876674333,
            "message": {
                "message_id": 66,
                "from": {
                    "id": 2137200685,
                    "is_bot": False,
                    "first_name": "Paolo",
                    "username": "punto...",
                    "language_code": "en",
                },
                "chat": {
                    "id": 2137200685,
                    "first_name": "Paolo",
                    "username": "punto...",
                    "type": "private",
                },
                "date": 1698409069,
                "text": "/echo Hello botte from botte-be pytests!",
                "entities": [{"offset": 0, "length": 5, "type": "bot_command"}],
            },
        }
        self.shared_link_body = {
            "update_id": 876674395,
            "message": {
                "message_id": 34434,
                "from": {
                    "id": 2137200685,
                    "is_bot": False,
                    "first_name": "Paolo",
                    "username": "punto...",
                    "language_code": "en",
                },
                "chat": {
                    "id": 2137200685,
                    "first_name": "Paolo",
                    "username": "punto...",
                    "type": "private",
                },
                "date": 1763378364,
                "text": "https://youtu.be/eytD1MZUHNY?si=sOdAbx3kEpjNSLDF",
                "entities": [{"offset": 0, "length": 48, "type": "url"}],
                "link_preview_options": {
                    "url": "https://youtu.be/eytD1MZUHNY?si=sOdAbx3kEpjNSLDF"
                },
            },
        }

    def test_echo(self):
        response = lambda_handler(
            ApiGatewayV2EventToLambdaFactory.make_for_post_request(
                path="/telegram-webhook", body_dict=self.echo_body
            ),
            self.context,
        )
        assert response["statusCode"] == 200

    def test_shared_link(self):
        response = lambda_handler(
            ApiGatewayV2EventToLambdaFactory.make_for_post_request(
                path="/telegram-webhook", body_dict=self.shared_link_body
            ),
            self.context,
        )
        assert response["statusCode"] == 200

    def test_unknown_chat_id(self, caplog):
        body = self.shared_link_body
        body["message"]["chat"]["id"] = 999
        response = lambda_handler(
            ApiGatewayV2EventToLambdaFactory.make_for_post_request(
                path="/telegram-webhook", body_dict=body
            ),
            self.context,
        )
        assert response["statusCode"] == 200
        assert isinstance(caplog.records[2].exc_info[1], UnknownChatId)

    def test_authorization_redacted(self):
        """
        The goal is to make sure that the `event` arg received by `lambda_handler()`
         has any sensitive info redacted, as the event is logged to CloudWatch.
        In this case the sensitive info is the HTTP header `x-telegram-bot-api-secret-token`,
         which is sent by Telegram webhook and is required because this Lambda uses
         the `webhookAuthorizer` (see serverless.yml).
        """
        # Note: I tried the same spying strategy with `lambda_handler` but it doesn't
        #  work, as we have to invoke lambda_handler() directly here in the test.
        #  So we just use anything in the src code that gets the `event` as arg,
        #  in this case the line: `api_event = APIGatewayProxyEventV2(event)`.
        with mock.patch(
            "botte_be.views.endpoint_webhook_view.APIGatewayProxyEventV2",
            wraps=APIGatewayProxyEventV2,
        ) as mock_obj:
            response = lambda_handler(
                ApiGatewayV2EventToLambdaFactory.make_for_post_request(
                    path="/message",
                    body_dict=self.echo_body,
                    headers={"x-telegram-bot-api-secret-token": "myauth"},
                ),
                self.context,
            )

        assert response["statusCode"] == 200
        assert (
            mock_obj.call_args[0][0]["headers"]["x-telegram-bot-api-secret-token"]
            == "m**REDACTED**"
        )
