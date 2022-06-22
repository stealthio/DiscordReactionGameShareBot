from multiprocessing.connection import wait
import random
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

    def queue_left_stick_direction(self, joystick_command):
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
        gamepad_object.press_button(self.input)
        timer = threading.Timer(self.duration, self.release, [gamepad_object])
        timer.start()
        if self.chained:
            return 0.0
        return self.duration
    
    def release(self, gamepad_object):
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
                    self.gamepad_object.queue_left_stick_direction(JoystickCommand(True, -1, 0, duration, chain))
                elif command.endswith("_right"):
                    self.gamepad_object.queue_left_stick_direction(JoystickCommand(True, 1, 0, duration, chain))
                elif command.endswith("_up"):
                    self.gamepad_object.queue_left_stick_direction(JoystickCommand(True, 0, 1, duration, chain))
                elif command.endswith("_down"):
                    self.gamepad_object.queue_left_stick_direction(JoystickCommand(True, 0, -1, duration, chain))
                elif command.endswith("_up_left"):
                    self.gamepad_object.queue_left_stick_direction(JoystickCommand(True, -1, 1, duration, chain))
                elif command.endswith("_up_right"):
                    self.gamepad_object.queue_left_stick_direction(JoystickCommand(True, 1, 1, duration, chain))
                elif command.endswith("_down_left"):
                    self.gamepad_object.queue_left_stick_direction(JoystickCommand(True, -1, -1, duration, chain))
                elif command.endswith("_down_right"):
                    self.gamepad_object.queue_left_stick_direction(JoystickCommand(True, 1, -1, duration, chain))
            elif command == "a":
                self.gamepad_object.queue_input(InputCommand(vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_A, duration, chain))
            elif command == "b":
                self.gamepad_object.queue_input(InputCommand(vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_B, duration, chain))
            elif command == "x":
                self.gamepad_object.queue_input(InputCommand(vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_X, duration, chain))
            elif command == "y":
                self.gamepad_object.queue_input(InputCommand(vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_Y, duration, chain))

class DiscordClient(discord.Client):
    async def on_reaction_add(self, reaction, user):
        if user == self.user:
            return
        if reaction.emoji in config["teams"]:
            self.user_mapping[user.id] =  config["teams"][reaction.emoji]
        if not user.id in self.user_mapping:
            return
        
        target_mapper = mappers[self.user_mapping[user.id]]

        if reaction.emoji in config["actions"]:
            action = config["actions"][reaction.emoji]
            target_mapper.exec_actions(action)

        await reaction.remove(user)

    async def on_ready(self):
        # get the first text channel on the discord server 
        self.channel = self.get_channel(989181971764748320)
        team_message = await self.channel.send("Join a team")

        for item in config["teams"]:
            await team_message.add_reaction(item)
            mappers.append(CommandToGamepadMapper(GamePad()))

        action_message = await self.channel.send("Actions")

        for k,v in config["actions"].items():
            await action_message.add_reaction(k)

        self.user_mapping = {}

mappers = []

config = json.load(open('niddhog.json', 'rb'))


client = DiscordClient()
client.run("")
