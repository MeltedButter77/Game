import json
import os

import pygame
from game_classes.block_class import Block
from game_classes.player_class import Player


# Shared logic for loading a level
def load_level(app_state, grid_size, player_count, world, level, retry_count=0):
    if retry_count >= 2:
        print("Failed to load or create level file after maximum retries")
        return False

    try:
        with open(f"levels/{player_count}_players/world_{world}/level_{level}.json", "r") as f:
            data = json.load(f)
            app_state.game_sprites = {"blocks": pygame.sprite.Group(), "players": pygame.sprite.Group()}

            for block_data in data["blocks"]:
                block = Block(grid_size,
                              pygame.Rect(block_data["x"], block_data["y"], block_data["width"], block_data["height"]))
                block.color = block_data["color"]
                block.add(app_state.game_sprites["blocks"])
            for player_data in data["players"]:
                player = Player((player_data["x"], player_data["y"]))
                player.color = player_data["color"]
                player.add(app_state.game_sprites["players"])

        print(f"Level loaded from levels/{player_count}_players/world_{world}/level_{level}.json")
        return True
    except FileNotFoundError:
        print(f"Level not found in levels/{player_count}_players/world_{world}/level_{level}.json")
        print(f"Creating an empty level in levels/{player_count}_players/world_{world}/level_{level}.json")
        try:
            os.makedirs(os.path.dirname(f"levels/{player_count}_players/world_{world}/level_{level}.json"),
                        exist_ok=True)
            with open(f"levels/{player_count}_players/world_{world}/level_{level}.json", "w") as f:
                json.dump({"blocks": [], "players": []}, f)
            return load_level(app_state, grid_size, player_count, world, level, retry_count + 1)
        except Exception as e:
            print(f"Error creating level file: {e}")
            return False


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
