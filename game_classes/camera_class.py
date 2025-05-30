import pygame

# This camera class allows for a game to be drawn on a separate surface and viewed through the window via this camera.
# Requires handle_input() (every frame) and handle_zoom() (on mouse scroll event)



class Camera:
    def __init__(self, screen_size, controls=dict(up=pygame.K_UP, down=pygame.K_DOWN, left=pygame.K_LEFT, right=pygame.K_RIGHT)):
        self.x = 0
        self.y = 0
        self.speed = 10
        self.zoom = 1.222
        self.min_zoom = 0.3
        self.max_zoom = 10
        self.pan_start_location = None

        self.screen_size = screen_size

        self.controls = controls

    def game_pos_to_screen(self, pos):
        """Convert game position to screen position"""
        return pos[0] * self.zoom - self.x, pos[1] * self.zoom - self.y

    def screen_pos_to_game(self, pos):
        """Convert screen position to game position"""
        return (pos[0] + self.x * self.zoom) / self.zoom, (pos[1] + self.y * self.zoom) / self.zoom

    def move_center_to(self, dest_pos):
        center_pos = self.screen_pos_to_game((self.screen_size[0] / 2, self.screen_size[1] / 2))
        self.x -= center_pos[0] - dest_pos[0]
        self.y -= center_pos[1] - dest_pos[1]

    def handle_event_input(self, event):
        if event.type == pygame.MOUSEWHEEL:
            mouse_pos = pygame.mouse.get_pos()
            before = self.screen_pos_to_game(mouse_pos)

            if event.y > 0:
                self.zoom *= 1.1
            elif event.y < 0:
                self.zoom /= 1.1

            self.zoom = max(self.min_zoom, min(self.max_zoom, self.zoom))

            after = self.screen_pos_to_game(mouse_pos)

            # Adjust the camera position so that the point under the mouse stays stable
            self.x -= (after[0] - before[0])
            self.y -= (after[1] - before[1])

        # Panning is the same regardless of zoom as relies solely on mouse position
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 2:  # Middle mouse button
                self.pan_start_location = event.pos

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 2:
                self.pan_start_location = None

        if event.type == pygame.MOUSEMOTION:
            if self.pan_start_location:
                # Calculate the new camera position based on mouse movement and zoom level
                self.x -= event.rel[0] / self.zoom
                self.y -= event.rel[1] / self.zoom

    def handle_frame_input(self):
        keys = pygame.key.get_pressed()
        if keys[self.controls["up"]]:
            self.y -= self.speed
        if keys[self.controls["down"]]:
            self.y += self.speed
        if keys[self.controls["left"]]:
            self.x -= self.speed
        if keys[self.controls["right"]]:
            self.x += self.speed
