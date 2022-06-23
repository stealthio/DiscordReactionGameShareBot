from Commands import *
import vgamepad


class CommandToGamepadMapper:
    def __init__(self, gamepad_object):
        self.gamepad_object = gamepad_object
    
    def exec_action(self, action):
        commands = action["commands"]
        duration = action["duration"]
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