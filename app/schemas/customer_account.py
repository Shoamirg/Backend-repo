from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class CustomerAccountCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=10, max_length=72, repr=False)
    @field_validator('password')
    @classmethod
    def password_bytes(cls, value):
        if len(value.encode('utf-8')) > 72:
            raise ValueError('Password exceeds 72 UTF-8 bytes')
        return value


class CustomerAccountUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    is_active: bool


class CustomerPasswordLogin(BaseModel):
    model_config = ConfigDict(extra='forbid')
    email: EmailStr = Field(max_length=255)
    password: str = Field(max_length=72, repr=False)


# ── mobile self-service ────────────────────────────────────────────────────
import uuid as _uuid
from typing import Optional

_PHONE = Field(pattern=r"^\+?[0-9\s\-()]{7,20}$")
_CODE = Field(pattern=r"^[0-9]{6}$")


def _password_field():
    return Field(min_length=10, max_length=72, repr=False)


class _NewPassword(BaseModel):
    @field_validator('password', 'new_password', check_fields=False)
    @classmethod
    def password_bytes(cls, value):
        if len(value.encode('utf-8')) > 72:
            raise ValueError('Password exceeds 72 UTF-8 bytes')
        return value


class SignupStart(BaseModel):
    model_config = ConfigDict(extra='forbid')
    email: EmailStr = Field(max_length=255)
    phone: str = _PHONE


class SignupComplete(_NewPassword):
    model_config = ConfigDict(extra='forbid')
    email: EmailStr = Field(max_length=255)
    phone: str = _PHONE
    code: str = _CODE
    password: str = _password_field()
    service_center_id: Optional[_uuid.UUID] = None


class PasswordResetStart(BaseModel):
    model_config = ConfigDict(extra='forbid')
    email: EmailStr = Field(max_length=255)


class PasswordResetComplete(_NewPassword):
    model_config = ConfigDict(extra='forbid')
    email: EmailStr = Field(max_length=255)
    code: str = _CODE
    new_password: str = _password_field()


class PasswordChange(_NewPassword):
    model_config = ConfigDict(extra='forbid')
    current_password: str = Field(max_length=72, repr=False)
    new_password: str = _password_field()


class AccountDelete(BaseModel):
    model_config = ConfigDict(extra='forbid')
    password: Optional[str] = Field(default=None, max_length=72, repr=False)


class CodeSent(BaseModel):
    detail: str = "If the details match, a code has been sent by SMS."
    expires_in: int
