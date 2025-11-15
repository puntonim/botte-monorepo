"""
** BOTTE DYNAMODB CLIENT **
===========================

This Botte DynamoDB client is the preferred client to interact with Botte in order
 to send Telegram text messages, when the consumer:
 - is running in AWS infra, in the same AWS account as Botte (otherwise use `botte-http-client`)
 - but it cannot invoke Botte Lambdas directly, fi. it is in a VPC with no connection to
    other AWS services nor Internet access (otherwise use `botte-lambda-client`)

Multiple Telegram messages will be sent by many Lambdas concurrently, unless the
 `do_send_msg_fifo` (and optionally `fifo_group_id`) arg is given.

Note: one of my patterns is to have Lambdas that connect to a SQLite database stored
 on EFS. EFS requires a VPC, and the Lambda to be in the same VPC. But, for VPCs,
 connection to the Internet and other AWS services requires expensive things like
 internet gateway, NAT or PrivateLink. But VPCs can connect to DynamoDB and S3 (only
 these 2 services) via a VPC Gateway Endpoint for free. So in the end: a Lambda in
 a VPC can connect to Botte DynamoDB interface by using a free VPC Gateway Endpoint
 and this Botte DynamoDB client.
 See contabel project in patatrack-monorepo for the VPC setup.

```py
import botte_dynamodb_client

client = botte_dynamodb_client.BotteDynamodbClient()
response = client.send_message(
    "Hello world!",
    sender_app="BOTTE_DYNAMODB_CLIENT_PYTESTS",
)
```
"""

import aws_dynamodb_client
import botte_dynamodb_tasks
import datetime_utils

__all__ = [
    "BotteDynamodbClient",
]

TABLE_NAME = "botte-be-task-prod"


class BotteDynamodbClient:
    def send_message(
        self,
        text: str,
        sender_app: str = "BOTTE_DYNAMODB_CLIENT",
        do_send_msg_fifo: bool = False,
        fifo_group_id: str | None = None,
        table_name: str = TABLE_NAME,
        # Used in pytests, see docstring.
        botte_message_dynamodb_task_extra_kwargs: dict | None = None,
    ):
        """
        Args:
            text (str): the text of the message to send.
            sender_app (str): just an identifier, default: "BOTTE_HTTP_CLIENT".
            do_send_msg_fifo: True to have Botte Lambda send this message
             sequentially in FIFO order, together with all other messages with
             do_send_msg_fifo=True and the same fifo_group_id.
             False to maximize concurrency, so many Lambdas will send all msgs with
             do_send_msg_fifo=False concurrently.
            fifo_group_id: only useful in a very rare use case: when you have 2+ groups
             of msgs that need to be sent by Lambda sequentially. You will have
             2+ concurrent Lambdas that send msgs with the same fifo_group_id
             sequentially. So it's concurrency between groups, but sequentially for
             msgs of the same group.
            table_name (str): name of DynamoDB table used as task queue by Botte
             Backend, optional.
            botte_message_dynamodb_task_extra_kwargs (dict): optional, used in pytests
             to be passed down to BotteMessageDynamodbTask() to override
             time-based and random values, example:
                from ksuid import KsuidMs
                botte_message_dynamodb_task_extra_kwargs=dict(
                    ksuid=KsuidMs.from_base62("34sbgpYvCbhsUZtNvB8OVmsxsAp"),
                    expiration_ts=1762002142,
                )
        """

        table = aws_dynamodb_client.DynamodbTable(table_name)
        now = datetime_utils.now_utc()
        data = dict(
            text=text,
            sender_app=sender_app,
            do_process_task_fifo=do_send_msg_fifo,
            fifo_group_id=fifo_group_id,
            expiration_ts=round(now.timestamp()),
        )
        data.update(botte_message_dynamodb_task_extra_kwargs or {})
        task = botte_dynamodb_tasks.BotteMessageDynamodbTask(**data)
        try:
            response = table.write(item=task.to_dict())
        # List all known exceptions.
        except aws_dynamodb_client.BotoAuthError:
            raise
        except aws_dynamodb_client.TableDoesNotExist:
            raise
        except aws_dynamodb_client.InvalidPutItemMethodParameter:
            raise
        except aws_dynamodb_client.PrimaryKeyConstraintError:
            raise
        except aws_dynamodb_client.EndpointConnectionError:
            raise
        # response like:
        # {'ResponseMetadata': {
        #     'RequestId': 'AEMBQ9DAB9PGQ6KNQAUDK5DFKNVV4KQNSO5AEMVJF66Q9ASUAAJG',
        #     'HTTPStatusCode': 200,
        #     'HTTPHeaders': {'connection': 'keep-alive', 'content-length': '2',
        #                     'content-type': 'application/x-amz-json-1.0',
        #                     'date': 'Sat, 01 Nov 2025 13:55:40 GMT', 'server': 'Server',
        #                     'x-amz-crc32': '2745614147',
        #                     'x-amzn-requestid': 'AEMBQ9DAB9PGQ6KNQAUDK5DFKNVV4KQNSO5AEMVJF66Q9ASUAAJG'},
        #     'RetryAttempts': 0}}
        return response
