from typing import Any

from pydantic import BaseModel


class SendRespose(BaseModel):
    success: bool
    message: str | None = None
    data: Any
