from typing import Any

from flask_sqlalchemy.model import Model


class DbModelValidationException(Exception):
    """
    The db model validation has an error.
    """

    def __init__(self, message: str):
        super().__init__(message)


class UserAlreadyExistingException(Exception):
    """
    The user is already existing in the database
    """

    def __init__(self):
        message = "User already existing."
        super().__init__(message)


class DbModelAlreadyExistingException(Exception):
    """
    When the db model is already existing
    """

    def __init__(self, model: Any, data: dict):
        message = f"Model {model.__name__} already existing with the data {str(data)}"  # noqa
        super().__init__(message)


class DbModelNotFoundException(Exception):
    """
    The db model was not found in database.
    """

    def __init__(self, *, model: Model, id: Any):
        err_msg = f"Object {model.__name__} with id = {id} doesn't exist."
        super().__init__(err_msg)


class DbModelFieldLengthException(DbModelValidationException):
    """
    The db model field is to short or to long
    """

    def __init__(self, message: str):
        super().__init__(message)


class DbModelFieldRequieredException(DbModelValidationException):
    """
    The db model field is required, but was null
    """

    def __init__(self, fieldname: str):
        message = f"The field '{fieldname}' is required but was null."
        super().__init__(message)


class DbModelFieldEmailInvalidException(DbModelValidationException):
    """
    The db model field email was invalid
    """

    def __init__(self, message: str):
        super().__init__(message)


class DbModelFieldTypeError(DbModelValidationException):
    """
    The db model field was invalid like
        -  int expected, was float
        -  int expected, was string ...
    """

    def __init__(self, fieldname: str, value: Any, expected_types: list[type]):
        expected_types = ", ".join([
            expected_type.__name__ for expected_type in expected_types])
        message = f"Field '{fieldname}'={value} was type of {type(value)} " \
                  + f", but expected types: '{expected_types}'"
        super().__init__(message)


class DbModelFieldValueError(DbModelValidationException):
    """
    The db model field was invalid like
        -  int expected, was float
        -  int expected, was string ...
    """

    def __init__(self, message: str):
        super().__init__(message)


class InvalidLoginCredentialsException(Exception):
    """
    When the email, username or passoword are invalid
    """

    def __init__(self):
        message = "User credentials are invalid."
        super().__init__(message)


class DbModelSerializationException(DbModelValidationException):
    """
    When parameter mapping not working because of an unexpected attribute.
    """

    def __init__(self, message: str):
        super().__init__(message)


class DbModelUnqiueConstraintException(DbModelValidationException):
    """
    When a column with a given value is already existing.
    """

    def __init__(
            self,
            *,
            filedname: str = None,
            value: Any = None,
            msg: str = None
    ) -> None:
        err_msg = msg if msg else f"Field '{filedname}' with value '{str(value)}' is already existing."  # noqa
        super().__init__(err_msg)


class PaginationException(DbModelValidationException):
    """
    When page input from user is invalid.
    """

    def __init__(self, err_msg) -> None:
        super().__init__(err_msg)


class PaginationPageException(PaginationException):
    """
    When page input from user is invalid.
    """

    def __init__(self, value: int) -> None:
        err_msg = f"The given page for pagination is invalid ({value})"  # noqa
        super().__init__(err_msg)


class PaginationPageSizeException(PaginationException):
    """
    When page size input from user is invalid.
    """

    def __init__(self, value: int) -> None:
        err_msg = f"The given page size for pagination is invalid ({value})"  # noqa
        super().__init__(err_msg)


class ValueErrorGeneral(Exception):
    """
    Custom ValueError implementation
    """

    def __init__(self, err_msg: str) -> None:
        super().__init__(err_msg)


class ImageNotGivenException(Exception):
    """
    When no image with specific name in request.files
    """

    def __init__(self, image_request_filekey: str) -> None:
        err_msg = f"When uploading an image, the content for key '{image_request_filekey}' is required."  # noqa
        super().__init__(err_msg)


class ImageNotAllowedFileExtensionException(Exception):
    """
    When file extension is not allowed.
    """

    def __init__(
            self,
            file_extension: str,
            allowed_file_extensions: list
    ) -> None:
        err_msg = f"The file extension '{file_extension}' is not allowed. Use {str(allowed_file_extensions)}."  # noqa
        super().__init__(err_msg)


class ImageNotFoundException(Exception):
    """
    When image was not found.
    """

    def __init__(self, id) -> None:
        err_msg = f"Image with id '{id}' was not found."
        super().__init__(err_msg)


class ForeignkeyNotFoundException(DbModelValidationException):
    """
    When foreignkey was not found.
    """

    def __init__(self, msg) -> None:
        super().__init__(msg)


class ReadOnlyFieldInPayloadException(DbModelValidationException):
    """
    When foreignkey was not found.
    """

    def __init__(self, fieldname) -> None:
        err_msg = f"The field '{fieldname}' is read only. Please remove this field from payload."  # noqa
        super().__init__(err_msg)


class AuthorizationException(Exception):
    """
    When foreignkey was not found.
    """

    def __init__(self, err_msg: str) -> None:
        super().__init__(err_msg)


class UserApplicationConfigurationException(Exception):
    """
    The db model validation has an error.
    """

    def __init__(self, message: str):
        super().__init__(message)
