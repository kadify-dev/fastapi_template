from pydantic import BaseModel, ConfigDict


class TokenBase(BaseModel):
    token_type: str = "bearer"

    model_config = ConfigDict(from_attributes=True)


class TokenPair(TokenBase):
    access_token: str
    refresh_token: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class AccessTokenResponse(TokenBase):
    access_token: str
