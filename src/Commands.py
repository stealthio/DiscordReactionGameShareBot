import threading


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