from requests import Response


class ValueErrorGeneral(Exception):
    """
    Custom ValueError implementation
    """

    def __init__(self, err_msg: str) -> None:
        super().__init__(err_msg)


class AIClientRateLimitError(Exception):
    def __init__(self, resp: Response):
        err = f"Code: {resp.status_code}, Response: {resp.text}"
        super().__init__(err)


class RequestsException(Exception):
    def __init__(self, resp: Response):
        err = f"Code: {resp.status_code}, Response: {resp.text}"
        super().__init__(err)


class VectorSearchRequestException(RequestsException):
    pass
