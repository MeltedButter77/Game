import json
import pygame
from game_classes.block_class import Block


# Shared logic for loading a level
def load_level(app_state, player_count, world, level):
        try:
            with open(f"levels/{player_count}_players/world_{world}/level_{level}.json", "r") as f:
                data = json.load(f)
                app_state.game_sprites = {"blocks": pygame.sprite.Group(), "players": pygame.sprite.Group()}

                for block_data in data["blocks"]:
                    block = Block(
                        pygame.Rect(block_data["x"], block_data["y"], block_data["width"], block_data["height"]))
                    block.color = block_data["color"]
                    block.add(app_state.game_sprites["blocks"])
                for player_data in data["players"]:
                    pass

            print(f"Level loaded from levels/{player_count}_players/world_{world}/level_{level}.json")
        except FileNotFoundError:
            print(f"Level not found in levels/{player_count}_players/world_{world}/level_{level}.json")
            return


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
