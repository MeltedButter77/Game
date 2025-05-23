import pygame
from game_states.state_helpers import BaseState, StateTransition, load_level
from game_classes.camera_class import Camera


class GameState(BaseState):
    def __init__(self, context):
        super().__init__(context)
        self.camera = Camera()
        world_width, world_height = 10000, 10000
        self.render_surface = pygame.Surface((world_width, world_height))

        self.game_sprites = {
            "blocks": pygame.sprite.Group(),
            "players": pygame.sprite.Group()
        }

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.next_transitions = [StateTransition("quit")]

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.next_transitions = [StateTransition("push", "menu", {"submenu": "game_pause"})]

    def load_level(self, player_count, world, level):
        load_level(self, player_count, world, level)

    def save_level(self):
        pass

    def update(self, delta_time):
        for player in self.game_sprites["players"].sprites():
            player.calc_next_pos(self.game_sprites["blocks"].sprites(), render_surface=self.render_surface)

        for player in self.game_sprites["players"].sprites():
            player.apply_next_pos()
        self.camera.x = self.game_sprites["players"].sprites()[0].rect.centerx - self.context["game_size"][0] / 2
        self.camera.y = self.game_sprites["players"].sprites()[0].rect.centery - self.context["game_size"][1] / 2

    def render(self, screen):
        self.render_surface.fill("light blue")
        for object_group in self.game_sprites.values():
            for sprite in object_group.sprites():
                self.render_surface.blit(sprite.image, sprite.rect)

        self.camera.render(screen, self.render_surface)


