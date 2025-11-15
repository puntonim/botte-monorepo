from typing import Any

import botte_dynamodb_tasks
import log_utils as logger
import telebot
from aws_lambda_powertools.utilities.typing import LambdaContext

from ..conf import settings
from .views_utils import lambda_static_init

# Objects declared outside the Lambda's handler method are part of Lambda's
# *execution environment*. This execution environment is sometimes reused for subsequent
# function invocations. Note that you can not assume that this always happens.
# Typical use cases: database connection and log init. The same db connection can be
# re-used in some subsequent function invocations. It is recommended though to add
# logic to check if a connection already exists before creating a new one.
# The execution environment also provides 512 MB of *disk space* in the /tmp directory.
# Again, this can be re-used in some subsequent function invocations.
# See: https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtime-environment.html#static-initialization

# This Lambda is configured with 0 retries. So do raise exceptions in the view.

lambda_static_init()

logger.info("DYNAMODB MESSAGE: LOADING")


@logger.get_adapter().inject_lambda_context(log_event=True)
def lambda_handler(event: dict[str, Any], context: LambdaContext) -> None:
    """
    Handler for the Lambda function triggered by an INSERT in a DynamoDB table event.
    The DynamoDB table serves as a task queue.

    This interface meant to be used by consumers that:
     - are running in AWS infra, in the same AWS account as Botte (otherwise they
        would use the HTTP interface in endpoint_message_view.py
     - but cannot invoke Botte Lambdas directly, fi. they are in a VPC with no
        connection to other AWS services nor Internet access (otherwise they would
        use the direct Lambda invocation interface in message_view.py

    Note: one of my patterns is to have Lambdas that connect to a SQLite database stored
     on EFS. EFS requires a VPC, and the Lambda to be in the same VPC. But, for VPCs,
     connection to the Internet and other AWS services requires expensive things like
     internet gateway, NAT or PrivateLink. But VPCs can connect to DynamoDB and S3 (only
     these 2 services) via a VPC Gateway Endpoint for free. So in the end: a Lambda in
     a VPC can connect to Botte DynamoDB interface by using a free VPC Gateway Endpoint
     and this Botte DynamoDB client.

    It sends a Telegram message from the registered bot to the target user, with the
     given message.

    Args:
        event: an AWS event, eg. API Gateway event.
        context: the context passed to the Lambda.

    The `event` is a dict (that can be casted to `DynamoDBStreamEvent`) like:
        {
            "Records": [
                {
                    "eventID": "4d2ea43eb5fd2c78ef00c1ab5f403cb9",
                    "eventName": "INSERT",
                    "eventVersion": "1.1",
                    "eventSource": "aws:dynamodb",
                    "awsRegion": "eu-south-1",
                    "dynamodb": {
                        "ApproximateCreationDateTime": 1762018140,
                        "Keys": {
                            "SK": {
                                "S": "34t1cou0pVRlvW8OECP0J1Q4nJC"
                            },
                            "PK": {
                                "S": "BOTTE_MESSAGE:34t1cou0pVRlvW8OECP0J1Q4nJC"
                            }
                        },
                        "NewImage": {
                            "SenderApp": {
                                "S": "E2E_TESTS_IN_BOTTE_BE"
                            },
                            "TaskId": {
                                "S": "BOTTE_MESSAGE"
                            },
                            "ExpirationTs": {
                                "N": "1762018136"
                            },
                            "SK": {
                                "S": "34t1cou0pVRlvW8OECP0J1Q4nJC"
                            },
                            "Payload": {
                                "M": {
                                    "text": {
                                        "S": "Hello from (botte-monorepo) Botte BE e2e tests for Dynamodb message"
                                    }
                                }
                            },
                            "PK": {
                                "S": "BOTTE_MESSAGE:34t1cou0pVRlvW8OECP0J1Q4nJC"
                            }
                        },
                        "SequenceNumber": "4444500001357803510521810",
                        "SizeBytes": 237,
                        "StreamViewType": "NEW_IMAGE"
                    },
                    "eventSourceARN": "arn:aws:dynamodb:eu-south-1:477353422995:table/botte-be-task-prod/stream/2025-10-31T18:41:51.551"
                }
            ]
        }

    The `context` is a `LambdaContext` instance with properties similar to:
        {
            "aws_request_id": "7841de32-8881-4a1d-a5a9-c84fabfd9dcb",
            "log_group_name": "/aws/lambda/patatrack-botte-prod-dynamodb-message",
            "log_stream_name": "2023/10/29/[$LATEST]0051e91dce2a47819b954d3986f8c619",
            "function_name": "patatrack-botte-prod-dynamodb-message",
            "memory_limit_in_mb": "256",
            "function_version": "$LATEST",
            "invoked_function_arn": "arn:aws:lambda:eu-south-1:477353422995:function:patatrack-botte-prod-dynamodb-message",
            "client_context": null,
            "identity": "CognitoIdentity([cognito_identity_id=None,cognito_identity_pool_id=None])",
            "_epoch_deadline_time_in_ms": 1698587123978
        }
    More info here: https://docs.aws.amazon.com/lambda/latest/dg/python-context.html

    Example:
        To trigger this Lambda, write to the DynamoDB table arn:aws:dynamodb:eu-south-1:477353422995:table/botte-be-task-prod
         a record like:
        {
          "PK": "BOTTE_MESSAGE:2XnrDN2uSq7WWNMADOgCgtMovSj",
          "SK": str(ksuid.KsuidMs()),
          "TaskId": "BOTTE_MESSAGE",
          "SenderApp": "CONTABEL",
          "ExpirationTs": 1698672903,
          "Payload": {
              "text": "Hello world"
          }
        }

        Which in DynamoDB console would be:
        {
            "PK": {"S": "BOTTE_MESSAGE:2XnrDN2uSq7WWNMADOgCgtMovSj"},
            "SK": {"S": "2XnrDN2uSq7WWNMADOgCgtMovSj"},
            "TaskId": {"S": "BOTTE_MESSAGE"},
            "ExpirationTs": {"N": "1699275564"},
            "SenderApp": {"S": "CONTABEL"},
            "Payload": {"M": {"text": {"S": "Hello world"}}},
        }
    """
    logger.info("DYNAMODB MESSAGE: START")

    # Cast the event to the proper Lambda Powertools class.
    # dynamodb_event = DynamoDBStreamEvent(event)

    messages = []
    try:
        for task in botte_dynamodb_tasks.BotteMessageDynamodbTask.yield_from_event(
            event
        ):
            messages.append({"ksuid": task.ksuid, "text": task.text})
    except botte_dynamodb_tasks.ValidationError:
        raise
    messages.sort(key=lambda x: x["ksuid"])

    bot = telebot.TeleBot(settings.TELEGRAM_TOKEN, threaded=False)
    for message in messages:
        message = bot.send_message(
            text=message["text"], chat_id=settings.PUNTONIM_CHAT_ID
        )
