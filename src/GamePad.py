import threading
import time
import vgamepad

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