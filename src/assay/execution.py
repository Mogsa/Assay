from typing import Literal

from fastapi import Request

ExecutionMode = Literal["manual", "autonomous"]

EXECUTION_MODE_HEADER = "X-Assay-Execution-Mode"


def resolve_execution_mode(request: Request) -> ExecutionMode:
    if request.headers.get("Authorization", "").startswith("Bearer "):
        if request.headers.get(EXECUTION_MODE_HEADER, "").lower() == "autonomous":
            return "autonomous"
        return "manual"

    # Browser and human-session traffic is always manual.
    if request.cookies.get("session"):
        return "manual"

    return "manual"
