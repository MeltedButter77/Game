import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, rect):
        super().__init__()

        # === Core Sprite Attributes ===
        self.rect = rect
        self.image = pygame.Surface(rect.size)
        self.future_rect = rect.copy()  # Used for collision prediction or pathing

        # === Static Player Settings ===
        self.speed = 10  # Movement speed
        self.gravity = pygame.Vector2(0, 1)  # Default gravity direction (down)
        self.flying = False  # If True, disables gravity (free movement)

        self.input_handler = None

        # Key mappings chosen by player (customizable)
        self.selected_controls = {
            "up": pygame.K_w,
            "down": pygame.K_s,
            "left": pygame.K_a,
            "right": pygame.K_d
        }

        # === Dynamic State ===
        self.location = pygame.Vector2(rect.x, rect.y)  # Sub-pixel location tracking
        self.velocity = pygame.Vector2(0, 0)  # Current movement vector
        self.on_ground = False  # For gravity/jumping logic

        # === Derived Setup (Depends on Previous Attributes) ===

        # Validate gravity direction
        if abs(self.gravity.y) > 0 and abs(self.gravity.x) > 0:
            print("Error: Gravity must be horizontal, vertical or zero, not diagonal.")
            exit(1)
        # Normalize gravity; consistent across all players
        if self.gravity.length() > 1:
            self.gravity.normalize()

        # Disable gravity if flying
        if self.flying:
            self.gravity = pygame.Vector2(0, 0)

        # === Control Mapping Based on Gravity ===
        if self.flying:
            # Free movement – direct mapping
            self.controls = {
                "up": self.selected_controls["up"],
                "down": self.selected_controls["down"],
                "left": self.selected_controls["left"],
                "right": self.selected_controls["right"]
            }
        elif self.gravity.y < 0:
            # Gravity pulls upward – jump is down key
            self.controls = {
                "jump": self.selected_controls["down"],
                "down": self.selected_controls["up"],
                "left": self.selected_controls["left"],
                "right": self.selected_controls["right"]
            }
        elif self.gravity.y > 0:
            # Gravity pulls downward – jump is up key
            self.controls = {
                "jump": self.selected_controls["up"],
                "down": self.selected_controls["down"],
                "left": self.selected_controls["left"],
                "right": self.selected_controls["right"]
            }
        elif self.gravity.x < 0:
            # Gravity pulls left – jump is right key
            self.controls = {
                "jump": self.selected_controls["right"],
                "down": self.selected_controls["left"],
                "left": self.selected_controls["up"],
                "right": self.selected_controls["down"]
            }
        elif self.gravity.x > 0:
            # Gravity pulls right – jump is left key
            self.controls = {
                "jump": self.selected_controls["left"],
                "down": self.selected_controls["right"],
                "left": self.selected_controls["up"],
                "right": self.selected_controls["down"]
            }

    def calc_next_pos(self, sprites):
        self.velocity += self.gravity

        keys = pygame.key.get_pressed()
        if self.gravity:
            if keys[self.controls["jump"]] and self.on_ground:
                if abs(self.gravity.y) > 0:
                    self.velocity.y = -self.speed * self.gravity.y
                else:
                    self.velocity.x = -self.speed * self.gravity.x
            if keys[self.controls["right"]]:
                if abs(self.gravity.y) > 0:
                    self.location.x += self.speed
                else:
                    self.location.y += self.speed
            if keys[self.controls["left"]]:
                if abs(self.gravity.y) > 0:
                    self.location.x += -self.speed
                else:
                    self.location.y += -self.speed

        elif self.flying:
            if keys[self.controls["up"]]:
                self.location.y += -self.speed
            if keys[self.controls["down"]]:
                self.location.y += self.speed
            if keys[self.controls["right"]]:
                self.location.x += self.speed
            if keys[self.controls["left"]]:
                self.location.x += -self.speed

        # Update location
        self.location.x += self.velocity.x
        self.location.y += self.velocity.y

        # Move future_rect to location
        self.future_rect.topleft = self.location

        # Loop checking collisions with blocks with updated future_rect. This prevents the order of blocks being checked from affecting the result
        rect_list = [sprite.rect for sprite in sprites]
        while self.future_rect.collidelist(rect_list) >= 0 and self.future_rect.topleft != self.rect.topleft:
            dx = self.future_rect.centerx - self.rect.centerx
            dy = self.future_rect.centery - self.rect.centery

            # Use independent rects for each axis
            future_rect_x = self.future_rect.copy()
            future_rect_x.y = self.rect.y  # Rect with only x offset
            future_rect_y = self.future_rect.copy()
            future_rect_y.x = self.rect.x  # Rect with only y offset

            # Start looping over block rects
            for collision_rect in rect_list:
                # Check if the future_rect collides with the current block
                if self.future_rect.colliderect(collision_rect):
                    # If neither axis is colliding, we cannot handle them separately.
                    # This approach steps back the future_rect perfectly diagonally (until one axis aligns with rect x or y, then future rect moves along one axis).
                    # The above line may be cut short if any step of future_rect is not colliding.
                    if not future_rect_x.colliderect(collision_rect) and not future_rect_y.colliderect(collision_rect):
                        for i in range(max(abs(dx), abs(dy))):
                            # Check collision to see if we can stop stepping back here
                            if self.future_rect.colliderect(collision_rect):
                                self.velocity = pygame.Vector2(0, 0)  # Reset velocity
                                # move future rect toward rect by 1
                                dx, dy = self.future_rect.centerx - self.rect.centerx, self.future_rect.centery - self.rect.centery
                                if dx != 0:
                                    self.future_rect.x -= dx // abs(dx)
                                if dy != 0:
                                    self.future_rect.y -= dy // abs(dy)
                        continue

                    # If one axis is colliding, we can handle it separately.
                    # This approach steps back the future_rect perfectly along one axis until it meets rect or is not colliding anymore.
                    for i in range(abs(dx)):
                        # Check collision first because this axis may not be colliding at all
                        if future_rect_x.colliderect(collision_rect):
                            self.velocity.x = 0  # Reset velocity
                            # move future rect toward rect by 1
                            dx = future_rect_x.centerx - self.rect.centerx
                            if dx != 0:
                                future_rect_x.x -= dx // abs(dx)
                    # Repeat for y
                    for i in range(abs(dy)):
                        if future_rect_y.colliderect(collision_rect):
                            self.velocity.y = 0
                            dy = future_rect_y.centery - self.rect.centery
                            if dy != 0:
                                future_rect_y.y -= dy // abs(dy)

                    # Update player's future_rect
                    self.future_rect.topleft = (future_rect_x.x, future_rect_y.y)

                    # Restart checking collisions with blocks once future_rect has been updated
                    # because all calcs for previous blocks are now outdated.
                    break

        # After adjustments, update location
        self.location = pygame.Vector2(self.future_rect.topleft)

        # === Update on_ground status based on gravity ===
        self.on_ground = False  # Reset to default
        if not self.flying:
            check_offset = pygame.Vector2(self.gravity).normalize()
            check_rect = self.rect.move(round(check_offset.x), round(check_offset.y))

            for sprite in sprites:
                if check_rect.colliderect(sprite.rect):
                    self.on_ground = True
                    break

    def apply_next_pos(self):
        self.rect = self.future_rect.copy()
