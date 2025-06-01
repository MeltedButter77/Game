import pygame


class InputHandler:
    def __init__(self, controller):
        self.player = None
        self.controller = controller  # pygame._sdl2.controller.Controller(0)

        self.axis_threshold = 2

        if controller == "keyboard":
            self.key_binds = {
                "up": pygame.K_w,
                "down": pygame.K_s,
                "left": pygame.K_a,
                "right": pygame.K_d,
                "jump": pygame.K_SPACE,
            }
        else:
            self.key_binds = {
                "left_y_axis": 1,  # Y-axis negative movement
                "left_x_axis": 0,  # X-axis positive movement
                "right_y_axis": 3,  #
                "right_x_axis": 2,  #
                "jump": 0,
            }

    def get_input(self):

        controls = {
            "jump": False,
            "up": False,
            "down": False,
            "left": False,
            "right": False,
        }

        if self.controller == "keyboard":
            pressed = pygame.key.get_pressed()
            controls["jump"] = pressed[self.key_binds["jump"]]
            controls["up"] = pressed[self.key_binds["up"]]
            controls["down"] = pressed[self.key_binds["down"]]
            controls["left"] = pressed[self.key_binds["left"]]
            controls["right"] = pressed[self.key_binds["right"]]
        else:
            if not self.controller.get_init():
                return None

            # Get axis values (left analog stick)
            axis_x = self.controller.get_axis(self.key_binds["left_x_axis"])
            axis_y = self.controller.get_axis(self.key_binds["left_y_axis"])
            # Button press
            controls["jump"] = self.controller.get_button(self.key_binds["jump"])

            # Convert analog input to digital-style booleans
            controls["left"] = axis_x < -self.axis_threshold
            controls["right"] = axis_x > self.axis_threshold
            controls["up"] = axis_y < -self.axis_threshold
            controls["down"] = axis_y > self.axis_threshold

        return controls
