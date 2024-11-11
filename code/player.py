from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, display, groups, collision_sprites):
        super().__init__(groups)
        self.display_surface = display

        # Load video frames for animation
        self.frames = self.extract_frames(join('images', 'player.mp4'))  # Replace with your video file path
        self.current_frame = 0
        self.frame_count = len(self.frames)

        # Initialize sprite image
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox_rect = self.rect.inflate(-1, -1)
        
        self.direction = pygame.Vector2()
        self.speed = 300
        self.collision_sprites = collision_sprites
        self.animation_speed = 0.1  # Adjust as needed
        self.animation_timer = 0

    def extract_frames(self, video_path):
        """Extract frames from video and return as a list of pygame surfaces with transparent backgrounds."""
        frames = []
        video = cv2.VideoCapture(video_path)
        success, frame = video.read()
        
        while success:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            surface = pygame.Surface((frame.shape[1], frame.shape[0]), pygame.SRCALPHA)
            pygame.surfarray.blit_array(surface, frame)
            surface.set_colorkey((0, 0, 0))  # Adjust if the background color is different
            surface = pygame.transform.scale(surface, (35, 35))
            frames.append(surface)
            success, frame = video.read()

        video.release()
        return frames

    def input(self):        
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(keys[pygame.K_a] or keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_s] or keys[pygame.K_DOWN]) - int(keys[pygame.K_w] or keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction

    def animate(self, dt):
        """Cycle through frames to create animation effect."""
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.current_frame = (self.current_frame + 1) % self.frame_count
            self.image = self.frames[self.current_frame]
            self.animation_timer = 0

    def move(self, dt):
        """Move the player in small steps to prevent wall glitching."""
        # Calculate total movement distance based on speed and direction
        total_dx = self.direction.x * self.speed * dt
        total_dy = self.direction.y * self.speed * dt

        # Set a step size for smoother collision handling
        step_size = 2  # Smaller values will prevent glitching at higher speeds

        # Move along the x-axis in small steps
        dx = step_size if total_dx > 0 else -step_size
        for _ in range(int(abs(total_dx) // step_size)):
            self.hitbox_rect.x += dx
            if self.check_collision():
                self.hitbox_rect.x -= dx
                break  # Stop moving if a collision occurs

        # Move along the y-axis in small steps
        dy = step_size if total_dy > 0 else -step_size
        for _ in range(int(abs(total_dy) // step_size)):
            self.hitbox_rect.y += dy
            if self.check_collision():
                self.hitbox_rect.y -= dy
                break  # Stop moving if a collision occurs

        # Update the player rect's position to match the hitbox
        self.rect.center = self.hitbox_rect.center

    def check_collision(self):
        """Check if the player collides with any sprite in collision_sprites."""
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                return True
        return False

    def update(self, dt):
        self.input()
        self.move(dt)
        self.animate(dt)
