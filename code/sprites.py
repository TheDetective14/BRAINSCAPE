from settings import *

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)
        self.ground = True

class CollisionSprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)

class CollidePoints(pygame.sprite.Sprite):
    def __init__(self, pos, surface, group, target_position):
        super().__init__(group)
        self.image = surface
        self.rect = self.image.get_rect(topleft=pos)
        self.target_position = target_position