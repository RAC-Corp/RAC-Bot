from typing import Union, Any, Optional

import aiohttp
import json as JSON

from .enums import Endpoints


class Functions:
    def __init__(self, bot, disabled: bool = False) -> None:
        self.bot = bot
        self.disabled: bool = disabled

    async def get_body(self, response: aiohttp.ClientResponse) -> Union[Any, str]:
        try:
            body = await response.json()
            return body
        except:
            body = await response.text()
            return body
        
    async def endpoint_request(
        self, 
        endpoint: Endpoints, 
        method: str = 'get',
        /, 
        *,
        headers: dict[str, Any] = {}, 
        json: dict[str, Any] = {}, 
        params: dict[str, Any] = {}
    ) -> tuple[int, Optional[str], Union[str, Any]]:
        if self.disabled:
            return (500, 'Internal Server Error', 'The system is in recovery mode')

        async with self.bot.session.request(
            method, endpoint.value, headers=headers, json=json, params=params
        ) as resp:
            body: Union[str, Any] = await self.get_body(resp)
            return (resp.status, resp.reason, body)
        
    async def image_request(
        self, 
        endpoint: Endpoints, 
        method: str = 'get',
        /, 
        *,
        headers: dict[str, Any] = {}, 
        json: dict[str, Any] = {}, 
        params: dict[str, Any] = {}
    ) -> tuple[int, Optional[str], Union[str, bytes]]:
        if self.disabled:
            return (500, 'Internal Server Error', 'The system is in recovery mode')

        async with self.bot.session.request(
            method, endpoint.value, headers=headers, json=json, params=params
        ) as resp:
            body: Union[str, Any] = await resp.read()
            return (resp.status, resp.reason, body)