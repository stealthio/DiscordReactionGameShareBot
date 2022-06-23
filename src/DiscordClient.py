import asyncio
import json
import threading
import time
import discord

from CommandToGamepadMapper import CommandToGamepadMapper
from GamePad import GamePad

config = json.load(open("./config.json", 'rb'))
gameConfig = json.load(open(config["gameConfiguration"], 'rb'))

mappers = []

class DiscordClient(discord.Client):
    async def on_reaction_add(self, reaction, user):
        if user == self.user:
            return
        if reaction.emoji in gameConfig["teams"]:
            # check if the user is in the team already, if so, remove them
            if user.id in self.user_mapping:
                if self.user_mapping[user.id] == gameConfig["teams"][reaction.emoji]:
                    self.user_mapping[user.id] = None
                    for message in self.teammessages:
                        if user.mention in self.teammessages[message].content:
                            await self.teammessages[message].edit(content=self.teammessages[message].content.replace(user.mention, ""))
                    await reaction.remove(user)
                    return

            self.user_mapping[user.id] = gameConfig["teams"][reaction.emoji]
            for message in self.teammessages:
                if user.mention in self.teammessages[message].content:
                    await self.teammessages[message].edit(content = self.teammessages[message].content.replace(user.mention, ""))
            await self.teammessages[reaction.emoji].edit(content = self.teammessages[reaction.emoji].content + " " + user.mention)

        if not user.id in self.user_mapping:
            await reaction.remove(user)
            return
        
        if reaction.emoji in gameConfig["actions"]:
            if config["votingMode"] == 0:
                target_mapper = mappers[self.user_mapping[user.id]]
                action = gameConfig["actions"][reaction.emoji]
                target_mapper.exec_actions(action)
            elif config["votingMode"] == 1:
                self.team_commands[self.user_mapping[user.id]].append(reaction.emoji)

        await reaction.remove(user)

    async def on_ready(self):
        self.channel = self.get_channel(config["channelId"])

        # clean up previous messages
        async for message in self.channel.history(limit=20):
            if message.author == self.user:
                await message.delete()
        team_message = await self.channel.send("Join a team")

        teams = []
        for item in gameConfig["teams"]:
            await team_message.add_reaction(item)
            mappers.append(CommandToGamepadMapper(GamePad()))
            teams.append(item)
    
        action_message = await self.channel.send("Actions")

        for k,v in gameConfig["actions"].items():
            await action_message.add_reaction(k)

        self.teammessages = {}
        for team in teams:
            self.teammessages[team] = await self.channel.send("Team " + team + ":\n")

        self.user_mapping = {}

        if config["votingMode"] == 1:
            self.team_commands = []
            for team in teams:
                self.team_commands.append([])


            self.timer_message = await self.channel.send("Timer: " + str(config["votingTime"]) + " seconds")
            self.timer = config["votingTime"]
            _thread = threading.Thread(target=self.start_timer)
            _thread.start()
            
    def start_timer(self):
        time_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(time_loop)
        time_loop.run_until_complete(self.timer_counter())

    async def timer_counter(self):
        while True:
            time.sleep(1)
            self.timer -= 1
            if self.timer <= 0:
                self.timer = config["votingTime"]
                print(self.team_commands)
                for i in range(len(self.team_commands)):
                    team_command = self.team_commands[i]
                    if len(team_command) > 0:
                        most_used = max(set(team_command), key = team_command.count)
                        print("Team " + str(i) + most_used)
                        action = gameConfig["actions"][most_used]
                        mappers[i].exec_actions(action)
                        self.team_commands[i] = []