import pygame
from game_states.base_state import BaseState


class PlayState(BaseState):
    def __init__(self, context):
        super().__init__(context)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.next_state = "quit"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.next_state = "pause_game"

    def update(self, delta_time):
        pass

    def render(self, screen):
        screen.fill("light blue")