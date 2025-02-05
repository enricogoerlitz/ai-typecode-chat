from typing import Union

UNEXPECTED_ERROR_RESULT = (
    {
        "message": "An unexpected error has occored."
    }, 500
)


def bad_request(exp: Union[str, Exception]) -> tuple[dict, int]:
    return {"message": str(exp)}, 400


def unauthorized(exp: Union[str, Exception] = None) -> tuple[dict, int]:
    if exp is None:
        exp = "User is unauthorized for this ressource."
    return {"message": str(exp)}, 401


def forbidden(exp: Union[str, Exception]) -> tuple[dict, int]:
    return {"message": str(exp)}, 403


def not_found(exp: Union[str, Exception]) -> tuple[dict, int]:
    return {"message": str(exp)}, 404


def conflict(exp: Union[str, Exception]) -> tuple[dict, int]:
    return {"message": str(exp)}, 409


def server_error(exp: str | Exception) -> tuple[dict, int]:
    return {"message": str(exp)}, 500


def not_implemented() -> tuple[dict, int]:
    return {"message": "Method not implemented."}, 501


def method_not_allowed() -> tuple[dict, int]:
    err = "Method not allowed."
    return {"message": err}, 405
