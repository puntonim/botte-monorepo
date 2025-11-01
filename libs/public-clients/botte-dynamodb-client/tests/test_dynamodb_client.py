import aws_dynamodb_client
import pytest
from ksuid import KsuidMs

import botte_dynamodb_client


class TestSendMessage:
    def setup_method(self):
        self.text = "Hello world from (botte-monorepo) botte dynamodb client pytests!"

    def test_happy_flow(self):
        client = botte_dynamodb_client.BotteDynamodbClient()
        response = client.send_message(
            self.text,
            sender_app="BOTTE_DYNAMODB_CLIENT_PYTESTS",
            botte_message_dynamodb_task_extra_kwargs=dict(
                ksuid=KsuidMs.from_base62("34sbgpYvCbhsUZtNvB8OVmsxsAp"),
                expiration_ts=1762002142,
            ),
        )
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
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

    def test_wrong_table_name(self):
        client = botte_dynamodb_client.BotteDynamodbClient()
        with pytest.raises(aws_dynamodb_client.TableDoesNotExist):
            client.send_message(
                self.text,
                sender_app="BOTTE_DYNAMODB_CLIENT_PYTESTS",
                table_name="XXX",
            )
