import threading
import struct

class MouseDriver:
    def __init__(self, input_file, spd, on_mouse_pressed, rev_x = False, rev_y = False):
        self.mouse_x = 0.5
        self.mouse_y = 0.5
        self.mouse_down = False

        def read_mouse():
            global mouse_x, mouse_y
            try:
                with open(input_file, 'rb') as f:
                    while True:
                        data = f.read(3)
                        button, x_move, y_move = struct.unpack('3b', data)
                        if rev_x:
                            self.mouse_x -= x_move * spd
                        else:
                            self.mouse_x += x_move * spd
                        if rev_y:
                            self.mouse_y -= y_move * spd
                        else:
                            self.mouse_y += y_move * spd
                        if button%2==1:
                            if not self.mouse_down:
                                on_mouse_pressed()
                            self.mouse_down = True
                        else:
                            self.mouse_down = False
                        self.mouse_x = min(max(0,self.mouse_x),1)
                        self.mouse_y = min(max(0,self.mouse_y),1)
            except FileNotFoundError:
                print("Mouse device not found")
            except PermissionError:
                print("Permission denied: Try running as root")

        mouse_thread = threading.Thread(target=read_mouse)
        mouse_thread.daemon = True  # This makes the thread exit when the main program exits
        mouse_thread.start()



    def get(self):
        return self.mouse_x, self.mouse_y
