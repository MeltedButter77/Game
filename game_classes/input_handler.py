import pygame


class InputHandler:
    def __init__(self, joystick=None):
        self.player = None
        self.joystick = joystick  # will be controller object or "keyboard"

        self.axis_threshold = 0.2

        self.controls = {
            "jump": False,
            "up": False,
            "down": False,
            "left": False,
            "right": False,
        }

        self.keyboard_binds_1 = {
            "up": pygame.K_w,
            "down": pygame.K_s,
            "left": pygame.K_a,
            "right": pygame.K_d,
            "jump": pygame.K_SPACE,
        }
        self.keyboard_binds_2 = {
            "up": pygame.K_UP,
            "down": pygame.K_DOWN,
            "left": pygame.K_LEFT,
            "right": pygame.K_RIGHT,
            "jump": pygame.K_SLASH,
        }

        self.joystick_binds = {
            "left_y_axis": 1,  # Y-axis negative movement
            "left_x_axis": 0,  # X-axis positive movement
            "right_y_axis": 3,  #
            "right_x_axis": 2,  #
            "l2_axis": 4,
            "r2_axis": 5,
            "r1_button": 5,
            "l1_button": 4,
            "a_button": 0,
            "b_button": 1,
            "x_button": 2,
            "y_button": 3,
        }

    def get_input(self):
        if self.joystick in ["keyboard_1", "keyboard_2"]:
            pressed = pygame.key.get_pressed()
            binds = self.keyboard_binds_1 if self.joystick == "keyboard_1" else self.keyboard_binds_2

            for action in ["jump", "up", "down", "left", "right"]:
                self.controls[action] = pressed[binds[action]]

        else:
            if not self.joystick.get_init():
                return None

            # Get axis values (left analog stick)
            axis_x = self.joystick.get_axis(self.joystick_binds["left_x_axis"])
            axis_y = self.joystick.get_axis(self.joystick_binds["left_y_axis"])
            # Button press
            self.controls["jump"] = self.joystick.get_button(self.joystick_binds["a_button"])

            # Convert analog input to booleans
            self.controls["left"] = axis_x < -self.axis_threshold
            self.controls["right"] = axis_x > self.axis_threshold
            self.controls["up"] = axis_y < -self.axis_threshold
            self.controls["down"] = axis_y > self.axis_threshold

        return self.controls
