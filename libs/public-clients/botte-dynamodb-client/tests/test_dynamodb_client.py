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
            # do_send_msg_fifo=False,
            # fifo_group_id=None,
            botte_message_dynamodb_task_extra_kwargs=dict(
                ksuid=KsuidMs.from_base62("34sbgpYvCbhsUZtNvB8OVmsxsAp"),
                expiration_ts=1920997986,  # Fri Nov 15 2030 18:33:06 GMT+0000.
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

    def test_fifo(self):
        client = botte_dynamodb_client.BotteDynamodbClient()
        response = client.send_message(
            self.text + " 1",
            sender_app="BOTTE_DYNAMODB_CLIENT_PYTESTS",
            do_send_msg_fifo=True,
            # fifo_group_id="G1",
            botte_message_dynamodb_task_extra_kwargs=dict(
                ksuid=KsuidMs.from_base62("35Wofqz8ljZroJ4IRISglJsgVGU"),
                expiration_ts=1920997986,  # Fri Nov 15 2030 18:33:06 GMT+0000.
            ),
        )
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
        response = client.send_message(
            self.text + " 2",
            sender_app="BOTTE_DYNAMODB_CLIENT_PYTESTS",
            do_send_msg_fifo=True,
            # fifo_group_id="G1",
            botte_message_dynamodb_task_extra_kwargs=dict(
                ksuid=KsuidMs.from_base62("35WokQlCqt4EllOWBQuBgFUFzIF"),
                expiration_ts=1920997986,  # Fri Nov 15 2030 18:33:06 GMT+0000.
            ),
        )
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
        response = client.send_message(
            self.text + " 3",
            sender_app="BOTTE_DYNAMODB_CLIENT_PYTESTS",
            do_send_msg_fifo=True,
            # fifo_group_id="G1",
            botte_message_dynamodb_task_extra_kwargs=dict(
                ksuid=KsuidMs.from_base62("35WonzE72dgS9YzkpEpLcI0jNqm"),
                expiration_ts=1920997986,  # Fri Nov 15 2030 18:33:06 GMT+0000.
            ),
        )
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

    def test_fifo_group_id(self):
        client = botte_dynamodb_client.BotteDynamodbClient()
        response = client.send_message(
            self.text + " 1",
            sender_app="BOTTE_DYNAMODB_CLIENT_PYTESTS",
            do_send_msg_fifo=True,
            fifo_group_id="G1",
            botte_message_dynamodb_task_extra_kwargs=dict(
                ksuid=KsuidMs.from_base62("35WpRT8oH6w0TuXrSRtQ1b6EMHt"),
                expiration_ts=1920997986,  # Fri Nov 15 2030 18:33:06 GMT+0000.
            ),
        )
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
        response = client.send_message(
            self.text + " 2",
            sender_app="BOTTE_DYNAMODB_CLIENT_PYTESTS",
            do_send_msg_fifo=True,
            fifo_group_id="G1",
            botte_message_dynamodb_task_extra_kwargs=dict(
                ksuid=KsuidMs.from_base62("35WpSW93GLcViNt278DtgLlQpRq"),
                expiration_ts=1920997986,  # Fri Nov 15 2030 18:33:06 GMT+0000.
            ),
        )
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
        response = client.send_message(
            self.text + " 3",
            sender_app="BOTTE_DYNAMODB_CLIENT_PYTESTS",
            do_send_msg_fifo=True,
            fifo_group_id="G2",
            botte_message_dynamodb_task_extra_kwargs=dict(
                ksuid=KsuidMs.from_base62("35WpTOaQGws2RuckBlQB17ADsnd"),
                expiration_ts=1920997986,  # Fri Nov 15 2030 18:33:06 GMT+0000.
            ),
        )
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
        response = client.send_message(
            self.text + " 4",
            sender_app="BOTTE_DYNAMODB_CLIENT_PYTESTS",
            do_send_msg_fifo=True,
            # fifo_group_id=None,
            botte_message_dynamodb_task_extra_kwargs=dict(
                ksuid=KsuidMs.from_base62("35WpUUMlOPXkwz1LjObF3UnQlr9"),
                expiration_ts=1920997986,  # Fri Nov 15 2030 18:33:06 GMT+0000.
            ),
        )
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

    def test_wrong_table_name(self):
        client = botte_dynamodb_client.BotteDynamodbClient()
        with pytest.raises(aws_dynamodb_client.TableDoesNotExist):
            client.send_message(
                self.text,
                sender_app="BOTTE_DYNAMODB_CLIENT_PYTESTS",
                table_name="XXX",
            )
