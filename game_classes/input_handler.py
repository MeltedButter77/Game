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
            keys = pygame.key.get_pressed()  # Get active keyboard state
            controls["jump"] = keys[self.key_binds["jump"]]
            controls["up"] = keys[self.key_binds["up"]]
            controls["down"] = keys[self.key_binds["down"]]
            controls["left"] = keys[self.key_binds["left"]]
            controls["right"] = keys[self.key_binds["right"]]
            return controls

        elif self.controller:
            if self.controller.get_button(self.key_binds["jump"]):
                controls["jump"] = True
            if self.controller.get_axis(self.key_binds["left_y_axis"]) < -self.axis_threshold:
                controls["up"] = True
            if self.controller.get_axis(self.key_binds["left_y_axis"]) > self.axis_threshold:
                controls["down"] = True
            if self.controller.get_axis(self.key_binds["left_x_axis"]) < -self.axis_threshold:
                controls["left"] = True
            if self.controller.get_axis(self.key_binds["left_x_axis"]) > self.axis_threshold:
                controls["right"] = True

        return controls
