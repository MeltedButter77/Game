import math
import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, position, color, gravity="down"):
        """Initialize a Player sprite with movement, gravity and input handling capabilities.
        
        Args:
            position: Initial (x,y) position tuple
            size: (width, height) tuple for sprite size
        """
        super().__init__()
        image_size = (32, 32)

        # === Core Sprite Attributes ===
        self.image = pygame.image.load("assets/player.png")  # .convert_alpha()
        self.image = pygame.transform.scale(self.image, image_size)
        self.unrotated_image = self.image.copy()

        self.collision_box_size = pygame.Vector2((image_size[0], image_size[1] * 2 / 3))  # base size for collision rects
        self.rect = pygame.Rect((0, 0), self.collision_box_size)
        self.rect.center = position
        self.future_rect = self.rect.copy()  # Used for collision prediction or pathing

        # === Static Player Settings ===
        self.speed = 180  # Movement speed
        self.jump_power = 320  # Jump height
        self.gravity_strength = 1300
        self.color = color

        # === Input Handling ===
        self.input_handler = None
        self.controls = None

        # === Gravity ===
        self.update_gravity_direction(gravity)  # Will change controls and collision rects'

        # === Dynamic State ===
        self.location = pygame.Vector2(self.rect.x, self.rect.y)  # Sub-pixel location tracking
        self.velocity = pygame.Vector2(0, 0)  # Current movement vector
        self.on_ground = False  # For gravity/jumping logic

    def is_flying(self):
        return self.gravity.length() == 0

    def update_gravity_direction(self, direction=None):
        gravity_vectors = {
            "up": (0, -self.gravity_strength),
            "down": (0, self.gravity_strength),
            "left": (-self.gravity_strength, 0),
            "right": (self.gravity_strength, 0),
            None: (0, 0)
        }

        self.gravity = pygame.Vector2(*gravity_vectors.get(direction, (0, 0)))

        if abs(self.gravity.x) > 0 and abs(self.gravity.y) > 0:
            raise ValueError("Gravity must be horizontal, vertical, or zero, not diagonal.")
        if self.gravity.length_squared() > self.gravity_strength:
            self.gravity = self.gravity.normalize() * self.gravity_strength

        # Handle rotation
        if self.gravity.x < 0:  # Left
            self.image = pygame.transform.rotate(self.unrotated_image, -90)
        elif self.gravity.x > 0:  # Right
            self.image = pygame.transform.rotate(self.unrotated_image, 90)
        elif self.gravity.y < 0:  # Up
            self.image = pygame.transform.flip(self.unrotated_image, False, True)
        elif self.gravity.y > 0:  # Down
            self.image = self.unrotated_image.copy()

        # Set proper collision box dimensions based on gravity
        width, height = self.collision_box_size
        if self.gravity.x == 0:  # Horizontal gravity -> wider hitbox
            width, height = height, width

        # Preserve center position when adjusting rect
        old_center = self.rect.center
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = old_center
        self.future_rect = self.rect.copy()

    def apply_input(self, delta_time):
        if not self.input_handler:
            return

        inputs = self.input_handler.get_input()
        if not inputs:
            return

        # Rotate inputs for gravity for controller players
        if not isinstance(self.input_handler.joystick, str):
            if self.gravity.x != 0 and self.gravity is not None:
                inputs["left"], inputs["right"] = inputs["up"], inputs["down"]

        if self.gravity:
            if inputs["jump"] and self.on_ground:
                if abs(self.gravity.y) > 0:
                    self.velocity.y = -self.jump_power * math.copysign(1, self.gravity.y)
                else:
                    self.velocity.x = -self.jump_power * math.copysign(1, self.gravity.x)
            # Handle horizontal movement with priority to the first pressed direction
            if inputs["right"] and not inputs["left"]:
                if abs(self.gravity.y) > 0:
                    self.location.x += self.speed * delta_time
                else:
                    self.location.y += self.speed * delta_time
            elif inputs["left"] and not inputs["right"]:
                if abs(self.gravity.y) > 0:
                    self.location.x -= self.speed * delta_time
                else:
                    self.location.y -= self.speed * delta_time

        elif self.is_flying():
            # Handle vertical movement with priority to the first pressed direction
            if inputs["up"] and not inputs["down"]:
                self.location.y -= self.speed * delta_time
            elif inputs["down"] and not inputs["up"]:
                self.location.y += self.speed * delta_time

            # Handle horizontal movement with priority to the first pressed direction
            if inputs["right"] and not inputs["left"]:
                self.location.x += self.speed * delta_time
            elif inputs["left"] and not inputs["right"]:
                self.location.x -= self.speed * delta_time

    def calc_next_pos(self, delta_time, sprites):
        self.velocity += self.gravity * delta_time

        # Update location
        self.location.x += self.velocity.x * delta_time
        self.location.y += self.velocity.y * delta_time

        # Move future_rect to location using math.floor for consistent rounding
        self.future_rect.topleft = (round(self.location.x), round(self.location.y))

        # Filter nearby rects and cache calculations for better performance
        search_rect = self.future_rect.inflate(self.rect.width * 2, self.rect.height * 2)
        rect_list = [sprite.rect for sprite in sprites if sprite != self and search_rect.colliderect(sprite.rect)]

        if not rect_list:  # Quick exit if no nearby collisions
            return

        while self.future_rect.collidelist(rect_list) >= 0 and self.future_rect.topleft != self.rect.topleft:
            dx = self.future_rect.centerx - self.rect.centerx
            dy = self.future_rect.centery - self.rect.centery

            # Binary search to find closest non-colliding position (this aims to improve efficiency)
            test_rect = self.future_rect.copy()
            step_x = dx // 2
            step_y = dy // 2
            while abs(step_x) > 1 or abs(step_y) > 1:
                test_rect.centerx = self.rect.centerx + step_x
                test_rect.centery = self.rect.centery + step_y

                if not test_rect.collidelist(rect_list) >= 0:
                    self.future_rect = test_rect.copy()
                    dx = step_x
                    dy = step_y

                step_x //= 2
                step_y //= 2

            # Use independent rects for final adjustments
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
                    # This approach is more efficient than the one below but less ideal. For example, y movement would be reduced when hitting a vertical wall.
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

            for rect in rect_list:
                if check_rect.colliderect(rect):
                    self.on_ground = True
                    break

    def apply_next_pos(self):
        self.rect = self.future_rect.copy()

    def get_display_rect(self, camera):
        return pygame.Rect(
            (self.image.get_rect(center=self.rect.center).x - camera.x) * camera.zoom,
            (self.image.get_rect(center=self.rect.center).y - camera.y) * camera.zoom,
            self.image.get_width() * camera.zoom,
            self.image.get_height() * camera.zoom
        )

    def draw(self, surface, camera):
        scaled_image = pygame.transform.scale(self.image, self.get_display_rect(camera).size)
        surface.blit(scaled_image, self.get_display_rect(camera))
