import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, position, size):
        """Initialize a Player sprite with movement, gravity and input handling capabilities.
        
        Args:
            position: Initial (x,y) position tuple
            size: (width, height) tuple for sprite size
        """
        super().__init__()

        # === Core Sprite Attributes ===
        self.image = pygame.image.load("assets/player.png")  # .convert_alpha()
        self.image = pygame.transform.scale(self.image, size)
        self.unrotated_image = self.image.copy()
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.display_rect = self.image.get_rect()
        self.future_rect = self.rect.copy()  # Used for collision prediction or pathing

        # === Static Player Settings ===
        self.speed = 10  # Movement speed
        self.update_gravity_direction("down")
        self.debug = False  # Toggle collision box visualization

        # === Input Handling ===
        self.input_handler = None
        self.controls = None

        # === Dynamic State ===
        self.location = pygame.Vector2(self.rect.x, self.rect.y)  # Sub-pixel location tracking
        self.velocity = pygame.Vector2(0, 0)  # Current movement vector
        self.on_ground = False  # For gravity/jumping logic

        # === Debugging ===
        self.debug = False

    def is_flying(self):
        return self.gravity.length() == 0

    def update_gravity_direction(self, direction=None):
        """Update gravity direction and adjust collision rectangles accordingly."""
        # Reset collision rect sizes
        if hasattr(self, "gravity"):
            if self.gravity.x == 0:
                self.rect.width += 20
                self.future_rect.width += 20
            if self.gravity.y == 0:
                self.rect.height += 20
                self.future_rect.height += 20

        # Set gravity vector based on direction
        gravity_vectors = {
            "up": (0, -1),
            "down": (0, 1),
            "left": (-1, 0),
            "right": (1, 0),
            None: (0, 0)
        }
        self.gravity = pygame.Vector2(*gravity_vectors.get(direction, (0, 0)))

        # Validate gravity direction
        if abs(self.gravity.y) > 0 and abs(self.gravity.x) > 0:
            print("Error: Gravity must be horizontal, vertical or zero, not diagonal.")
            exit(1)
        if self.gravity.length() > 1:
            self.gravity.normalize()

        # Update image rotation
        if self.gravity.x < 0:
            self.image = pygame.transform.rotate(self.unrotated_image, -90)
        elif self.gravity.x > 0:
            self.image = pygame.transform.rotate(self.unrotated_image, 90)
        elif self.gravity.y < 0:
            self.image = pygame.transform.flip(self.unrotated_image, False, True)
        elif self.gravity.y > 0:
            self.image = pygame.transform.flip(self.unrotated_image, False, False)

        # Update collision rect
        if self.gravity.x == 0:
            self.rect.width -= 20
            self.future_rect.width -= 20
        if self.gravity.y == 0:
            self.rect.height -= 20
            self.future_rect.height -= 20

    def load_controls(self):
        # Loads self.controls based on input handler and gravity
        # Basically sets each bind (the keys) to a key value chosen by the input handler
        if self.input_handler is None:
            return

        if self.input_handler == "keyboard":
            if self.is_flying():
                # Free movement – direct mapping
                self.controls = {
                    "jump": self.input_handler.key_binds["jump"],
                    "up": self.input_handler.key_binds["up"],
                    "down": self.input_handler.key_binds["down"],
                    "left": self.input_handler.key_binds["left"],
                    "right": self.input_handler.key_binds["right"]
                }
            elif self.gravity.y < 0:
                # Gravity pulls upward – jump is down key
                self.controls = {
                    "jump": self.input_handler.key_binds["jump"],
                    "up": self.input_handler.key_binds["down"],
                    "down": self.input_handler.key_binds["up"],
                    "left": self.input_handler.key_binds["left"],
                    "right": self.input_handler.key_binds["right"]
                }
            elif self.gravity.y > 0:
                # Gravity pulls downward – jump is up key
                self.controls = {
                    "jump": self.input_handler.key_binds["jump"],
                    "up": self.input_handler.key_binds["up"],
                    "down": self.input_handler.key_binds["down"],
                    "left": self.input_handler.key_binds["left"],
                    "right": self.input_handler.key_binds["right"]
                }
            elif self.gravity.x < 0:
                # Gravity pulls left – jump is right key
                self.controls = {
                    "jump": self.input_handler.key_binds["jump"],
                    "up": self.input_handler.key_binds["right"],
                    "down": self.input_handler.key_binds["left"],
                    "left": self.input_handler.key_binds["up"],
                    "right": self.input_handler.key_binds["down"]
                }
            elif self.gravity.x > 0:
                # Gravity pulls right – jump is left key
                self.controls = {
                    "jump": self.input_handler.key_binds["jump"],
                    "up": self.input_handler.key_binds["left"],
                    "down": self.input_handler.key_binds["right"],
                    "left": self.input_handler.key_binds["up"],
                    "right": self.input_handler.key_binds["down"]
                }

        elif self.input_handler and self.input_handler.controller != "keyboard":
            if self.is_flying():
                # Free movement – direct mapping
                self.controls = {
                    "jump": self.input_handler.key_binds["jump"],
                    "up": self.input_handler.key_binds["left_y_axis"],
                    "down": self.input_handler.key_binds["left_y_axis"],
                    "left": self.input_handler.key_binds["left_x_axis"],
                    "right": self.input_handler.key_binds["left_x_axis"]
                }
            elif self.gravity.y < 0:
                # Gravity pulls upward – jump is down key
                self.controls = {
                    "jump": self.input_handler.key_binds["jump"],
                    "up": self.input_handler.key_binds["left_y_axis"],
                    "down": self.input_handler.key_binds["left_y_axis"],
                    "left": self.input_handler.key_binds["left_x_axis"],
                    "right": self.input_handler.key_binds["left_x_axis"]
                }
            elif self.gravity.y > 0:
                # Gravity pulls downward – jump is up key
                self.controls = {
                    "jump": self.input_handler.key_binds["jump"],
                    "up": self.input_handler.key_binds["left_y_axis"],
                    "down": self.input_handler.key_binds["left_y_axis"],
                    "left": self.input_handler.key_binds["left_x_axis"],
                    "right": self.input_handler.key_binds["left_x_axis"]
                }
            elif self.gravity.x < 0:
                # Gravity pulls left – jump is right key
                self.controls = {
                    "jump": self.input_handler.key_binds["jump"],
                    "up": self.input_handler.key_binds["left_x_axis"],
                    "down": self.input_handler.key_binds["left_x_axis"],
                    "left": self.input_handler.key_binds["left_y_axis"],
                    "right": self.input_handler.key_binds["left_y_axis"]
                }
            elif self.gravity.x > 0:
                # Gravity pulls right – jump is left key
                self.controls = {
                    "jump": self.input_handler.key_binds["jump"],
                    "up": self.input_handler.key_binds["left_x_axis"],
                    "down": self.input_handler.key_binds["left_x_axis"],
                    "left": self.input_handler.key_binds["left_y_axis"],
                    "right": self.input_handler.key_binds["left_y_axis"]
                }

    def apply_input(self):
        if not self.input_handler:
            return
        if not self.controls:
            # Load controls based on input handler and gravity
            self.load_controls()

        keys = self.input_handler.get_input()

        if self.gravity:
            if keys["jump"] and self.on_ground:
                if abs(self.gravity.y) > 0:
                    self.velocity.y = -self.speed * self.gravity.y
                else:
                    self.velocity.x = -self.speed * self.gravity.x
            if keys["right"]:
                if abs(self.gravity.y) > 0:
                    self.location.x += self.speed
                else:
                    self.location.y += self.speed
            if keys["left"]:
                if abs(self.gravity.y) > 0:
                    self.location.x += -self.speed
                else:
                    self.location.y += -self.speed

        elif self.is_flying():
            if keys["up"]:
                self.location.y += -self.speed
            if keys["down"]:
                self.location.y += self.speed
            if keys["right"]:
                self.location.x += self.speed
            if keys["left"]:
                self.location.x += -self.speed

    def calc_next_pos(self, sprites):
        self.velocity += self.gravity

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
        if not self.is_flying():
            check_offset = pygame.Vector2(self.gravity).normalize()
            check_rect = self.rect.move(round(check_offset.x), round(check_offset.y))

            for sprite in sprites:
                if check_rect.colliderect(sprite.rect):
                    self.on_ground = True
                    break

    def apply_next_pos(self):
        self.rect = self.future_rect.copy()

    def draw(self, surface, camera):
        self.display_rect.center = self.rect.center
        adjusted_display_rect = pygame.Rect(
            (self.display_rect.x - camera.x) * camera.zoom,
            (self.display_rect.y - camera.y) * camera.zoom,
            self.display_rect.width * camera.zoom,
            self.display_rect.height * camera.zoom
        )
        scaled_image = pygame.transform.scale(self.image, adjusted_display_rect.size)
        surface.blit(scaled_image, adjusted_display_rect)

        if self.debug:
            adjusted_collision_rect = pygame.Rect(
                (self.rect.x - camera.x) * camera.zoom,
                (self.rect.y - camera.y) * camera.zoom,
                self.rect.width * camera.zoom,
                self.rect.height * camera.zoom
            )
            pygame.draw.rect(surface, (0, 0, 0), adjusted_collision_rect, 1)
