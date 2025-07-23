import json
from enum import StrEnum


class ConfigKeys(StrEnum):
    DISCORD_BOT_TOKEN = "discordBotToken"
    REGISTERED_CHANNELS = "registeredChannels"
    LAST_FLAVORS = "lastFlavors"

class Config(object):
    _config = None
    def __init__(self):
        with open("config.json") as f:
            self._config = json.load(f)

    def get(self, key):
        return self._config.get(key)

    def set(self, key, value):
        self._config[key] = value
        with open("config.json", "w") as f:
            json.dump(self._config, f, indent=4)