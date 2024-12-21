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

    # iisr player endpoints
    iisr_temp_ban_create = api_url + 'roblox/iisr/players/ban/temp'
    iisr_perm_ban_create = api_url + 'roblox/iisr/players/ban/perm'
    iisr_temp_ban_all_servers = api_url + 'roblox/iisr/players/ban/temp/all-servers'
    iisr_perm_ban_all_servers = api_url + 'roblox/iisr/players/ban/perm/all-servers'
    iisr_ban_remove = api_url + 'roblox/iisr/players/ban/remove'
    iisr_ban_remove_all_servers = api_url + 'roblox/iisr/players/ban/remove/all-servers'
    iisr_bans = api_url + 'roblox/iisr/players/bans'
    iisr_kick = api_url + 'roblox/iisr/players/kick'
    iisr_kick_all = api_url + 'roblox/iisr/players/kick/all'

    # iisr server endpoints
    iisr_server_shutdown = api_url + 'roblox/iisr/server/shutdown'
    iisr_server_info = api_url + 'roblox/iisr/server/info'
    iisr_server_lock = api_url + 'roblox/iisr/server/lock'
    iisr_server_unlock = api_url + 'roblox/iisr/server/unlock'
    iisr_server_announce = api_url + 'roblox/iisr/server/announce'
    iisr_server_announce_all = api_url + 'roblox/iisr/server/announce/all'

    # roguessr server endpoints
    roguessr_server_shutdown = api_url + 'roblox/roguessr/server/shutdown'
    roguessr_server_info = api_url + 'roblox/roguessr/server/info'
    # roguessr_server_lock = api_url + 'roblox/roguessr/server/lock'
    # roguessr_server_unlock = api_url + 'roblox/roguessr/server/unlock'
    roguessr_server_announce = api_url + 'roblox/roguessr/server/announce'
    roguessr_server_announce_all = api_url + 'roblox/roguessr/server/announce/all'

    # roguessr game endpoints
    roguessr_game_maps = api_url + 'roblox/roguessr/game/maps'
    roguessr_game_change_map = api_url + 'roblox/roguessr/game/change-map'

    # utility endpoints
    utility_ping = api_url + 'utilities/ping'
    utility_usage = api_url + 'utilities/usage'
    utility_uptime = api_url + 'utilities/uptime'
    utility_tasks = api_url + 'utilities/tasks'

    # TODO: other endpoints