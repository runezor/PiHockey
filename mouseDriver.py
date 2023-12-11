import pyautogui
from pynput.mouse import Listener
import threading

class MouseDriver:
    def __init__(self, window_w, window_h, on_mouse_pressed):
        self.window_x = 0
        self.window_y = 0

        self.window_w = window_w
        self.window_h = window_h

        def on_click(x, y, button, pressed):
            if pressed:
                on_mouse_pressed()

        def start_listener():
            with Listener(on_click=on_click) as listener:
                listener.join()

        listener_thread = threading.Thread(target=start_listener)
        listener_thread.start()

    def get(self):
        mouse_x, mouse_y = pyautogui.position()
        # Update window
        if mouse_x<self.window_x:
            self.window_x = mouse_x
        if mouse_x>self.window_x+self.window_w:
            self.window_x = mouse_x-self.window_w
        if mouse_y<self.window_y:
            self.window_y = mouse_y
        if mouse_y>self.window_y+self.window_h:
            self.window_y = mouse_y-self.window_h

        return (mouse_x-self.window_x)/self.window_w, (mouse_y-self.window_y)/self.window_h