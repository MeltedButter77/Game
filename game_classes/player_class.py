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

    def calc_next_pos(self, blocks, render_surface):
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

        for block in blocks:
            if self.future_rect.colliderect(block.rect):
                dx = self.future_rect.centerx - self.rect.centerx
                dy = self.future_rect.centery - self.rect.centery

                # Calculate overlaps
                overlap_left = abs(self.rect.right - block.rect.left)
                overlap_right = abs(self.rect.left - block.rect.right)
                overlap_top = abs(self.rect.bottom - block.rect.top)
                overlap_bottom = abs(self.rect.top - block.rect.bottom)

                horizontal_overlap = min(overlap_left, overlap_right)
                vertical_overlap = min(overlap_top, overlap_bottom)
                print(horizontal_overlap, vertical_overlap)

                if horizontal_overlap < vertical_overlap:
                    # Resolve horizontal
                    if dx > 0:
                        self.future_rect.right = block.rect.left
                    elif dx < 0:
                        self.future_rect.left = block.rect.right
                    self.velocity.x = 0
                else:
                    # Resolve vertical
                    if dy > 0:
                        self.future_rect.bottom = block.rect.top
                    elif dy < 0:
                        self.future_rect.top = block.rect.bottom
                    self.velocity.y = 0

        # After adjustments, update location
        self.location = pygame.Vector2(self.future_rect.topleft)

    def apply_next_pos(self):
        self.rect = self.future_rect.copy()
