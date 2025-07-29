import pygame
from game_states.state_helpers import BaseState, StateTransition, load_level
from game_classes.camera_class import Camera


class GameState(BaseState):
    def __init__(self, context):
        super().__init__(context)
        self.camera = Camera(self.context["screen_size"])

        self.game_sprites = {
            "blocks": pygame.sprite.Group(),
            "players": pygame.sprite.Group()
        }

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.next_transitions = [StateTransition("quit")]
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.next_transitions = [StateTransition("push", "menu", {"submenu": "game_pause"})]

            # On input, assign unassigned player to input handler and vice versa
            # filter all input handlers that do not have a player
            for input_handler in self.context["input_handlers"]:
                if input_handler.player:
                    continue

                # filter all input handlers that are not inputting
                if not any(input_handler.get_input().values()):
                    continue

                for player in self.game_sprites["players"].sprites():
                    if not player.input_handler:
                        input_handler.player = player
                        player.input_handler = input_handler
                        if not isinstance(input_handler.joystick, str):
                            print(f"Assigned {self.game_sprites["players"].sprites().index(player)} to {input_handler.joystick.get_name()}")
                        else:
                            print(f"Assigned {self.game_sprites["players"].sprites().index(player)} to keyboard_1 or keyboard_2")
                        break

    def load_level(self, player_count, world, level):
        load_level(self, self.context["grid_size"], player_count, world, level)

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
