from pydantic import BaseModel, ConfigDict


class TokenBase(BaseModel):
    token: str
    model_config = ConfigDict(from_attributes=True)


class AccessToken(TokenBase):
    pass


class RefreshToken(TokenBase):
    pass
