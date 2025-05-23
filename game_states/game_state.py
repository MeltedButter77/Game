import pygame
from game_states.states import BaseState, StateTransition


class GameState(BaseState):
    def __init__(self, context):
        super().__init__(context)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.next_transitions = [StateTransition("quit")]

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.next_transitions = [StateTransition("push", "menu", {"submenu": "pause"})]

    def load_level(self, player_count, world, level):
        pass

    def save_level(self):
        pass

    def update(self, delta_time):
        pass

    def render(self, screen):
        screen.fill("light blue")