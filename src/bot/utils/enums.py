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
    ai_gemini_create = api_url + 'ai/gemini/create'
    ai_cloudflare_text_create = api_url + 'ai/cf/text/create'
    ai_cloudflare_image_create = api_url + 'ai/cf/image/create'
    ai_moderation_text = api_url + 'ai/moderation/text'
    ai_cai_create = api_url + 'ai/cai/create'
    ai_cai_history = api_url + 'ai/cai/history'

    # bot commands endpoints
    bot_commands_upload_commands = api_url + 'bot/commands/upload'

    # player endpoints
    iisr_temp_ban_create = api_url + 'roblox/iisr/players/ban/temp'
    iisr_perm_ban_create = api_url + 'roblox/iisr/players/ban/perm'
    iisr_temp_ban_all_servers = api_url + 'roblox/iisr/players/ban/temp/all-servers'
    iisr_perm_ban_all_servers = api_url + 'roblox/iisr/players/ban/perm/all-servers'

    # utility endpoints
    utility_ping = api_url + 'utilities/ping'

    # TODO: other endpoints