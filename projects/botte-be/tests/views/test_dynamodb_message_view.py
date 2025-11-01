import botte_dynamodb_tasks
import pytest
from aws_utils.aws_testfactories.dynamodb_event_factory import DynamodbEventFactory
from aws_utils.aws_testfactories.lambda_context_factory import LambdaContextFactory
from ksuid import KsuidMs

from botte_be.views.dynamodb_message_view import lambda_handler


class TestDynamodbMessageView:
    def setup_method(self):
        self.context = LambdaContextFactory().make()
        self.new_image = {
            "PK": {"S": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID},
            "SK": {"S": str(KsuidMs())},
            "TaskId": {"S": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID},
            "SenderApp": {"S": "BOTTE_BE_PYTEST"},
            "Payload": {
                "M": {
                    "text": {
                        "S": "Hello world from (botte-monorepo) botte-be pytests!"
                    },
                }
            },
            "ExpirationTs": {"N": 1698672903},
        }

    def test_happy_flow(self):
        lambda_handler(
            DynamodbEventFactory.make_for_insert(new_image=self.new_image),
            self.context,
        )

    def test_invalid_pk(self):
        self.new_image["PK"] = {"S": "XXX"}
        with pytest.raises(botte_dynamodb_tasks.ValidationError):
            lambda_handler(
                DynamodbEventFactory.make_for_insert(new_image=self.new_image),
                self.context,
            )

    def test_no_pk(self):
        del self.new_image["PK"]
        with pytest.raises(botte_dynamodb_tasks.ValidationError):
            lambda_handler(
                DynamodbEventFactory.make_for_insert(new_image=self.new_image),
                self.context,
            )

    def test_invalid_sk(self):
        self.new_image["SK"] = {"S": "XXX"}
        with pytest.raises(botte_dynamodb_tasks.ValidationError):
            lambda_handler(
                DynamodbEventFactory.make_for_insert(new_image=self.new_image),
                self.context,
            )

    def test_no_sk(self):
        del self.new_image["SK"]
        with pytest.raises(botte_dynamodb_tasks.ValidationError):
            lambda_handler(
                DynamodbEventFactory.make_for_insert(new_image=self.new_image),
                self.context,
            )

    def test_invalid_task_id(self):
        self.new_image["TaskId"] = {
            "S": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID + "XXX"
        }
        with pytest.raises(botte_dynamodb_tasks.ValidationError):
            lambda_handler(
                DynamodbEventFactory.make_for_insert(new_image=self.new_image),
                self.context,
            )

    def test_no_task_id(self):
        del self.new_image["TaskId"]
        with pytest.raises(botte_dynamodb_tasks.ValidationError):
            lambda_handler(
                DynamodbEventFactory.make_for_insert(new_image=self.new_image),
                self.context,
            )

    def test_no_text(self):
        del self.new_image["Payload"]["M"]["text"]
        with pytest.raises(botte_dynamodb_tasks.ValidationError):
            lambda_handler(
                DynamodbEventFactory.make_for_insert(new_image=self.new_image),
                self.context,
            )

    def test_invalid_expiration_ts(self):
        self.new_image["ExpirationTs"] = {"N": "XXX"}
        with pytest.raises(botte_dynamodb_tasks.ValidationError):
            lambda_handler(
                DynamodbEventFactory.make_for_insert(new_image=self.new_image),
                self.context,
            )

    def test_no_expiration_ts(self):
        del self.new_image["ExpirationTs"]
        with pytest.raises(botte_dynamodb_tasks.ValidationError):
            lambda_handler(
                DynamodbEventFactory.make_for_insert(new_image=self.new_image),
                self.context,
            )
