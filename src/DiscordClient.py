import asyncio
import threading
import discord
import Manager
       
class DiscordClient(discord.Client):
    async def on_reaction_add(self, reaction, user):
        if user == self.user: # Don't react to own messages
            return
        Manager.handle_reaction(reaction, user)
        Manager.set_info_message(self)
        await reaction.remove(user)

    # Deletes the previous messages by the bot
    async def clean_up(self):
        async for message in self.channel.history(limit=20):
            if message.author == self.user:
                await message.delete()
    
    async def send_message(self, message):
        return await self.channel.send(message)

    async def set_info_message(self, message):
        await self.info_message.edit(content=message)

    async def add_reaction(self, message, reaction):
        return await message.add_reaction(reaction)

    def set_channel(self, channel):
        self.channel = self.get_channel(channel)

    def execute_async_function_parallel(self, function, *args):
        print("Executing function: " + function.__name__ + " with args: " + str(args))
        asyncio.run_coroutine_threadsafe(function(*args), self.loop)

    def run_parallel(self, function, *args):
        thread = threading.Thread(target=self.execute_async_function_parallel, args=(function, *args))
        thread.start()

    async def on_ready(self):
        Manager.setup_discord_bot(self)
        await(self.clean_up())

        # Set up the team message and reactions
        self.join_team_message = await self.send_message("Join a team")
        for team in Manager.teams:
            await self.add_reaction(self.join_team_message, team)
        
        # Set up the action message and reactions
        self.action_message = await self.send_message("Actions")
        for action in Manager.actions:
            await self.add_reaction(self.action_message, action)
        
        # Set up an informational message that will be updated on changes
        self.info_message = await self.send_message(".")
