__all__ = [
    "BaseDynamodbTaskException",
    "ValidationError",
]


class BaseDynamodbTaskException(Exception):
    pass


class ValidationError(BaseDynamodbTaskException):
    pass
