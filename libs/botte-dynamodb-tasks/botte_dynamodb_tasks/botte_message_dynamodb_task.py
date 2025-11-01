"""
** BOTTE DYNAMODB TASKS **
==========================

Used by [botte-dynamodb-client](../public-clients/botte-dynamodb-client), with [aws-dynamodb-client](https://github.com/puntonim/clients-monorepo/tree/main/aws-dynamodb-client),
 to interact with Botte via its DynamoDB interface.

Botte has a DynamoDb interface meant to be used by consumers that:
 - are running in AWS infra, in the same AWS account as Botte (otherwise they would use [botte-http-client](../botte-http-client))
 - but cannot invoke Botte Lambdas directly, fi. they are in a VPC with no connection to
    other AWS services nor Internet access (otherwise they would use [botte-lambda-client](../botte-lambda-client))

Note: one of my patterns is to have Lambdas that connect to a SQLite database stored
 on EFS. EFS requires a VPC, and the Lambda to be in the same VPC. But, for VPCs,
 connection to the Internet and other AWS services requires expensive things like
 internet gateway, NAT or PrivateLink. But VPCs can connect to DynamoDB and S3 (only
 these 2 services) via a VPC Gateway Endpoint for free. So in the end: a Lambda in
 a VPC can connect to Botte DynamoDB interface by using a free VPC Gateway Endpoint
 and this Botte DynamoDB client.

This lib provides means to create and parse tasks to be read and written to Botte
 DynamoDB task queue.

```py
import json
from datetime import datetime, timezone
import pytest
from ksuid import KsuidMs
import botte_dynamodb_tasks

text = "Hello world from (botte-monorepo) botte-dynamodb-tasks pytests!"
sender_app = "BOTTE_DYNAMODB_TASKS_PYTEST"
ksuid = KsuidMs()
expiration_ts = round(
    datetime(2023, 11, 12, 11, 46, tzinfo=timezone.utc).timestamp()
)

task = botte_dynamodb_tasks.BotteMessageDynamodbTask(
    text=text,
    sender_app=sender_app,
    ksuid=ksuid,
    expiration_ts=expiration_ts,
)
assert task.to_dict() == {
    "PK": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID,
    "SK": str(ksuid),
    "TaskId": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID,
    "SenderApp": sender_app,
    "Payload": {
        "text": text,
    },
    "ExpirationTs": expiration_ts,
}
assert task.to_json() == json.dumps(
    {
        "PK": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID,
        "SK": str(ksuid),
        "TaskId": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID,
        "SenderApp": sender_app,
        "Payload": {
            "text": text,
        },
        "ExpirationTs": expiration_ts,
    },
    sort_keys=True,
)
```
"""

import json
from datetime import timedelta, timezone
from functools import lru_cache
from typing import Any

import datetime_utils
from boto3.dynamodb.types import TypeDeserializer
from ksuid import KsuidMs

from . import exceptions

__all__ = [
    "BotteMessageDynamodbTask",
    "BOTTE_MESSAGE_TASK_ID",
]

BOTTE_MESSAGE_TASK_ID = "BOTTE_MESSAGE"


class BotteMessageDynamodbTask:
    def __init__(
        self,
        text: str,
        sender_app: str,
        # Eg. str(KsuidMs()) -> '2XfZrNMydhTvwyWlHdzJPdz3wuA'.
        #  And: KsuidMs.from_base62('2XfZrNMydhTvwyWlHdzJPdz3wuA').
        ksuid: KsuidMs | None = None,
        expiration_ts: int | None = None,
    ):
        self.text = text
        self.sender_app = sender_app
        if not ksuid:
            # Unique ID (like UUID), but with a timestamp info in it, and
            #  alphabetically sortable by timestamp.
            # Eg. str(KsuidMs()) -> '2XfZrNMydhTvwyWlHdzJPdz3wuA'.
            #  And: KsuidMs.from_base62('2XfZrNMydhTvwyWlHdzJPdz3wuA').
            ksuid = KsuidMs()
        self.ksuid = ksuid
        # Mind that ExpirationTs is configured as automatic TTL in the DynamoDB Table.
        # Note that the deletion happens eventually, within 2 days.
        if not expiration_ts:
            # It's Unix epoch time format in seconds (UTC of course).
            ksuid_date = ksuid.datetime.astimezone(timezone.utc)
            expiration_ts = round((ksuid_date + timedelta(hours=1)).timestamp())
        self.expiration_ts = expiration_ts

    def to_dict(self) -> dict:
        """
        Used by consumers to build the DynamoDB Item to INSERT.

        Using dynamodb-client lib (which uses Boto3 lib) this dict is converted
         to this JSON:
            {
                "PK": {
                    "S": "BOTTE_MESSAGE"
                },
                "SK": {
                    "S": "34sVCw69dftbK1MSWtRkv6T8vGp"
                },
                "ExpirationTs": {
                    "N": "1762002142"
                },
                "Payload": {
                    "M": {
                        "text": {
                            "S": "Hello world!"
                        }
                    }
                },
                "SenderApp": {
                    "S": "BOTTE_DYNAMODB_CLIENT_PYTESTS"
                },
                "TaskId": {
                    "S": "BOTTE_MESSAGE"
                }
            }
        """
        data = {
            "PK": BOTTE_MESSAGE_TASK_ID,
            "SK": None,  # Used for sorting and de-duplicating.
            "TaskId": BOTTE_MESSAGE_TASK_ID,
            "SenderApp": self.sender_app,
            "Payload": {
                "text": self.text,
            },
            "ExpirationTs": self.expiration_ts,  # It's the TTL.
        }

        # Validation.
        if not isinstance(self.text, str):
            raise exceptions.ValidationError(f"text must be string: {self.text}")

        if not isinstance(self.sender_app, str):
            raise exceptions.ValidationError(
                f"SenderApp must be string: {self.sender_app}"
            )

        if not isinstance(self.ksuid, KsuidMs):
            raise exceptions.ValidationError(f"ksuid must be KsuidMs: {self.ksuid}")
        data["SK"] = str(self.ksuid)

        try:
            datetime_utils.timestamp_to_utc_datetime(self.expiration_ts)
        except Exception as exc:
            raise exceptions.ValidationError(
                f"ExpirationTs must be int timestamp: {self.expiration_ts}"
            ) from exc

        return data

    @lru_cache  # noqa: B019
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)

    @staticmethod
    def _make_from_record(record: dict) -> "BotteMessageDynamodbTask":
        """
        Record format:
            {
                "eventID": "ff29711457aeb0372bc2a89d8edd7098",
                "eventName": "INSERT",
                "eventVersion": "1.1",
                "eventSource": "aws:dynamodb",
                "awsRegion": "eu-south-1",
                "dynamodb": {
                    "ApproximateCreationDateTime": 1698673253,
                    "Keys": {
                        "TaskId": {
                            "S": "BOTTE_MESSAGE"
                        },
                        "Text": {
                            "S": "2023-10-29T13:22:56.252653+00:00#Hello world from Dynamo!!"
                        }
                    },
                    "NewImage": {
                        "TaskId": {
                            "S": "BOTTE_MESSAGE"
                        },
                        "ExpirationTs": {
                            "N": "1698672903"
                        },
                        "Text": {
                            "S": "2023-10-29T13:22:56.252653+00:00#Hello world from Dynamo!!"
                        }
                    },
                    "SequenceNumber": "45400000000013380201987",
                    "SizeBytes": 180,
                    "StreamViewType": "NEW_IMAGE"
                },
                "eventSourceARN": "arn:aws:dynamodb:eu-south-1:477353422995:table/patatrack-botte-message-db-queue-production/stream/2023-10-30T13:38:23.986"
            }
        """
        # TODO update docstring after inspecting the endpoint.

        event_name = record.get("eventName")
        if event_name != "INSERT":
            raise exceptions.ValidationError(
                f"Not an INSERT DynamoDB stream event: {event_name}"
            )

        new_image: dict = record.get("dynamodb", {}).get("NewImage", {})
        if not new_image:
            raise exceptions.ValidationError(
                f"dynamodb > NewImage missing in record: {record}"
            )

        pk = _deserialize(new_image.get("PK"))
        sk = _deserialize(new_image.get("SK"))
        task_id = _deserialize(new_image.get("TaskId"))
        sender_app = _deserialize(new_image.get("SenderApp"))
        payload = _deserialize(new_image.get("Payload"))
        # Mind that ExpirationTs is configured as automatic TTL.
        expiration_ts = _deserialize(new_image.get("ExpirationTs"))

        # Validation.
        if pk != BOTTE_MESSAGE_TASK_ID:
            raise exceptions.ValidationError(f"Invalid PK: {pk}")

        try:
            # Unfortunately it seems to never raise even for invalid strings like "XXX".
            ksuid = KsuidMs.from_base62(sk)
        except Exception as exc:
            raise exceptions.ValidationError(f"SK must be KsuidMs: {sk}") from exc

        # Unfortunately KsuidMs.from_base62() seems to never raise even for invalid
        #  strings like "XXX", so we check the timestamp.
        if (
            not datetime_utils.timestamp_to_utc_datetime(int(ksuid.timestamp)).year
            >= datetime_utils.now().year - 1
        ):
            raise exceptions.ValidationError(f"SK must be KsuidMs: {sk}")

        if task_id != BOTTE_MESSAGE_TASK_ID:
            raise exceptions.ValidationError(f"Invalid TaskId: {task_id}")

        if not sender_app:
            raise exceptions.ValidationError(f"Invalid SenderApp: {sender_app}")
        elif not isinstance(sender_app, str):
            raise exceptions.ValidationError(f"SenderApp must be string: {sender_app}")

        if not payload:
            raise exceptions.ValidationError(f"Invalid Payload: {payload}")
        elif not isinstance(payload, dict):
            raise exceptions.ValidationError(f"Payload must be dict: {payload}")
        text = payload.get("text")
        if not text:
            raise exceptions.ValidationError(f"Invalid text: {text}")
        elif not isinstance(text, str):
            raise exceptions.ValidationError(f"text must be string: {text}")

        try:
            datetime_utils.timestamp_to_utc_datetime(int(expiration_ts))
        except Exception as exc:
            raise exceptions.ValidationError(
                f"Invalid format for ExpirationTs: {expiration_ts}"
            ) from exc

        return BotteMessageDynamodbTask(
            text=text,
            sender_app=sender_app,
            ksuid=ksuid,
            expiration_ts=expiration_ts,
        )

    @staticmethod
    def yield_from_event(event: dict[str, Any]):
        records = event.get("Records")
        if records is None:
            raise exceptions.ValidationError(
                'Malformed DynamoDB stream: no ["Records"]'
            )

        for record in records:
            try:
                yield BotteMessageDynamodbTask._make_from_record(record)
            except exceptions.ValidationError:
                raise


def _deserialize(data: dict[str, Any]):
    """
    Deserialize a dict read from DynamoDB.

    See: https://boto3.amazonaws.com/v1/documentation/api/latest/_modules/boto3/dynamodb/types.html
    """
    if not data:
        return None
    return TypeDeserializer().deserialize(data)
