import json

from DiscordClient import DiscordClient


config = json.load(open("config.json", 'rb'))
gameConfig = json.load(open(config["gameConfiguration"], 'rb'))


client = DiscordClient()
client.run(config["token"])