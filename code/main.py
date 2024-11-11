from settings import *
from sprites import *
from menus import *
from player import *
from groups import *
from gamemanager import *   

class Game:
    def __init__(self):
        # Setup
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("BrainScape")
        pygame.font.init()
        pygame.mixer.init()
        self.clock = pygame.time.Clock()
        self.running = True
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.collide_points = pygame.sprite.Group()
        self.gameStateManager = GameStateManager('MainMenu')

        self.states = {
            'MainMenu': MainMenu(self.display_surface, self.gameStateManager),
            'Library': Library(self.display_surface, self.gameStateManager)
        }

        self.video = cv2.VideoCapture(join('images', 'intro.mp4'))

    def run(self):
        while self.running:
            dt = self.clock.tick() / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.all_sprites.update(dt)
            
            self.states[self.gameStateManager.get_state()].run()
            
            pygame.display.update()
            
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()