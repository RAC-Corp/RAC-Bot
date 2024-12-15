from typing import Union, Any, Optional

import aiohttp
import json as JSON

from .enums import Endpoints


class Functions:
    def __init__(self, bot) -> None:
        self.bot = bot

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
        async with self.bot.session.request(
            method, endpoint.value, headers=headers, json=json, params=params
        ) as resp:
            body: Union[str, Any] = await self.get_body(resp)
            return (resp.status, resp.reason, body)