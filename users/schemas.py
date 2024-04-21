from pydantic import BaseModel, EmailStr, ValidationError, validator


class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str
    password_confirmation: str

    @validator('password_confirmation')
    def validate_password_match(cls, value, values):
        if 'password' in values and value != values['password']:
            raise ValidationError("Passwords do not match")
        return value

