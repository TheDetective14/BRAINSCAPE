from settings import *
from gamemanager import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, display, groups, collision_sprites):
        super().__init__(groups)
        self.display_surface = display
        self.image_down = pygame.image.load(join('images', 'player', 'down.png')).convert_alpha()
        self.image_up = pygame.image.load(join('images', 'player', 'up.png')).convert_alpha()
        self.image_left = pygame.image.load(join('images', 'player', 'left.png')).convert_alpha()
        self.image_right = pygame.image.load(join('images', 'player', 'right.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image_down, (20, 45))
        self.image_down = pygame.transform.scale(self.image_down, (10, 45))
        self.image_up = pygame.transform.scale(self.image_up, (10, 45))
        self.image_left = pygame.transform.scale(self.image_left, (10, 45))
        self.image_right = pygame.transform.scale(self.image_right, (10, 45))
        self.rect = self.image_right.get_frect(center = pos)
        self.hitbox_rect = self.rect.inflate(-1, -1)
        
        self.direction = pygame.Vector2()
        self.speed = 300
        self.collision_sprites = collision_sprites

    def input(self):        
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(keys[pygame.K_a] or keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_s] or keys[pygame.K_DOWN]) - int(keys[pygame.K_w] or keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction

        if self.direction.y < 0:  # Moving up
            self.image = self.image_up
        elif self.direction.y > 0:  # Moving down
            self.image = self.image_down
        elif self.direction.x < 0:  # Moving left
            self.image = self.image_left
        elif self.direction.x > 0:  # Moving right
            self.image = self.image_right

    def move(self,dt):
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        self.hitbox_rect.y += self.direction.y * self.speed * dt
        self.collision('vertical')
        self.rect.center = self.hitbox_rect.center
    
    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == 'horizontal':
                    if self.direction.x > 0: self.hitbox_rect.right = sprite.rect.left
                    if self.direction.x < 0: self.hitbox_rect.left = sprite.rect.right
                else:
                    if self.direction.y < 0: self.hitbox_rect.top = sprite.rect.bottom
                    if self.direction.y > 0: self.hitbox_rect.bottom = sprite.rect.top
    
    def update(self, dt):
        self.input()
        self.move(dt)