import math
import json
import pygame
from game_classes.camera_class import Camera
from game_states.state_helpers import BaseState, StateTransition, load_level
from game_classes.block_class import Block


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

        self.mouse_down_pos = None
        self.level_info = None

        self.game_sprites = {
            "blocks": pygame.sprite.Group(),
            "players": pygame.sprite.Group()
        }

    def _handle_block_editing(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.next_state = "pause_game"

        # TODO: Fix rounding of positions and sizes when creating new blocks

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:  # Right mouse button pressed
                block_under_mouse = [block for block in self.game_sprites["blocks"] if block.rect.collidepoint(self.camera.screen_pos_to_game(event.pos))]
                if block_under_mouse:
                    self.game_sprites["blocks"].remove(block_under_mouse[0])

            if event.button == 1:  # Left mouse button pressed
                # Convert screen position to game coordinates
                self.mouse_down_pos = self.camera.screen_pos_to_game(event.pos)

                # Snap the position down to the nearest 10 (grid alignment)
                self.mouse_down_pos = (
                    math.floor(self.mouse_down_pos[0] / 10) * 10,
                    math.floor(self.mouse_down_pos[1] / 10) * 10
                )

                # Create a new 10x10 block at the snapped mouse-down position
                Block(pygame.Rect(self.mouse_down_pos, (10, 10))).add(self.game_sprites["blocks"])

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
                self.game_sprites["blocks"].sprites()[-1].rect = new_rect
                self.game_sprites["blocks"].sprites()[-1].update_image()  # Updates size of image to match new rect

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # The left mouse button released
                # Clear the mouse-down position to end the drag operation
                self.mouse_down_pos = None

    def save_level(self):

        # read from saved_count.txt
        try:
            with open("levels/saved_count.txt", "r") as f:
                level_count = int(f.read())
        except FileNotFoundError:
            level_count = 0
            # create saved_count.txt
            with open("levels/saved_count.txt", "w") as f:
                f.write(str(int(level_count + 1)))
        # Add one to the saved_count.txt
        with open("levels/saved_count.txt", "w") as f:
            f.write(str(int(level_count + 1)))

        # Save block data as JSON
        location = f"levels/saved/saved_level_{level_count}.json"
        if self.level_info:
            location = f"levels/{self.level_info['player_count']}_players/world_{self.level_info['world']}/level_{self.level_info['level']}.json"

        with open(location, "w") as f:
            data = {
                "blocks": [
                    {
                        "x": block.rect.x,
                        "y": block.rect.y,
                        "width": block.rect.width,
                        "height": block.rect.height,
                        "color": "blue"
                    }
                    for block in self.game_sprites["blocks"]
                ],
                "players": [
                    {
                        "x": player.rect.x,
                        "y": player.rect.y,
                        "width": player.rect.width,
                        "height": player.rect.height,
                        "color": "red"
                    }
                    for player in self.game_sprites["players"]
                ],
            }
            json.dump(data, f, indent=4)

        print(f"Level saved to " + location)

    def load_level(self, player_count, world, level):
        self.level_info = {"player_count": player_count, "world": world, "level": level}
        load_level(self, player_count, world, level)

    def handle_events(self, events):
        for event in events:
            self.camera.handle_event_input(event)
            self._handle_block_editing(event)

            if event.type == pygame.QUIT:
                self.next_transitions = [StateTransition("quit")]

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.next_transitions = [StateTransition("push", "menu", {"submenu": "editor_pause"})]

    def update(self, delta_time):
        self.camera.handle_frame_input()

    def render(self, screen):
        screen.fill("light pink")
        for object_group in self.game_sprites.values():
            for sprite in object_group.sprites():
                screen.blit(sprite.image, sprite.rect.copy().move(-self.camera.x, -self.camera.y))
