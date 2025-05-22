import pygame.surface


class BaseState:
    def __init__(self, context):
        self.context = context
        self.next_state = None

    def handle_events(self, events):
        pass

    def update(self, delta_time):
        pass

    def render(self, screen):
        pass
