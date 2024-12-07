from enum import Enum
from .config import Config


api_url: str = 'https://api.rac-corp.net/'
api_headers: dict[str, str] = {
    'Authorization': Config.api_key()
}


class Endpoints(Enum):
    # ai endpoints
    AI_GEMINI_CREATE = api_url + 'ai/gemini/create'
    AI_MODERATION_TEXT = api_url + 'ai/moderation/text'
    AI_CAI_CREATE = api_url + 'ai/cai/create'
    AI_CAI_HISTORY = api_url + 'ai/cai/history'

    # utility endpoints
    UTILITY_PING = api_url + 'utilities/ping'

    # TODO: other endpoints