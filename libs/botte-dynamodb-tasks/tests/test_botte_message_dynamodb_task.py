import json
from datetime import datetime, timezone

import pytest
from aws_utils.aws_testfactories.dynamodb_event_to_lambda_factory import (
    DynamodbEventToLambdaFactory,
)
from ksuid import KsuidMs

import botte_dynamodb_tasks


class TestBotteMessageDynamodbTask:
    def setup_method(self):
        self.text = "Hello world from (botte-monorepo) botte-dynamodb-tasks pytests!"
        self.sender_app = "BOTTE_DYNAMODB_TASKS_PYTEST"
        self.ksuid = KsuidMs()
        self.expiration_ts = round(
            datetime(2023, 11, 12, 11, 46, tzinfo=timezone.utc).timestamp()
        )

    def test_to_dict_and_json(self):
        task = botte_dynamodb_tasks.BotteMessageDynamodbTask(
            text=self.text,
            sender_app=self.sender_app,
            ksuid=self.ksuid,
            expiration_ts=self.expiration_ts,
        )
        assert task.to_dict() == {
            "PK": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID + f"#{self.ksuid}",
            "SK": str(self.ksuid),
            "TaskId": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID,
            "SenderApp": self.sender_app,
            "Payload": {
                "text": self.text,
            },
            "ExpirationTs": self.expiration_ts,
        }
        assert task.to_json() == json.dumps(
            {
                "PK": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID + f"#{self.ksuid}",
                "SK": str(self.ksuid),
                "TaskId": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID,
                "SenderApp": self.sender_app,
                "Payload": {
                    "text": self.text,
                },
                "ExpirationTs": self.expiration_ts,
            },
            sort_keys=True,
        )

    def test_to_dict_and_json_fifo(self):
        task = botte_dynamodb_tasks.BotteMessageDynamodbTask(
            text=self.text,
            sender_app=self.sender_app,
            do_process_task_fifo=True,
            ksuid=self.ksuid,
            expiration_ts=self.expiration_ts,
        )
        assert task.to_dict() == {
            "PK": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID,
            "SK": str(self.ksuid),
            "TaskId": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID,
            "SenderApp": self.sender_app,
            "Payload": {
                "text": self.text,
            },
            "ExpirationTs": self.expiration_ts,
        }
        assert task.to_json() == json.dumps(
            {
                "PK": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID,
                "SK": str(self.ksuid),
                "TaskId": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID,
                "SenderApp": self.sender_app,
                "Payload": {
                    "text": self.text,
                },
                "ExpirationTs": self.expiration_ts,
            },
            sort_keys=True,
        )

    def test_to_dict_and_json_fifo_group_id(self):
        task = botte_dynamodb_tasks.BotteMessageDynamodbTask(
            text=self.text,
            sender_app=self.sender_app,
            do_process_task_fifo=True,
            fifo_group_id="G1",
            ksuid=self.ksuid,
            expiration_ts=self.expiration_ts,
        )
        assert task.to_dict() == {
            "PK": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID + "#G1",
            "SK": str(self.ksuid),
            "TaskId": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID,
            "SenderApp": self.sender_app,
            "Payload": {
                "text": self.text,
            },
            "ExpirationTs": self.expiration_ts,
        }
        assert task.to_json() == json.dumps(
            {
                "PK": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID + "#G1",
                "SK": str(self.ksuid),
                "TaskId": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID,
                "SenderApp": self.sender_app,
                "Payload": {
                    "text": self.text,
                },
                "ExpirationTs": self.expiration_ts,
            },
            sort_keys=True,
        )

    def test_yield_from_event(self):
        new_image = {
            "PK": {"S": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID + f"#{self.ksuid}"},
            "SK": {"S": str(self.ksuid)},
            "TaskId": {"S": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID},
            "SenderApp": {"S": self.sender_app},
            "Payload": {
                "M": {
                    "text": {"S": self.text},
                }
            },
            "ExpirationTs": {"N": self.expiration_ts},
        }
        event = DynamodbEventToLambdaFactory.make_for_insert(new_image=new_image)
        for task in botte_dynamodb_tasks.BotteMessageDynamodbTask.yield_from_event(
            event
        ):
            assert task.text == self.text
            assert task.sender_app == self.sender_app
            assert task.ksuid == self.ksuid
            assert task.expiration_ts == self.expiration_ts

    def test_yield_from_event_fifo(self):
        new_image = {
            "PK": {"S": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID},
            "SK": {"S": str(self.ksuid)},
            "TaskId": {"S": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID},
            "SenderApp": {"S": self.sender_app},
            "Payload": {
                "M": {
                    "text": {"S": self.text},
                }
            },
            "ExpirationTs": {"N": self.expiration_ts},
        }
        event = DynamodbEventToLambdaFactory.make_for_insert(new_image=new_image)
        for task in botte_dynamodb_tasks.BotteMessageDynamodbTask.yield_from_event(
            event
        ):
            assert task.text == self.text
            assert task.sender_app == self.sender_app
            assert task.ksuid == self.ksuid
            assert task.expiration_ts == self.expiration_ts

    def test_yield_from_event_fifo_group_id(self):
        new_image = {
            "PK": {"S": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID + "#G1"},
            "SK": {"S": str(self.ksuid)},
            "TaskId": {"S": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID},
            "SenderApp": {"S": self.sender_app},
            "Payload": {
                "M": {
                    "text": {"S": self.text},
                }
            },
            "ExpirationTs": {"N": self.expiration_ts},
        }
        event = DynamodbEventToLambdaFactory.make_for_insert(new_image=new_image)
        for task in botte_dynamodb_tasks.BotteMessageDynamodbTask.yield_from_event(
            event
        ):
            assert task.text == self.text
            assert task.sender_app == self.sender_app
            assert task.ksuid == self.ksuid
            assert task.expiration_ts == self.expiration_ts

    def test_yield_from_event_invalid_pk(self):
        new_image = {
            "PK": {"S": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID + "XXX"},
            "SK": {"S": str(self.ksuid)},
            "TaskId": {"S": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID},
            "SenderApp": {"S": self.sender_app},
            "Payload": {
                "M": {
                    "text": {"S": self.text},
                }
            },
            "ExpirationTs": {"N": self.expiration_ts},
        }
        event = DynamodbEventToLambdaFactory.make_for_insert(new_image=new_image)
        with pytest.raises(botte_dynamodb_tasks.ValidationError) as exc:
            list(botte_dynamodb_tasks.BotteMessageDynamodbTask.yield_from_event(event))
        assert "Invalid PK" in str(exc)

    def test_yield_from_event_no_pk(self):
        new_image = {
            # "PK": {"S": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID + "XXX"},
            "SK": {"S": str(self.ksuid)},
            "TaskId": {"S": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID},
            "SenderApp": {"S": self.sender_app},
            "Payload": {
                "M": {
                    "text": {"S": self.text},
                }
            },
            "ExpirationTs": {"N": self.expiration_ts},
        }
        event = DynamodbEventToLambdaFactory.make_for_insert(new_image=new_image)
        with pytest.raises(botte_dynamodb_tasks.ValidationError) as exc:
            list(botte_dynamodb_tasks.BotteMessageDynamodbTask.yield_from_event(event))
        assert "Invalid PK" in str(exc)

    def test_yield_from_event_invalid_sk(self):
        new_image = {
            "PK": {"S": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID + f"#{self.ksuid}"},
            "SK": {"S": str(self.ksuid) + "XXX"},
            "TaskId": {"S": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID},
            "SenderApp": {"S": self.sender_app},
            "Payload": {
                "M": {
                    "text": {"S": self.text},
                }
            },
            "ExpirationTs": {"N": self.expiration_ts},
        }
        event = DynamodbEventToLambdaFactory.make_for_insert(new_image=new_image)
        with pytest.raises(botte_dynamodb_tasks.ValidationError) as exc:
            list(botte_dynamodb_tasks.BotteMessageDynamodbTask.yield_from_event(event))
        assert "SK must be KsuidMs" in str(exc)

    def test_yield_from_event_no_sk(self):
        new_image = {
            "PK": {"S": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID + f"#{self.ksuid}"},
            # "SK": {"S": str(self.ksuid) + "XXX"},
            "TaskId": {"S": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID},
            "SenderApp": {"S": self.sender_app},
            "Payload": {
                "M": {
                    "text": {"S": self.text},
                }
            },
            "ExpirationTs": {"N": self.expiration_ts},
        }
        event = DynamodbEventToLambdaFactory.make_for_insert(new_image=new_image)
        with pytest.raises(botte_dynamodb_tasks.ValidationError) as exc:
            list(botte_dynamodb_tasks.BotteMessageDynamodbTask.yield_from_event(event))
        assert "SK must be KsuidMs" in str(exc)

    def test_yield_from_event_invalid_task_id(self):
        new_image = {
            "PK": {"S": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID + f"#{self.ksuid}"},
            "SK": {"S": str(self.ksuid)},
            "TaskId": {"S": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID + "XXX"},
            "SenderApp": {"S": self.sender_app},
            "Payload": {
                "M": {
                    "text": {"S": self.text},
                }
            },
            "ExpirationTs": {"N": self.expiration_ts},
        }
        event = DynamodbEventToLambdaFactory.make_for_insert(new_image=new_image)
        with pytest.raises(botte_dynamodb_tasks.ValidationError) as exc:
            list(botte_dynamodb_tasks.BotteMessageDynamodbTask.yield_from_event(event))
        assert "Invalid TaskId" in str(exc)

    def test_yield_from_event_no_task_id(self):
        new_image = {
            "PK": {"S": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID + f"#{self.ksuid}"},
            "SK": {"S": str(self.ksuid)},
            "TaskIdXXX": {"S": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID},
            "SenderApp": {"S": self.sender_app},
            "Payload": {
                "M": {
                    "text": {"S": self.text},
                }
            },
            "ExpirationTs": {"N": self.expiration_ts},
        }
        event = DynamodbEventToLambdaFactory.make_for_insert(new_image=new_image)
        with pytest.raises(botte_dynamodb_tasks.ValidationError) as exc:
            list(botte_dynamodb_tasks.BotteMessageDynamodbTask.yield_from_event(event))
        assert "Invalid TaskId" in str(exc)

    def test_yield_from_event_no_sender_app(self):
        new_image = {
            "PK": {"S": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID + f"#{self.ksuid}"},
            "SK": {"S": str(self.ksuid)},
            "TaskId": {"S": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID},
            "SenderAppXXX": {"S": self.sender_app},
            "Payload": {
                "M": {
                    "text": {"S": self.text},
                }
            },
            "ExpirationTs": {"N": self.expiration_ts},
        }
        event = DynamodbEventToLambdaFactory.make_for_insert(new_image=new_image)
        with pytest.raises(botte_dynamodb_tasks.ValidationError) as exc:
            list(botte_dynamodb_tasks.BotteMessageDynamodbTask.yield_from_event(event))
        assert "Invalid SenderApp" in str(exc)

    def test_yield_from_event_no_payload(self):
        new_image = {
            "PK": {"S": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID + f"#{self.ksuid}"},
            "SK": {"S": str(self.ksuid)},
            "TaskId": {"S": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID},
            "SenderApp": {"S": self.sender_app},
            "PayloadXXX": {
                "M": {
                    "text": {"S": self.text},
                }
            },
            "ExpirationTs": {"N": self.expiration_ts},
        }
        event = DynamodbEventToLambdaFactory.make_for_insert(new_image=new_image)
        with pytest.raises(botte_dynamodb_tasks.ValidationError) as exc:
            list(botte_dynamodb_tasks.BotteMessageDynamodbTask.yield_from_event(event))
        assert "Invalid Payload" in str(exc)

    def test_yield_from_event_no_payload_text(self):
        new_image = {
            "PK": {"S": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID + f"#{self.ksuid}"},
            "SK": {"S": str(self.ksuid)},
            "TaskId": {"S": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID},
            "SenderApp": {"S": self.sender_app},
            "Payload": {
                "M": {
                    "textXXX": {"S": self.text},
                }
            },
            "ExpirationTs": {"N": self.expiration_ts},
        }
        event = DynamodbEventToLambdaFactory.make_for_insert(new_image=new_image)
        with pytest.raises(botte_dynamodb_tasks.ValidationError) as exc:
            list(botte_dynamodb_tasks.BotteMessageDynamodbTask.yield_from_event(event))
        assert "Invalid text" in str(exc)

    def test_yield_from_event_invalid_expiration_ts(self):
        new_image = {
            "PK": {"S": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID + f"#{self.ksuid}"},
            "SK": {"S": str(self.ksuid)},
            "TaskId": {"S": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID},
            "SenderApp": {"S": self.sender_app},
            "Payload": {
                "M": {
                    "text": {"S": self.text},
                }
            },
            "ExpirationTs": {"N": "XXX"},
        }
        event = DynamodbEventToLambdaFactory.make_for_insert(new_image=new_image)
        with pytest.raises(botte_dynamodb_tasks.ValidationError) as exc:
            list(botte_dynamodb_tasks.BotteMessageDynamodbTask.yield_from_event(event))
        assert "Invalid format for ExpirationTs" in str(exc)

    def test_yield_from_event_no_expiration_ts(self):
        new_image = {
            "PK": {"S": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID + f"#{self.ksuid}"},
            "SK": {"S": str(self.ksuid)},
            "TaskId": {"S": botte_dynamodb_tasks.BOTTE_MESSAGE_TASK_ID},
            "SenderApp": {"S": self.sender_app},
            "Payload": {
                "M": {
                    "text": {"S": self.text},
                }
            },
            "ExpirationTsXXX": {"N": self.expiration_ts},
        }
        event = DynamodbEventToLambdaFactory.make_for_insert(new_image=new_image)
        with pytest.raises(botte_dynamodb_tasks.ValidationError) as exc:
            list(botte_dynamodb_tasks.BotteMessageDynamodbTask.yield_from_event(event))
        assert "Invalid format for ExpirationTs" in str(exc)
