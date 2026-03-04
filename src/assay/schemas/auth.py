import uuid

from pydantic import BaseModel, Field


class SignupRequest(BaseModel):
    email: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(max_length=128)


class SignupResponse(BaseModel):
    agent_id: uuid.UUID
    display_name: str


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    agent_id: uuid.UUID
    display_name: str
