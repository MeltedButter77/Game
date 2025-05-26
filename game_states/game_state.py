import pygame
import pygame._sdl2.controller
from game_states.state_helpers import BaseState, StateTransition, load_level
from game_classes.camera_class import Camera


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


class GameState(BaseState):
    def __init__(self, context):
        super().__init__(context)
        self.camera = Camera()

        self.game_sprites = {
            "blocks": pygame.sprite.Group(),
            "players": pygame.sprite.Group()
        }

        self.controllers = None
        self.input_handlers = None
        self.load_input_handlers()

        self.load_controllers_event = pygame.USEREVENT + 1
        pygame.time.set_timer(self.load_controllers_event, 10000)

    def load_input_handlers(self):
        if self.controllers is None:
            self.controllers = []
        if self.input_handlers is None:
            self.input_handlers = [InputHandler("keyboard")]

        # Populate controllers list
        for i in range(pygame._sdl2.controller.get_count() - 1):
            if not pygame._sdl2.controller.Controller(i) in self.controllers:
                if not pygame._sdl2.controller.Controller(i).get_init():
                    pygame._sdl2.controller.Controller(i).init()
                self.controllers.append(pygame._sdl2.controller.Controller(i))

        for controller in self.controllers:
            # Remove controllers that are no longer connected
            if not controller.attached():
                self.controllers.remove(controller)
                controller.quit()

            # Assign a handler to each controller
            has_handler = False
            for input_handler in self.input_handlers:
                if input_handler.controller == controller:
                    has_handler = True
            if not has_handler:
                self.input_handlers.append(InputHandler(controller))

        # Remove deactivated controller's input_handlers
        for input_handler in self.input_handlers:
            if not input_handler.controller == "keyboard":
                try:
                    if not input_handler.controller.attached():
                        self.input_handlers.remove(input_handler)
                        input_handler.controller.quit()
                except Exception as e:
                    print(e)
                    self.input_handlers.remove(input_handler)
                    input_handler.controller.quit()

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.next_transitions = [StateTransition("quit")]

            if event.type == self.load_controllers_event:
                self.load_input_handlers()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.next_transitions = [StateTransition("push", "menu", {"submenu": "game_pause"})]

            # On input, assign the input handler to the player and player to input handler
            for input_handler in self.input_handlers:
                user_input = input_handler.get_input()
                for value in user_input.values():
                    if value:
                        for player in self.game_sprites["players"]:
                            if not player.input_handler:
                                input_handler.player = self.game_sprites["players"].sprites()[0]
                                input_handler.player.input_handler = input_handler

    def load_level(self, player_count, world, level):
        load_level(self, player_count, world, level)

    def save_level(self):
        pass

    def update(self, delta_time):
        for player in self.game_sprites["players"].sprites():
            player.calc_next_pos(self.game_sprites["blocks"].sprites())

        for player in self.game_sprites["players"].sprites():
            player.apply_next_pos()
            if player.input_handler:
                player.apply_input()
        self.camera.x = self.game_sprites["players"].sprites()[0].rect.centerx - self.context["game_size"][0] / 2
        self.camera.y = self.game_sprites["players"].sprites()[0].rect.centery - self.context["game_size"][1] / 2

    def render(self, screen):
        screen.fill("light blue")
        for object_group in self.game_sprites.values():
            for sprite in object_group.sprites():
                screen.blit(sprite.image, sprite.rect.copy().move(-self.camera.x, -self.camera.y))
