import botte_dynamodb_client


class TestE2eDynamodbMessage:
    """
    Goal: test the DynamoDB task queue interface.
    """

    def setup_method(self):
        self.data = {
            "text": "Hello from (botte-monorepo) botte-be e2e tests for Dynamodb message",
            "sender_app": "E2E_TESTS_IN_BOTTE_BE",  # `sender_app` is optional.
        }

    def test_happy_flow(self):
        client = botte_dynamodb_client.BotteDynamodbClient()
        response = client.send_message(
            text=self.data["text"], sender_app=self.data["sender_app"]
        )
        # response like:
        # {'ResponseMetadata': {
        #     'RequestId': 'E47CEDVP5S6J4TH2M9GI1OV4EFVV4KQNSO5AEMVJF66Q9ASUAAJG',
        #     'HTTPStatusCode': 200,
        #     'HTTPHeaders': {'server': 'Server', 'date': 'Sat, 01 Nov 2025 17:29:00 GMT',
        #                     'content-type': 'application/x-amz-json-1.0',
        #                     'content-length': '2', 'connection': 'keep-alive',
        #                     'x-amzn-requestid': 'E47CEDVP5S6J4TH2M9GI1OV4EFVV4KQNSO5AEMVJF66Q9ASUAAJG',
        #                     'x-amz-crc32': '2745614147'}, 'RetryAttempts': 0}}
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

    # @pytest.mark.skip(
    #     reason="Don't always run this as it causes the sending of an email"
    # )
    # def test_lambda_to_raise_exception_and_email_sent(self, dynamodb_task_table_name):
    #     table = DynamodbTable(dynamodb_task_table_name)
    #     now = datetime_utils.now_utc()
    #     task = BotteMessageDynamodbTask(
    #         text="Hello from Botte tests e2e dynamodb message",
    #         sender_service="BOTTE_E2E_TESTS",
    #         propagation_payload={
    #             "propagation_id": "BOTTE_E2E_TESTS",
    #             "investment_ids": [11, 22],
    #         },
    #         expiration_ts=round(now.timestamp()),
    #     )
    #     item = task.to_dict()
    #     del item["Payload"]
    #     response = table.write(item=item)
    #     assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
