

class StateTransition:
    def __init__(self, type_, target=None, data=None):
        self.type = type_          # e.g., "push", "pop", "switch", "quit"
        self.target = target       # e.g., "editor", "menu"
        self.data = data or {}     # Optional extra info


class BaseState:
    def __init__(self, context):
        self.context = context
        self.next_transitions = None

    def handle_events(self, events):
        pass

    def update(self, delta_time):
        pass

    def render(self, screen):
        pass
