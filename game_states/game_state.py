import pygame
from game_states.state_helpers import BaseState, StateTransition, load_level


class GameState(BaseState):
    def __init__(self, context):
        super().__init__(context)

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

    def load_level(self, player_count, world, level):
        load_level(self, player_count, world, level)

    def save_level(self):
        pass

    def update(self, delta_time):
        pass

    def render(self, screen):
        screen.fill("light blue")
        for object_group in self.game_sprites.values():
            for sprite in object_group.sprites():
                screen.blit(sprite.image, sprite.rect)
