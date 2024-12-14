from typing import Union, Optional
from discord.ext import commands


class IISRTempBanFlags(commands.FlagConverter, case_insensitive=True, prefix='-', delimiter=' '):
    target: str # Union[str, int]
    duration: str
    reason: Optional[str] = None


class IISRPermBanFlags(commands.FlagConverter, case_insensitive=True, prefix='-', delimiter=' '):
    target: str
    reason: Optional[str] = None