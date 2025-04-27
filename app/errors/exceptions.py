from fastapi import HTTPException, status


class BaseHTTPException(HTTPException):
    def __init__(self, status_code: int, detail=str, headers: dict | None = None):
        super().__init__(status_code, detail, headers)


class ClientError(BaseHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Bad request"

    def __init__(self, detail: str | None = None):
        super().__init__(status_code=self.status_code, detail=detail or self.detail)


class UnauthorizedError(ClientError):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Not authorized"


class AuthenticationError(UnauthorizedError):
    detail = "Authentication failed"


class InvalidCredentialsError(AuthenticationError):
    detail = "Invalid credentials"


class TokenError(UnauthorizedError):
    detail = "Token error"


class TokenNotFoundError(TokenError):
    detail = "Token not found"


class InvalidTokenError(TokenError):
    detail = "Invalid token"


class TokenExpiredError(TokenError):
    detail = "Token expired"


class RefreshTokenExpiredError(TokenExpiredError):
    detail = "Refresh token expired"


class AccessTokenExpiredError(TokenExpiredError):
    detail = "Access token expired"


class ForbiddenError(ClientError):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Operation forbidden"


class PermissionDeniedError(ForbiddenError):
    detail = "Permission denied"


class InactiveUserError(ForbiddenError):
    detail = "Inactive user account"


class NotFoundError(ClientError):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Resource not found"


class UserNotFoundError(NotFoundError):
    detail = "User not found"


class ConflictError(ClientError):
    status_code = status.HTTP_409_CONFLICT
    detail = "Conflict occurred"


class UserAlreadyExistsError(ConflictError):
    detail = "User already exists"


class ValidationError(ClientError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Validation error"


class ServerError(BaseHTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Internal server error"

    def __init__(self, detail: str | None = None):
        super().__init__(status_code=self.status_code, detail=detail or self.detail)


class DatabaseError(ServerError):
    detail = "Database operation failed"
