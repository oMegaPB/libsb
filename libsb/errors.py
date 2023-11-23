import typing as t

__all__ = [
    "HTTPError",
    "InvalidApiKey",
    "ItemNotFound",
    "IsNotAPet",
    "InvalidArgument",
    "UnknownError",
]

class ApiException(Exception):
    ...

class InvalidArgument(Exception):
    def __init__(self, description: t.Optional[str] = None, *args, **kwargs) -> None:
        self.description = description or "Argument provided is invalid"
        super().__init__(*args, **kwargs)

class HTTPError(ApiException):
    def __init__(self, code: int, description: t.Optional[str] = None, *args) -> None:
        self.code = code
        self.description = description
        super().__init__(description, *args)

class InvalidApiKey(HTTPError):
    def __init__(self, code: int, description: str, *args) -> None:
        self.code = code
        self.description = description
        super().__init__(code=code, description=description, *args)

class ItemNotFound(InvalidArgument):
    def __init__(self, description: t.Optional[str] = None, *args, **kwargs) -> None:
        self.description = description or "Item is not found"
        super().__init__(*args, **kwargs)

class IsNotAPet(InvalidArgument):
    def __init__(self, description: t.Optional[str] = None, *args, **kwargs) -> None:
        self.description = description or "Presented item is not a pet"
        super().__init__(*args, **kwargs)

class UnknownError(Exception):
    ...