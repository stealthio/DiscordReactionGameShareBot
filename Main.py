import asyncio
import time
import threading
import vgamepad
import discord
import json

# A class for each connected virtual gamepad. Holds the queued InputCommands
class GamePad:
    def __init__(self):
        self.input_queue = []
        self.gamepad = vgamepad.VX360Gamepad()
        self.execution_loop_thread = threading.Thread(target=self.execution_loop)
        self.execution_loop_thread.start()
    
    def queue_input(self, input_command):
        self.input_queue.append(input_command)
    
    def execute_next_input(self):
        if len(self.input_queue) > 0:
            return self.input_queue.pop(0).execute(self)
        return 0.1
    
    def execution_loop(self):
        while True:
            time.sleep(self.execute_next_input() + 0.1)
        
    def press_button(self, button):
        self.gamepad.press_button(button)
        self.gamepad.update()
    
    def release_button(self, button):
        self.gamepad.release_button(button)
        self.gamepad.update()

    def queue_stick_direction(self, joystick_command):
        self.input_queue.append(joystick_command)

class JoystickCommand:
    def __init__(self, left, x_amount, y_amount, duration, chained = False):
        self.left = left
        self.x_amount = x_amount
        self.y_amount = y_amount
        self.duration = duration
        self.chained = chained
    
    def __str__(self):
        return "JoystickCommand: " + str(self.left) + " " + str(self.x_amount) + " " + str(self.y_amount) + " " + str(self.duration)

    def execute(self, gamepad_object):
        if self.left:
            gamepad_object.gamepad.left_joystick_float(self.x_amount, self.y_amount)
            timer = threading.Timer(self.duration, self.reset, [gamepad_object])
            timer.start()
        else:
            gamepad_object.gamepad.right_joystick_float(self.x_amount, self.y_amount)
            timer = threading.Timer(self.duration, self.reset, [gamepad_object])
            timer.start()
        gamepad_object.gamepad.update()
        if self.chained:
            return 0.0
        return self.duration
    
    def reset(self, gamepad_object):
        if self.left:
            gamepad_object.gamepad.left_joystick_float(0, 0)
        else:
            gamepad_object.gamepad.right_joystick_float(0, 0)
        gamepad_object.gamepad.update()

# a class for input commands that will be queued
class InputCommand:
    def __init__(self, input, duration, chained = False):
        self.input = input
        self.duration = duration
        self.chained = chained
    
    def execute(self, gamepad_object):
        if self.input == "lt":
            gamepad_object.gamepad.left_trigger_float(value_float=1.0)
        elif self.input == "rt":
            gamepad_object.gamepad.right_trigger_float(value_float=1.0)
        elif self.input == "wait":
            return self.duration
        else:
            gamepad_object.press_button(self.input)
        timer = threading.Timer(self.duration, self.release, [gamepad_object])
        timer.start()
        if self.chained:
            return 0.0
        return self.duration
    
    def release(self, gamepad_object):
        if self.input == "lt":
            gamepad_object.gamepad.left_trigger_float(value_float=0.0)
        elif self.input == "rt":
            gamepad_object.gamepad.right_trigger_float(value_float=0.0)
        else:
            gamepad_object.release_button(self.input)

class CommandToGamepadMapper:
    def __init__(self, gamepad_object):
        self.gamepad_object = gamepad_object
    
    def exec_actions(self, actions):
        commands = actions["commands"]
        duration = actions["duration"]
        for i in range(len(commands)):
            command = commands[i]
            chain = i < len(commands) - 1
            if command.startswith("left_stick"):
                if command.endswith("_left"):
                    self.gamepad_object.queue_stick_direction(JoystickCommand(True, -1, 0, duration, chain))
                elif command.endswith("_right"):
                    self.gamepad_object.queue_stick_direction(JoystickCommand(True, 1, 0, duration, chain))
                elif command.endswith("_up"):
                    self.gamepad_object.queue_stick_direction(JoystickCommand(True, 0, 1, duration, chain))
                elif command.endswith("_down"):
                    self.gamepad_object.queue_stick_direction(JoystickCommand(True, 0, -1, duration, chain))
                elif command.endswith("_up_left"):
                    self.gamepad_object.queue_stick_direction(JoystickCommand(True, -1, 1, duration, chain))
                elif command.endswith("_up_right"):
                    self.gamepad_object.queue_stick_direction(JoystickCommand(True, 1, 1, duration, chain))
                elif command.endswith("_down_left"):
                    self.gamepad_object.queue_stick_direction(JoystickCommand(True, -1, -1, duration, chain))
                elif command.endswith("_down_right"):
                    self.gamepad_object.queue_stick_direction(JoystickCommand(True, 1, -1, duration, chain))
            elif command.startswith("right_stick"):
                if command.endswith("_left"):
                    self.gamepad_object.queue_stick_direction(JoystickCommand(False, -1, 0, duration, chain))
                elif command.endswith("_right"):
                    self.gamepad_object.queue_stick_direction(JoystickCommand(False, 1, 0, duration, chain))
                elif command.endswith("_up"):
                    self.gamepad_object.queue_stick_direction(JoystickCommand(False, 0, 1, duration, chain))
                elif command.endswith("_down"):
                    self.gamepad_object.queue_stick_direction(JoystickCommand(False, 0, -1, duration, chain))
                elif command.endswith("_up_left"):
                    self.gamepad_object.queue_stick_direction(JoystickCommand(False, -1, 1, duration, chain))
                elif command.endswith("_up_right"):
                    self.gamepad_object.queue_stick_direction(JoystickCommand(False, 1, 1, duration, chain))
                elif command.endswith("_down_left"):
                    self.gamepad_object.queue_stick_direction(JoystickCommand(False, -1, -1, duration, chain))
                elif command.endswith("_down_right"):
                    self.gamepad_object.queue_stick_direction(JoystickCommand(False, 1, -1, duration, chain))
            elif command == "a":
                self.gamepad_object.queue_input(InputCommand(vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_A, duration, chain))
            elif command == "b":
                self.gamepad_object.queue_input(InputCommand(vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_B, duration, chain))
            elif command == "x":
                self.gamepad_object.queue_input(InputCommand(vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_X, duration, chain))
            elif command == "y":
                self.gamepad_object.queue_input(InputCommand(vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_Y, duration, chain))
            elif command == "lb":
                self.gamepad_object.queue_input(InputCommand(vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER, duration, chain))
            elif command == "rb":
                self.gamepad_object.queue_input(InputCommand(vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER, duration, chain))
            elif command == "lt":
                self.gamepad_object.queue_input(InputCommand("lt", duration, chain))
            elif command == "rt":
                self.gamepad_object.queue_input(InputCommand("rt", duration, chain))
            elif command == "wait_short":
                self.gamepad_object.queue_input(InputCommand("wait", 0.2, False))
            elif command == "wait_medium":
                self.gamepad_object.queue_input(InputCommand("wait", 0.5, False))

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


            self.timer_message = await self.channel.send("Timer - " + str(config["votingTime"]) + " seconds")
            self.timer = config["votingTime"]

            self.timer_task = self.loop.create_task(self.timer_counter())

    async def timer_counter(self):
        while True:
            time.sleep(0.25)
            self.timer -= 0.25
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
    

mappers = []

config = json.load(open("config.json", 'rb'))
gameConfig = json.load(open(config["gameConfiguration"], 'rb'))


client = DiscordClient()
client.run(config["token"])