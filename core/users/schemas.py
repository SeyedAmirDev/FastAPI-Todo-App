from pydantic import (
    BaseModel,
    Field,
    field_validator,
)
from fastapi import HTTPException, status


class UserLoginSchema(BaseModel):
    username: str = Field(
        ..., max_length=250, description="username of the user"
    )
    password: str = Field(..., description="password of the user")

    @field_validator("username")
    def validate_username(cls, value: str) -> str:
        if not value.isalnum():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username must contain only letters and digits.",
            )
        return value.lower()


class RefreshTokenSchema(BaseModel):
    refresh_token: str = Field(
        ..., description="refresh token for generate new access token"
    )


class UserRegisterSchema(BaseModel):
    username: str = Field(
        ..., min_length=5, max_length=250, description="username of the user"
    )
    password: str = Field(
        ..., min_length=8, description="password of the user"
    )
    password_confirm: str = Field(
        ..., min_length=8, description="confirm password of the user"
    )

    # @model_validator(mode="after")
    # def verify_passwords_match(self) -> Self:
    #     print(self.password_confirm, self.password)
    #     if self.password != self.password_confirm:
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail="Passwords do not match"
    #         )
    #     return self

    @field_validator("username")
    def validate_username(cls, value: str) -> str:
        if not value.isalnum():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username must contain only letters and digits.",
            )
        return value.lower()

    @field_validator("password_confirm")
    def check_password_match(cls, password_confirm, validation):
        if not (password_confirm == validation.get("password")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password does not match",
            )
        return password_confirm
