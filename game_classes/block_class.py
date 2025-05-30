import pygame
import os


class Block(pygame.sprite.Sprite):
    def __init__(self, grid_size, rect):
        super().__init__()
        self.color = "blue"
        self.rect = rect
        self.grid_size = grid_size

        self.color_map = {
            "blue": (70, 90, 140),
            "red": (150, 60, 60),
            "green": (80, 120, 80),
            "yellow": (200, 180, 100),
            "orange": (200, 130, 70),
            "purple": (100, 70, 120),
            "cyan": (100, 160, 160),
            "white": (240, 240, 240),
            "black": (20, 20, 20),
            "gray": (100, 100, 100),
            "magenta": (160, 90, 130)
        }

        self.image = pygame.Surface(self.rect.size).convert_alpha()
        self.image.fill((0, 0, 0, 0))  # Transparent background

        # Load base images
        base_images = {
            "corner": "assets/tiles/corner.png",
            "edge": "assets/tiles/edge.png",
            "center": "assets/tiles/center.png"
        }

        self.images = {}

        # Define how to derive each tile from the base image and its rotation
        tile_variants = {
            "top-left": ("corner", 0),
            "top": ("edge", 0),
            "top-right": ("corner", -90),
            "left": ("edge", 90),
            "center": ("center", 0),
            "right": ("edge", -90),
            "bottom-left": ("corner", 90),
            "bottom": ("edge", 180),
            "bottom-right": ("corner", 180),
        }

        # Load and transform images
        for tile_name, (base_name, rotation) in tile_variants.items():
            path = base_images[base_name]
            if os.path.exists(path):
                image = pygame.image.load(path).convert_alpha()
                image = pygame.transform.scale(image, (self.grid_size, self.grid_size))
                if rotation != 0:
                    image = pygame.transform.rotate(image, rotation)
                image.fill(self.color_map[self.color], special_flags=pygame.BLEND_RGBA_MULT)
                self.images[tile_name] = image
            else:
                print(f"Base image '{path}' not found. Using placeholder for '{tile_name}'.")
                placeholder = pygame.Surface((self.grid_size, self.grid_size), pygame.SRCALPHA).convert_alpha()
                placeholder.fill((255, 0, 0, 128))
                self.images[tile_name] = placeholder

        self.update_image()

    def update_image(self):
        self.image = pygame.Surface(self.rect.size).convert_alpha()
        self.image.fill((0, 0, 0, 0))  # Transparent background

        tiles_x = self.rect.width // self.grid_size
        tiles_y = self.rect.height // self.grid_size

        for i in range(tiles_x):
            for j in range(tiles_y):
                x = i * self.grid_size
                y = j * self.grid_size

                at_left = (i == 0)
                at_right = (i == tiles_x - 1)
                at_top = (j == 0)
                at_bottom = (j == tiles_y - 1)

                if at_top and at_left:
                    tile = self.images["top-left"]
                elif at_top and at_right:
                    tile = self.images["top-right"]
                elif at_bottom and at_left:
                    tile = self.images["bottom-left"]
                elif at_bottom and at_right:
                    tile = self.images["bottom-right"]
                elif at_top:
                    tile = self.images["top"]
                elif at_bottom:
                    tile = self.images["bottom"]
                elif at_left:
                    tile = self.images["left"]
                elif at_right:
                    tile = self.images["right"]
                else:
                    tile = self.images["center"]

                self.image.blit(tile, (x, y))

    def draw(self, surface, camera):
        zoomed_rect = pygame.Rect(
            (self.rect.x - camera.x) * camera.zoom,
            (self.rect.y - camera.y) * camera.zoom,
            self.rect.width * camera.zoom,
            self.rect.height * camera.zoom
        )
        scaled_image = pygame.transform.scale(self.image, zoomed_rect.size)
        surface.blit(scaled_image, zoomed_rect)
