import json

import pytest
from aws_utils.aws_testfactories.api_gateway_event_to_lambda_factory import (
    ApiGatewayV2EventToLambdaFactory,
)
from aws_utils.aws_testfactories.lambda_context_factory import (
    LambdaContextFactory,
)

from botte_be.conf import settings
from botte_be.views.endpoint_introspection_view import (
    UnhealthEndpointException,
    lambda_handler,
)


class TestIntrospection:
    def setup_method(self):
        self.context = LambdaContextFactory().make()

    @pytest.mark.withlogs
    def test_health(self, caplog):
        response = lambda_handler(
            ApiGatewayV2EventToLambdaFactory.make_for_get_request(path="/health"),
            self.context,
        )
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body

        # The first log is the event logged by `@logger.get_adapter().inject_lambda_context(log_event=True)`.
        msg = eval(caplog.records[0].message)
        assert msg["routeKey"] == "GET /health"
        # Then my logs.
        assert caplog.records[1].message == "ENDPOINT INTROSPECTION: START"
        # Notice that `logger.debug("Debug log entry")` did not make any log statement
        #  as the log level is set to info.
        assert caplog.records[2].message == "Info log entry"
        assert caplog.records[3].message == "Responding 200"

    def test_unhealth(self):
        with pytest.raises(UnhealthEndpointException):
            lambda_handler(
                ApiGatewayV2EventToLambdaFactory.make_for_get_request(path="/unhealth"),
                self.context,
            )

    def test_version(self):
        response = lambda_handler(
            ApiGatewayV2EventToLambdaFactory.make_for_get_request(path="/version"),
            self.context,
        )
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["appName"] == settings.APP_NAME
