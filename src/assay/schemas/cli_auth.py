import uuid

from pydantic import BaseModel, Field, model_validator

from assay.schemas.catalog import CatalogCustomModel


class CliDeviceStartRequest(BaseModel):
    display_name: str = Field(max_length=128)
    model_slug: str | None = None
    custom_model: CatalogCustomModel | None = None
    runtime_kind: str
    provider_terms_acknowledged: bool = False

    @model_validator(mode="after")
    def validate_model_choice(self):
        if (self.model_slug is None) == (self.custom_model is None):
            raise ValueError("Provide exactly one of model_slug or custom_model")
        return self


class CliDeviceStartResponse(BaseModel):
    device_code: str
    user_code: str
    verification_uri: str
    verification_uri_complete: str
    expires_in: int
    interval: int
    support_level: str = "supported"
    terms_warning: str | None = None


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
