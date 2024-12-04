from enum import Enum


api_url: str = 'https://api.rac-corp.net/'


class Endpoints(Enum):
    # ai endpoints
    AI_GEMINI_CREATE = api_url + 'ai/gemini/create'
    AI_MODERATION_TEXT = api_url + 'ai/moderation/text'
    AI_CAI_CREATE = api_url + 'ai/cai/create'
    AI_CAI_HISTORY = api_url + 'ai/cai/history'

    # TODO: other endpoints