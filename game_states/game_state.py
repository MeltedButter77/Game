import pygame
import pygame._sdl2.controller
from game_states.state_helpers import BaseState, StateTransition, load_level
from game_classes.camera_class import Camera
from game_classes.input_handler import InputHandler


class GameState(BaseState):
    def __init__(self, context):
        super().__init__(context)
        self.camera = Camera(self.context["screen_size"])

        self.game_sprites = {
            "blocks": pygame.sprite.Group(),
            "players": pygame.sprite.Group()
        }

        self.controllers = None
        self.input_handlers = None
        self.load_input_handlers()

        self.load_controllers_event = pygame.USEREVENT + 1
        pygame.time.set_timer(self.load_controllers_event, 1000)

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
                if not input_handler.controller.get_init():
                    input_handler.player.input_handler = None
                    input_handler.player = None
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

            # On input, assign unassigned player to input handler and vice versa
            for input_handler in self.input_handlers:
                if input_handler.player:
                    continue

                user_input = input_handler.get_input()

                if all(not value for value in user_input.values()):
                    continue
                for value in user_input.values():
                    if value:
                        for player in self.game_sprites["players"]:
                            if not player.input_handler:
                                input_handler.player = player
                                player.input_handler = input_handler
                                break
                        break

    def load_level(self, player_count, world, level):
        load_level(self, self.context["grid_size"], player_count, world, level)
        self.controllers = None
        self.input_handlers = None
        self.load_input_handlers()

    def save_level(self):
        pass

    def update(self, delta_time):
        # Calculate next positions
        for player in self.game_sprites["players"].sprites():
            player.calc_next_pos(delta_time, self.game_sprites["blocks"].sprites() + self.game_sprites["players"].sprites())

        # Move players
        for player in self.game_sprites["players"].sprites():
            player.apply_next_pos()
            if player.input_handler:
                player.apply_input(delta_time)

        if len(self.game_sprites["players"].sprites()) > 0:
            center_of_all_players = pygame.Vector2(0, 0)
            for player in self.game_sprites["players"].sprites():
                center_of_all_players += player.rect.center
            center_of_all_players /= len(self.game_sprites["players"].sprites())
            self.camera.move_center_to(center_of_all_players)

    def render(self, screen):
        screen.fill("light blue")
        for object_group in self.game_sprites.values():
            for sprite in object_group.sprites():
                sprite.draw(screen, self.camera)
