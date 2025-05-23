import pygame


class Block(pygame.sprite.Sprite):
    def __init__(self, rect):
        super().__init__()
        self.color = "blue"
        self.rect = rect

        self.image = pygame.Surface(rect.size)
        self.image.fill(self.color)
