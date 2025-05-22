import math
import json
import pygame
from camera_class import Camera
from game_states.states import BaseState, StateTransition


class Block(pygame.sprite.Sprite):
    def __init__(self, rect):
        super().__init__()
        self.color = "blue"
        self.rect = rect

        self.image = pygame.Surface(rect.size)
        self.image.fill(self.color)


class EditorState(BaseState):
    def __init__(self, context):
        super().__init__(context)
        self.camera = Camera(
            {
                "up": pygame.K_w,
                "down": pygame.K_s,
                "left": pygame.K_a,
                "right": pygame.K_d,
            }
        )

        world_width, world_height = 10000, 10000
        self.render_surface = pygame.Surface((world_width, world_height))
        self.mouse_down_pos = None

        self.blocks = pygame.sprite.Group()
        self.players = pygame.sprite.Group()

    def _handle_block_editing(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.next_state = "pause_game"

        # TODO: Fix rounding of positions and sizes when creating new blocks

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:  # Right mouse button pressed
                block_under_mouse = [block for block in self.blocks if block.rect.collidepoint(self.camera.screen_pos_to_game(event.pos))]
                if block_under_mouse:
                    self.blocks.remove(block_under_mouse[0])

            if event.button == 1:  # Left mouse button pressed
                # Convert screen position to game coordinates
                self.mouse_down_pos = self.camera.screen_pos_to_game(event.pos)

                # Snap the position down to the nearest 10 (grid alignment)
                self.mouse_down_pos = (
                    math.floor(self.mouse_down_pos[0] / 10) * 10,
                    math.floor(self.mouse_down_pos[1] / 10) * 10
                )

                # Create a new 10x10 block at the snapped mouse-down position
                Block(pygame.Rect(self.mouse_down_pos, (10, 10))).add(self.blocks)

        if event.type == pygame.MOUSEMOTION:
            if event.buttons[0]:  # The left mouse button is held down
                # Convert the current mouse position to game coordinates
                mouse_pos = self.camera.screen_pos_to_game(event.pos)

                # Snap the position down to the nearest 10 (grid alignment)
                mouse_pos = (
                    math.ceil(mouse_pos[0] / 10) * 10,
                    math.ceil(mouse_pos[1] / 10) * 10
                )

                # Calculate the size of the rectangle based on the drag distance
                dx = mouse_pos[0] - self.mouse_down_pos[0]
                dy = mouse_pos[1] - self.mouse_down_pos[1]

                # Ensure neither width nor height is zero (minimum grid size in either direction)
                size = (
                    dx if dx != 0 else 10,
                    dy if dy != 0 else 10
                )

                # Create a new rect from mouse_down_pos to current mouse_pos
                new_rect = pygame.Rect(self.mouse_down_pos, size)
                new_rect.normalize()  # Adjusts rect to ensure positive width and height

                # Update the size of the most recently created block
                self.blocks.sprites()[-1].rect = new_rect

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # The left mouse button released
                # Clear the mouse-down position to end the drag operation
                self.mouse_down_pos = None

    def save_level(self):
        # Save block data as JSON
        with open("levels/level.json", "w") as f:
            data = {
                "blocks": [
                    {
                        "x": block.rect.x,
                        "y": block.rect.y,
                        "width": block.rect.width,
                        "height": block.rect.height,
                        "color": block.color
                    }
                    for block in self.blocks
                ],
                "players": [
                    {
                        "name": player.name,
                        "x": player.x,
                        "y": player.y,
                        "health": player.health
                    }
                    for player in self.players
                ],
            }
            json.dump(data, f, indent=4)

        print("Level saved to level.json")

    def load_level(self):
        # Load block data from JSON
        with open("levels/level.json", "r") as f:
            data = json.load(f)
            self.blocks.empty()
            for block_data in data["blocks"]:
                block = Block(pygame.Rect(block_data["x"], block_data["y"], block_data["width"], block_data["height"]))
                block.color = block_data["color"]
                block.add(self.blocks)
            for player_data in data["players"]:
                pass

        print("Level loaded from level.json")

    def handle_events(self, events):
        for event in events:
            self.camera.handle_event_input(event)
            self._handle_block_editing(event)

            if event.type == pygame.QUIT:
                self.next_transition = StateTransition("quit")

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.next_transition = StateTransition("push", "menu", {"submenu": "pause"})

                if event.key == pygame.K_k:
                    self.save_level()
                if event.key == pygame.K_l:
                    self.load_level()

    def update(self, delta_time):
        self.camera.handle_frame_input()

    def render(self, screen):

        self.render_surface.fill("light pink")
        for block in self.blocks:
            pygame.draw.rect(self.render_surface, block.color, block.rect)

        self.camera.render(screen, self.render_surface)
