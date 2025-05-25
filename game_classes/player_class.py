import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, rect):
        super().__init__()
        self.rect = rect
        self.future_rect = rect.copy()

        self.image = pygame.Surface(rect.size)

        self.speed = 10
        self.location = pygame.Vector2(rect.x, rect.y)
        self.velocity = pygame.Vector2(0, 0)

        self.gravity = 1

    def calc_next_pos(self, blocks):
        self.velocity.y += self.gravity

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.velocity.y = -self.speed
        if keys[pygame.K_d]:
            self.location.x += self.speed
        if keys[pygame.K_a]:
            self.location.x += -self.speed

        # Update location
        self.location.x += self.velocity.x
        self.location.y += self.velocity.y

        # Move future_rect to location
        self.future_rect.topleft = self.location

        # Loop checking collisions with blocks with updated future_rect. This prevents the order of blocks being checked from affecting the result
        block_rects = [block.rect for block in blocks]
        while self.future_rect.collidelist(block_rects) >= 0 and self.future_rect.topleft != self.rect.topleft:
            dx = self.future_rect.centerx - self.rect.centerx
            dy = self.future_rect.centery - self.rect.centery

            # Use independent rects for each axis
            future_rect_x = self.future_rect.copy()
            future_rect_x.y = self.rect.y  # Rect with only x offset
            future_rect_y = self.future_rect.copy()
            future_rect_y.x = self.rect.x  # Rect with only y offset

            # Start looping over blocks
            for block in blocks:
                # Check if the future_rect collides with the current block
                if self.future_rect.colliderect(block.rect):
                    # If neither axis is colliding, we cannot handle them separately.
                    # This approach steps back the future_rect perfectly diagonally (until one axis aligns with rect x or y, then future rect moves along one axis).
                    # The above line may be cut short if any step of future_rect is not colliding.
                    if not future_rect_x.colliderect(block.rect) and not future_rect_y.colliderect(block.rect):
                        for i in range(max(abs(dx), abs(dy))):
                            # Check collision to see if we can stop stepping back here
                            if self.future_rect.colliderect(block.rect):
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
                        if future_rect_x.colliderect(block.rect):
                            self.velocity.x = 0  # Reset velocity
                            # move future rect toward rect by 1
                            dx = future_rect_x.centerx - self.rect.centerx
                            if dx != 0:
                                future_rect_x.x -= dx // abs(dx)
                    # Repeat for y
                    for i in range(abs(dy)):
                        if future_rect_y.colliderect(block.rect):
                            self.velocity.y = 0
                            dy = future_rect_y.centery - self.rect.centery
                            if dy != 0:
                                future_rect_y.y -= dy // abs(dy)

                    # Update player's future_rect
                    self.future_rect.topleft = (future_rect_x.x, future_rect_y.y)
                    print(self.future_rect.topleft)

                    # Restart checking collisions with blocks once future_rect has been updated
                    # because all calcs for previous blocks are now outdated.
                    break

        # After adjustments, update location
        self.location = pygame.Vector2(self.future_rect.topleft)

    def apply_next_pos(self):
        self.rect = self.future_rect.copy()
