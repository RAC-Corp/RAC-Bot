from enum import Enum
from .config import Config


api_url: str = 'https://api.rac-corp.net/'
api_headers: dict[str, str] = {
    'Authorization': Config.api_key(),
    'User-Agent': 'RAC-Bot'
}


class CommandSignatures(Enum):
    iisr_temp_ban = '-target <str> -duration <str> -serverid <str> -reason <str?>'
    iisr_perm_ban = '-target <str> -serverid <str> -reason <str?>'


class Endpoints(Enum):
    # ai endpoints
    AI_GEMINI_CREATE = api_url + 'ai/gemini/create'
    AI_CLOUDFLARE_TEXT_CREATE = api_url + 'ai/cf/text/create'
    AI_CLOUDFLARE_IMAGE_CREATE = api_url + 'ai/cf/image/create'
    AI_MODERATION_TEXT = api_url + 'ai/moderation/text'
    AI_CAI_CREATE = api_url + 'ai/cai/create'
    AI_CAI_HISTORY = api_url + 'ai/cai/history'

    # bot commands endpoints
    BOT_COMMANDS_UPLOAD_COMMANDS = api_url + 'bot/commands/upload'

    # player endpoints
    TEMP_BAN_CREATE = api_url + 'roblox/players/ban/temp'
    PERM_BAN_CREATE = api_url + 'roblox/players/ban/perm'

    # utility endpoints
    UTILITY_PING = api_url + 'utilities/ping'

    # TODO: other endpoints