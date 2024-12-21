from typing import Any, Optional
from discord.ext.commands import CommandError


class HTTPException(CommandError):
    def __init__(
        self, 
        status: int, 
        detail: str, 
        body: Optional[Any] = None,
        message: Optional[str] = None,
        *args: Any
    ) -> None:
        super().__init__(message, args)
        self.status = status
        self.detail = detail
        self.body = body


class GeneralException(CommandError):
    def __init__(
        self, 
        error: Any,
        message: Optional[str] = None,
        *args: Any
    ) -> None:
        super().__init__(message, args)
        self.error = error