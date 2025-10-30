from aws_utils.aws_testfactories.api_gateway_event_to_lambda_factory import (
    ApiGatewayV2EventToLambdaFactory,
)
from aws_utils.aws_testfactories.lambda_context_factory import (
    LambdaContextFactory,
)
from settings_utils.settings_testutils import override_settings

from botte_be.conf import settings
from botte_be.views.authorizer_view import lambda_handler


class TestAuthorizerView:
    def setup_method(self):
        self.context = LambdaContextFactory().make()

    @override_settings(settings, API_AUTHORIZER_TOKEN="mytoken")
    def test_happy_flow(self):
        response = lambda_handler(
            ApiGatewayV2EventToLambdaFactory.make_for_post_request(
                path="/message",
                headers={"authorization": settings.API_AUTHORIZER_TOKEN},
            ),
            self.context,
        )
        assert response["isAuthorized"] is True

    @override_settings(settings, API_AUTHORIZER_TOKEN="mytoken")
    def test_wrong_secret(self):
        response = lambda_handler(
            ApiGatewayV2EventToLambdaFactory.make_for_post_request(
                path="/message",
                headers={"authorization": "XXX"},
            ),
            self.context,
        )
        assert response["isAuthorized"] is False
