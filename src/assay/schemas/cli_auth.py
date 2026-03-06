import uuid

from pydantic import BaseModel, Field


class CliDeviceStartRequest(BaseModel):
    display_name: str = Field(max_length=128)
    model_slug: str
    runtime_kind: str


class CliDeviceStartResponse(BaseModel):
    device_code: str
    user_code: str
    verification_uri: str
    verification_uri_complete: str
    expires_in: int
    interval: int


class CliDevicePollRequest(BaseModel):
    device_code: str


class CliDeviceApproveRequest(BaseModel):
    user_code: str
    agent_id: uuid.UUID | None = None


class CliDeviceTokenResponse(BaseModel):
    status: str
    agent_id: uuid.UUID
    display_name: str
    model_slug: str
    runtime_kind: str
    access_token: str
    refresh_token: str
    expires_in: int


class CliTokenRefreshRequest(BaseModel):
    refresh_token: str


class CliDeviceApprovalResponse(BaseModel):
    status: str
    agent_id: uuid.UUID
    display_name: str
    model_slug: str
    runtime_kind: str
