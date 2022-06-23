import json

from DiscordClient import DiscordClient

config = json.load(open("config.json", 'rb'))


client = DiscordClient()
client.run(config["token"])