from settings import *
from sprites import *
from groups import *
from player import Player
from dialouge import DialogueSystem

class MainMenu:
    def __init__(self, display, gameStateManager):
        self.display_surface = display
        self.gameStateManager = gameStateManager
        self.video_path = join('images', 'intro.mp4')
        self.video = cv2.VideoCapture(self.video_path)
        self.playing_video = True
        self.background_image = pygame.image.load(join('images', 'Menu.png')).convert_alpha()
        self.background_image = pygame.transform.scale(self.background_image, (WINDOW_WIDTH, WINDOW_HEIGHT))

    def play_video(self):
        # Read a frame from the video
        ret, frame = self.video.read()
        if ret:
            # Flip the frame vertically if it’s upside down
            frame = cv2.flip(frame, 90)
            # Resize the frame to fit the display window size
            frame = cv2.resize(frame, (self.display_surface.get_width(), self.display_surface.get_height()))
            # Convert the frame to a Pygame-compatible format (RGB surface)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = pygame.surfarray.make_surface(frame)
            # Display the frame on the Pygame display
            self.display_surface.blit(pygame.transform.rotate(frame, -90), (0, 0))  # Rotate if needed for orientation
        else:
            # If the video ended, stop playing and return to blue screen
            self.playing_video = False
            self.video.release()

    def show_game_title_screen(self):
        # Draw background image
        self.display_surface.blit(self.background_image, (0, 0))

        # Create font for buttons
        font = pygame.font.Font(join('fonts', 'Benguiat.ttf'), 19)

        # Define buttons with positions and actions
        buttons = [
            {"text": "PLAY", "x": WINDOW_WIDTH // 2, "y": WINDOW_HEIGHT - 278},
        ]

        for button in buttons:
            # Render the button text
            button_text = font.render(button["text"], True, (255, 255, 255))  # Default white text
            text_rect = button_text.get_rect(center=(button["x"], button["y"]))

            # Change text color on hover
            if text_rect.collidepoint(pygame.mouse.get_pos()):
                button_text = font.render(button["text"], True, (192, 192, 192))  # Light gray on hover
                if pygame.mouse.get_pressed()[0]:
                    self.gameStateManager.set_state('Library')

            # Draw only the text without a background rectangle
            self.display_surface.blit(button_text, text_rect)
    
    def run(self):
        if self.playing_video:
            self.play_video()
        else:
            self.show_game_title_screen()

class Library:
    def __init__(self, display, gameStateManager):
        self.display_surface = display
        self.gameStateManager = gameStateManager
        self.running = True
        self.clock = pygame.time.Clock()
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.font = pygame.font.Font(join('fonts', 'Minecraft.ttf'), 32)

        self.collide_points = {
                'maze': pygame.Rect(496, 880, 20, 20),
                'locked': pygame.Rect(494, 288, 100, 100)
            }
        
        self.maze_collide_points = {
            'yellow': {
                'rect': pygame.Rect(1460, 1539, 100, 100),
                'active': True
            },
            'green': {
                'rect': pygame.Rect(2648, 1842, 100, 100),
                'active': True
            },
            'blue': {
                'rect': pygame.Rect(2722, 908, 100, 100),
                'active': True
            },
            'orange': {
                'rect': pygame.Rect(1700, 672, 100, 100),
                'active': True
            },
            'red': {
                'rect': pygame.Rect(2134, 1632, 100, 100),
                'active': True
            },
            'purple': {
                'rect': pygame.Rect(2081, 1135, 100, 100),
                'active': True
            }
        }
        
        self.dialogue_lines = [
            "*You open your eyes* (Press space to continue)",
            "In front of you is a normal library.",
            "A regular library, just like any other.",
            "You can't tell what, but something is wrong.",
            "You don't know how you got there, or where you are...",
            "Is that you need to explore the area, and escape."
        ]
        self.dialogue_system = DialogueSystem(self.dialogue_lines, self.display_surface, self.font)

        self.setup()

    def setup(self):
        map = load_pygame(join('data', 'maps', 'library.tmx'))

        for x, y, image in map.get_layer_by_name('Ground').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)
        for obj in map.get_layer_by_name('Walls'):
            CollisionSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)), self.collision_sprites)
        for obj in map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player((obj.x, obj.y), self.display_surface, self.all_sprites, self.collision_sprites)

    def reject_access(self):
        # Render the message
        self.message = "You are not allowed to enter this room yet. Find another way"
        text = self.font.render(self.message, True, 'white')
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))  # Center the text

        # Screen shake duration and intensity
        shake_duration = 500  # milliseconds
        shake_intensity = 10  # pixels

        # Main loop to display the message with shake effect at the beginning
        start_time = pygame.time.get_ticks()  # Get the current time in milliseconds
        while True:
            # Check if 5 seconds have passed
            current_time = pygame.time.get_ticks()
            if current_time - start_time > 3000:
                break  # Exit the loop after 5 seconds

            # Screen shake effect
            if current_time - start_time < shake_duration:
                shake_x = random.randint(-shake_intensity, shake_intensity)
                shake_y = random.randint(-shake_intensity, shake_intensity)
            else:
                shake_x, shake_y = 0, 0  # Stop shaking after the shake duration

            # Fill the screen with red
            self.display_surface.fill('red')

            # Draw the text with the shake offset
            self.display_surface.blit(text, text_rect.move(shake_x, shake_y))

            # Update the display
            pygame.display.update()

    def run(self):
        while self.running:
            dt = self.clock.tick() / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            if self.player.hitbox_rect.colliderect(self.collide_points['maze']):
                self.gameStateManager.set_state('Maze')
                Maze(self.display_surface, self.gameStateManager, self.maze_collide_points).run()
            if self.player.hitbox_rect.colliderect(self.collide_points['locked']):
                self.reject_access()
                self.gameStateManager.set_state('Library')
                Library(self.display_surface, self.gameStateManager).run()
            
            self.all_sprites.update(dt)
            self.dialogue_system.update_text()
            self.dialogue_system.handle_input()
            self.display_surface.fill('black')
            self.all_sprites.draw(self.player.rect.center)
            self.dialogue_system.draw_dialogue_box()
            pygame.display.update()
            
        pygame.quit()

class Maze:
    def __init__(self, display, gameStateManager, collide_points):
        self.display_surface = display
        self.gameStateManager = gameStateManager
        self.running = True
        self.clock = pygame.time.Clock()
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()

        self.collide_points = collide_points

        # self.music = pygame.mixer.Sound(join('audio', 'BGM', 'Background Music.mp3'))
        # self.music.play(loops = -1)
        self.setup()

    def setup(self):
        map = load_pygame(join('data', 'maps', 'maze.tmx'))

        for x, y, image in map.get_layer_by_name('Ground').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)
        for obj in map.get_layer_by_name('Walls'):
            CollisionSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)), self.collision_sprites)
        for obj in map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player((obj.x, obj.y), self.display_surface, self.all_sprites, self.collision_sprites)

    def run(self):
        while self.running:
            dt = self.clock.tick() / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            yellow_point = self.collide_points['yellow']
            blue_point = self.collide_points['blue']
            red_point = self.collide_points['red']
            orange_point = self.collide_points['orange']
            purple_point = self.collide_points['purple']
            green_point = self.collide_points['green']

            if yellow_point['active'] and self.player.hitbox_rect.colliderect(yellow_point['rect']):
                self.gameStateManager.set_state('yellow')
                yellow_point['active'] = False
                MathOlympus(self.display_surface, self.gameStateManager).run()
            if green_point['active'] and self.player.hitbox_rect.colliderect(green_point['rect']):
                self.gameStateManager.set_state('green')
                green_point['active'] = False
                CreditsScene(self.display_surface, self.gameStateManager).run()
            if blue_point['active'] and self.player.hitbox_rect.colliderect(blue_point['rect']):
                self.gameStateManager.set_state('blue')
                blue_point['active'] = False
                MapMaestros.PartOne.MainMenu(self.display_surface, self.gameStateManager).run()
            if orange_point['active'] and self.player.hitbox_rect.colliderect(orange_point['rect']):
                self.gameStateManager.set_state('orange')
                orange_point['active'] = False
                MazeTrazze(self.display_surface, self.gameStateManager).run()
            if red_point['active'] and self.player.hitbox_rect.colliderect(red_point['rect']):
                self.gameStateManager.set_state('red')
                red_point['active'] = False
                JumbleMania(self.display_surface, self.gameStateManager).run()
            if purple_point['active'] and self.player.hitbox_rect.colliderect(purple_point['rect']):
                self.gameStateManager.set_state('purple')
                purple_point['active'] = False
                SequenceSurge(self.display_surface, self.gameStateManager).run()
            
            # TEMPORARY
            if pygame.mouse.get_pressed()[0]:
                print(self.player.hitbox_rect.x, self.player.hitbox_rect.y)

            self.all_sprites.update(dt)
            self.display_surface.fill('black')
            self.all_sprites.draw(self.player.rect.center)
            
            pygame.display.update()
            
        pygame.quit()

class JumbleMania:
    def __init__(self, display, gameStateManager):
        # Display settings
        self.SIZE = (1280, 720)
        self.screen = display
        self.gameStateManager = gameStateManager

        # Colors
        self.WHITE = (255, 255, 255)
        self.DARK_RED = (139, 0, 0)
        self.LIGHT_RED = (255, 102, 102)
        self.VERY_DARK_BROWN = (30, 20, 10)

        # Fonts
        self.custom_font_path = join('fonts', 'Benguiat.ttf')
        self.font = pygame.font.Font(self.custom_font_path, 20)
        self.definition_font = pygame.font.Font(self.custom_font_path, 30)
        self.time_font = pygame.font.Font(self.custom_font_path, 24)
        self.score_font = pygame.font.Font(self.custom_font_path, 135)

        self.collide_points = {
            'yellow': {
                'rect': pygame.Rect(1460, 1539, 100, 100),
                'active': False
            },
            'green': {
                'rect': pygame.Rect(2648, 1842, 100, 100),
                'active': True
            },
            'blue': {
                'rect': pygame.Rect(2722, 908, 100, 100),
                'active': False
            },
            'orange': {
                'rect': pygame.Rect(1700, 672, 100, 100),
                'active': False
            },
            'red': {
                'rect': pygame.Rect(2134, 1632, 100, 100),
                'active': False
            },
            'purple': {
                'rect': pygame.Rect(2081, 1135, 100, 100),
                'active': False
            }
        }

        # Load and scale images
        self.background_intro = pygame.transform.scale(pygame.image.load(join('images', 'ace', 'Minigame menu.png')), self.SIZE)
        self.background_image = pygame.transform.scale(pygame.image.load(join('images', 'ace', 'lava.png')), self.SIZE)
        self.instructions_background = pygame.transform.scale(pygame.image.load(join('images', 'ace', 'Instructions Minigame.png')), self.SIZE)
        self.play_button_image = pygame.transform.scale(pygame.image.load(join('images', 'ace', 'Play.png')), (250, 125))
        self.tile_image = pygame.transform.scale(pygame.image.load(join('images', 'ace', 'Tile Image.png')), (100, 70))
        self.submit_button_image = pygame.transform.scale(pygame.image.load(join('images', 'ace', 'Submit.png')), (300, 150))
        self.correct_image = pygame.transform.scale(pygame.image.load(join('images', 'ace', 'Correct.png')), (300, 150))
        self.incorrect_image = pygame.transform.scale(pygame.image.load(join('images', 'ace', 'Incorrect.png')), (300, 150))
        self.score_background_image = pygame.transform.scale(pygame.image.load(join('images', 'ace', 'Score.png')), self.SIZE)
        self.passed_background_image = pygame.transform.scale(pygame.image.load(join('images', 'ace', 'Passed.png')), self.SIZE)
        self.failed_background_image = pygame.transform.scale(pygame.image.load(join('images', 'ace', 'Failed.png')), self.SIZE)
        self.play_again_button_image = pygame.transform.scale(pygame.image.load(join('images', 'ace', 'Play Again.png')), (300, 150))
    # BGM
    def play_music_1(self):
        """Play intro music (Music 1) and loop it."""
        pygame.mixer.music.load(join('audio', 'BGM', 'Music 1.mp3'))
        pygame.mixer.music.play(loops=-1)

    def play_music_2(self):
        """Play game screen music (Music 2) without looping."""
        pygame.mixer.music.load(join('audio', 'BGM', 'Music 2.mp3'))
        pygame.mixer.music.play(loops=-1)

    def play_music_3(self):
        """Play score screen music (Music 3) and loop it."""
        pygame.mixer.music.load(join('audio', 'BGM', 'Music 3.2.mp3'))
        pygame.mixer.music.play(loops=-1)

    def stop_all_music(self):
        """Stop all playing music."""
        pygame.mixer.music.stop()

    # Fade-in function
    def fade_in(self, surface, image, duration=1.5):
        clock = pygame.time.Clock()
        for alpha in range(0, 255, max(1, int(255 / (duration * 60)))):
            surface.fill((0, 0, 0))
            image.set_alpha(alpha)
            surface.blit(image, (0, 0))
            pygame.display.flip()
            clock.tick(60)

    # Draw text function
    def draw_text(self, surface, text, font, color, pos, align="center"):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "center":
            text_rect.center = pos
        elif align == "left":
            text_rect.topleft = pos
        surface.blit(text_surface, text_rect)

    def typewriter_effect(self, surface, text, font, color, pos, delay=10):
        """Display text with a typewriter effect."""
        text = str(text)
        displayed_text = ""
        
        for char in text:
            displayed_text += char
            rendered_line = self.font.render(displayed_text, True, color)
            surface.blit(rendered_line, pos)
            pygame.display.flip()
            pygame.time.delay(delay)  # Delay between each character

    def show_instructions(self):
        self.fade_in(self.screen, self.instructions_background, duration=1.3)
        
        play_button_rect = self.play_button_image.get_rect(center=(self.SIZE[0] // 2, self.SIZE[1] - 75))
        step_size = 30
        shift_amount = -step_size * 4
        start_y = 260
        left_x = self.SIZE[0] - 524 + shift_amount

        instructions_part1 = [
            "You will be shown a scramble of letters.",
            "A definition will be provided to you.",
            "You must drag and drop each letter to",
            "form the correct structure of the provided",
            "word, and press the SUBMIT button."
        ]
        instructions_part2 = [
            "This will be a great challenge. You are",
            "only provided 15 seconds to arrange the",
            "correct word. You must get at least 3",
            "questions correct out of 5, or else you",
            "will be doomed to repeat this trial over",
            "and over. Forever bound to repeat the same",
            "fate, while the fifth and final",
            "Stone of Truth will never",
            "grace your presence."
        ]
        instructions_part3 = [    
            "Good luck."
        ]

        # Function to display part with typewriter animation
        def display_part(part, show_button=False):
            self.screen.blit(self.instructions_background, (0, 0))
            for i, line in enumerate(part):
                self.typewriter_effect(self.screen, line, self.font, self.WHITE, (left_x, start_y + i * step_size))
            
            if show_button:
                self.screen.blit(self.play_button_image, play_button_rect)
            
            pygame.display.flip()

        # Display first part with typewriter animation
        display_part(instructions_part1)
        pygame.time.delay(2000)  # Wait briefly before switching screens

        # Display second part with typewriter animation and Play button
        display_part(instructions_part2)
        pygame.time.delay(3500)

        # Display second part with typewriter animation and Play button
        display_part(instructions_part3, show_button=True)
                    
        # Event loop to wait for Play button click
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if play_button_rect.collidepoint(event.pos):
                        self.stop_all_music()  # Stop music 1 when Play button is clicked
                        return
            pygame.display.flip()

    # Intro screen function
    def show_start_button(self):
        self.stop_all_music()
        self.play_music_1()  # Start playing music 1 during the intro
        self.fade_in(self.screen, self.background_intro)
        start_time = time.time()
        while time.time() - start_time < 2.5:
            self.screen.blit(self.background_intro, (0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
            pygame.display.flip()
        self.show_instructions()

    # Word data
    def get_word_data(self):
        return [
            ("glimpse", "A quick or brief look at something."),
            ("idle", "Not active or not in use."),
            ("keen", "Having a sharp edge or a strong interest."),
            ("noble", "Having high moral qualities or ideals."),
            ("omit", "To leave out or exclude."),
            ("quest", "A search or pursuit to achieve something."),
            ("urgent", "Requiring immediate attention."),
            ("vague", "Not clear or specific."),
            ("witty", "Showing quick and inventive verbal humor."),
            ("zeal", "Great energy or enthusiasm in pursuit of a cause."),
            ("dwell", "To live or reside in a place."),
            ("hinge", "A joint that allows two parts to swing together."),
            ("islet", "A small island."),
            ("mirth", "Joyfulness or amusement."),
            ("rift", "A crack or split in something."),
            ("trek", "A long, arduous journey."),
            ("adept", "Skilled or proficient at something."),
            ("crisp", "Firm, dry, and brittle."),
            ("dusk", "The time just before nightfall."),
            ("grief", "Deep sorrow, especially caused by loss."),
            ("vow", "A solemn promise."),
            ("pique", "To stimulate interest or curiosity."),
            ("tweak", "To make slight adjustments to something."),
            ("align", "To place in a straight line or proper position."),
            ("haven", "A place of safety or refuge."),
            ("mend", "To repair something that is broken."),
            ("utter", "To speak or say something."),
            ("avert", "To turn away or prevent something."),
            ("tangle", "To twist or knot together."),
            ("quaint", "Attractively unusual or old-fashioned."),
            ("abide", "To accept or act in accordance with something."),
            ("mundane", "Ordinary or commonplace."),
            ("kindle", "To ignite or inspire."),
            ("excel", "To perform exceptionally well."),
            ("unite", "To come together for a common purpose."),
            ("ample", "More than enough."),
            ("jargon", "Specialized language used by a particular group."),
            ("lucid", "Clear and easy to understand."),
            ("zenith", "The highest point or peak of something."),
            ("nuance", "A subtle difference in meaning or expression."),
            ("quirk", "A peculiar behavior or trait."),
            ("ally", "A partner or friend in a common cause."),
            ("gist", "The main point or essence of something."),
            ("knack", "A special skill or talent."),
            ("quell", "To suppress or put an end to."),
            ("nifty", "Particularly good, clever, or stylish."),
            ("vouch", "To assert or confirm the truth of something."),
            ("candid", "Honest and straightforward; open."),
            ("serene", "Calm, peaceful, and untroubled."),
            ("justice", "The quality of being fair."),
        ]

    # Scramble word function
    def scramble_word(self, word):
        word_list = list(word)
        random.shuffle(word_list)
        return ''.join(word_list)

    # Letter sprite class with dragging capability
    class Letter(pygame.sprite.Sprite):
        def __init__(self, screen, char, x, y):
            super().__init__()
            self.screen = screen
            self.char = char
            self.image = pygame.transform.scale(pygame.image.load(join('images', 'ace', 'Letter.png')), (90, 60))
            self.rect = self.image.get_rect(topleft=(x, y))
            self.font = pygame.font.Font(join('fonts', 'Benguiat.ttf'), 40)
            self.text = self.font.render(self.char, True, (0, 0, 0))
            self.text_rect = self.text.get_rect(center=self.rect.center)
            self.dragging = False
            self.snap_distance = 30  # Define a threshold distance for snapping

        def draw(self):
            self.screen.blit(self.image, self.rect)
            self.screen.blit(self.text, self.text_rect)

        def update_position(self, x, y):
            self.rect.topleft = (x, y)
            self.text_rect.center = self.rect.center

        def start_drag(self):
            self.dragging = True

        def stop_drag(self):
            self.dragging = False

        def is_correctly_placed(self, placeholders):
            for i, placeholder in enumerate(placeholders):
                if self.rect.colliderect(placeholder) and placeholder.x == self.rect.x and placeholder.y == self.rect.y:
                    return True
            return False
        
        # Modified is_dragging function to consider visual proximity of ALL letters
        def is_dragging(self, pos, all_letters):
            closest_letter = None
            closest_distance = float('inf')  # Initialize with infinity

            for letter in all_letters:
                # Check if the mouse click is within the letter's visual area
                if letter.rect.collidepoint(pos) and letter.rect.centerx - letter.rect.width // 2 <= pos[0] <= letter.rect.centerx + letter.rect.width // 2 and letter.rect.centery - letter.rect.height // 2 <= pos[1] <= letter.rect.centery + letter.rect.height // 2:
                    distance = ((letter.rect.centerx - pos[0]) ** 2 + (letter.rect.centery - pos[1]) ** 2) ** 0.5
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_letter = letter

            if closest_letter is not None:
                closest_letter.start_drag()  # Only the closest letter is marked as dragging

        def update_drag(self):
            if self.dragging:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                self.update_position(mouse_x - self.rect.width // 2, mouse_y - self.rect.height // 2)

        def snap_to_placeholder(self, placeholders):
            for placeholder in placeholders:
                distance = ((self.rect.centerx - placeholder.centerx) ** 2 +
                            (self.rect.centery - placeholder.centery) ** 2) ** 0.5
                if distance < self.snap_distance:
                    self.update_position(placeholder.x, placeholder.y)
                    break

    # Check if letters are in the correct order to form the target word
    def check_correct_order(self, letters, word, placeholders):
        # Arrange letters by their horizontal position on the screen
        arranged_letters = sorted(letters, key=lambda l: l.rect.x)
        
        # Ensure each letter is correctly placed in the right placeholder
        for i, letter in enumerate(arranged_letters):
            if not letter.is_correctly_placed(placeholders):
                return False
        
        # Form the word from arranged letters
        arranged_word = ''.join([letter.char for letter in arranged_letters])
        
        # Ensure the arranged word exactly matches the target word
        return arranged_word == word

    # Main game function with automatic answer checking on time out
    def play_game(self):
        self.stop_all_music()
        self.play_music_2()  # Play music 2 in a loop
        word_data = self.get_word_data()
        questions = random.sample(word_data, 5)
        score = 0  # Reset score to 0 every time a new game starts

        for word, definition in questions:  # Loop through all questions
            scrambled = self.scramble_word(word)
            letters = [self.Letter(self.screen, char, 0, 0) for char in scrambled]
            running = True
            clock = pygame.time.Clock()
            start_time = time.time()
            time_limit = 15

            # Positioning code for letters and placeholders
            tile_start_x = self.SIZE[0] // 2 - (100 * len(scrambled) + 10 * (len(scrambled) - 1)) // 2
            tile_start_y = 235
            letter_start_y = tile_start_y + 170

            for i, letter in enumerate(letters):
                letter.update_position(tile_start_x + i * (letter.rect.width + 10), letter_start_y)

            placeholders = [
                self.tile_image.get_rect(topleft=(tile_start_x + i * (self.tile_image.get_width() + 10), tile_start_y))
                for i in range(len(scrambled))
            ]

            submit_button_rect = self.submit_button_image.get_rect(center=(self.SIZE[0] // 2, self.SIZE[1] - 115))
            result_rect = submit_button_rect.copy()

            while running:
                self.screen.blit(self.background_image, (0, 0))
                self.draw_text(self.screen, definition, self.definition_font, self.WHITE, (self.SIZE[0] // 2, 210), align="center")

                for rect in placeholders:
                    self.screen.blit(self.tile_image, rect)
                for letter in letters:
                    letter.draw()

                self.screen.blit(self.submit_button_image, submit_button_rect)
                time_elapsed = time.time() - start_time
                time_left = max(0, time_limit - int(time_elapsed))
                self.draw_text(self.screen, f"TIME LEFT: {time_left}", self.time_font, self.WHITE, (self.SIZE[0] // 2, submit_button_rect.top + 10), align="center")

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        for letter in letters:
                            letter.is_dragging(event.pos, letters)  # Pass all letters to is_dragging
                        if submit_button_rect.collidepoint(event.pos):
                            if self.check_correct_order(letters, word, placeholders):
                                self.screen.blit(self.correct_image, result_rect)
                                score += 1
                            else:
                                self.screen.blit(self.incorrect_image, result_rect)
                            pygame.display.flip()
                            pygame.time.delay(1000)
                            running = False
                    elif event.type == pygame.MOUSEBUTTONUP:
                        for letter in letters:
                            if letter.dragging:
                                letter.snap_to_placeholder(placeholders)
                            letter.stop_drag()

                for letter in letters:
                    letter.update_drag()

                if time_left <= 0:
                    if self.check_correct_order(letters, word, placeholders):
                        self.screen.blit(self.correct_image, result_rect)
                        score += 1
                    else:
                        self.screen.blit(self.incorrect_image, result_rect)
                    pygame.display.flip()
                    pygame.time.delay(1000)
                    running = False

                pygame.display.flip()
                clock.tick(60)

        # Limit the score to a maximum of 5
        score = min(score, 5)
        self.show_score(score)
        return score 

    # Show score function with play again button
    def show_score(self, score):
        self.stop_all_music()
        self.play_music_3()
        self.screen.blit(self.score_background_image, (0, 0))
        self.fade_in(self.screen, self.score_background_image, duration=1.5)
        self.draw_text(self.screen, f"{score}", self.score_font, self.VERY_DARK_BROWN, (self.SIZE[0] // 2, self.SIZE[1] // 2 + 63), align="center")
        pygame.display.flip()
        pygame.time.delay(5000)

        if score >= 3:
            self.fade_in(self.screen, self.passed_background_image, duration=1.5)
            pygame.time.delay(5000)
            self.stop_all_music()
            pygame.quit()
            return
        else:
            self.fade_in(self.screen, self.failed_background_image, duration=1.5)
            play_again_button_rect = self.play_again_button_image.get_rect(center=(self.SIZE[0] // 2, self.SIZE[1] - 75))
            self.screen.blit(self.play_again_button_image, play_again_button_rect)
            pygame.display.flip()

            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if play_again_button_rect.collidepoint(event.pos):
                            self.stop_all_music()
                            self.show_start_button()
                            self.play_game()
                            return
                pygame.display.flip()

    def run(self):
        # Start the game
        # Main loop to control game states
        # Main loop to control game states
        running = True
        game_state = "intro"
        score = 0  # Initialize score variable

        while running:
            if game_state == "intro":
                self.show_start_button()  # Intro screen and instructions
                game_state = "playing"  # Set state to playing after intro

            elif game_state == "playing":
                score = self.play_game()  # Capture the score returned from play_game
                game_state = "score"  # Go to score screen after playing

            elif game_state == "score":
                self.show_score(score)  # Show score and handle play-again option
                if score >= 3:
                    running = False  # End game if passed
                else:
                    game_state = "intro"  # Restart if failed

            # Event handling to check for exit events at each game stage
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    Maze(self.screen, self.gameStateManager, self.collide_points)

class MapMaestros:
    class PartOne:
        class MainMenu:
            def __init__(self, display, gameStateManager):
                # Initialize Pygame
                pygame.init()
                self.gameStateManager = gameStateManager

                # Screen dimensions
                WINDOW_WIDTH = 1280
                WINDOW_HEIGHT = 720
                self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
                pygame.display.set_caption("Starry Background")

                # Load videos
                self.video_clip = cv2.VideoCapture(join('images', 'josh', 'star_backs.mp4'))
                self.fps = self.video_clip.get(cv2.CAP_PROP_FPS)      # OpenCV v2.x used "CV_CAP_PROP_FPS"
                self.frame_count = int(self.video_clip.get(cv2.CAP_PROP_FRAME_COUNT))
                self.video_duration = self.frame_count/self.fps
                ret, frame = self.video_clip.read()
                self.first_frame = frame
                self.video_width, self.video_height = self.first_frame.shape[:2]
                self.screen_aspect_ratio = WINDOW_WIDTH / WINDOW_HEIGHT
                self.video_aspect_ratio = self.video_width / self.video_height
                self.zoom_factor = 1.0
                self.current_frame = 0
                self.frame_time = 0

                # Load button images
                self.start_button_image = pygame.image.load(join('images', 'josh', 'start_button.png')).convert_alpha()
                self.exit_button_image = pygame.image.load(join('images', 'josh', 'exit_button.png')).convert_alpha()
                self.start_button_image = pygame.transform.scale(self.start_button_image, (self.start_button_image.get_width() // 3, self.start_button_image.get_height() // 3))
                self.exit_button_image = pygame.transform.scale(self.exit_button_image, (self.exit_button_image.get_width() // 3, self.exit_button_image.get_height() // 3))

                # Set button positions
                self.start_button_rect = self.start_button_image.get_rect(center=(WINDOW_WIDTH // 2 - 15, WINDOW_HEIGHT // 2 + 150))
                self.exit_button_rect = self.exit_button_image.get_rect(center=(WINDOW_WIDTH // 2 - 15, WINDOW_HEIGHT // 2 + 250))

                # Load and play background music
                pygame.mixer.music.load(join('audio', 'BGM', 'main_menusound.mp3'))
                pygame.mixer.music.play(-1)  # Play on a loop

            def run(self):
                # Game loop
                running = True
                while running:
                    # Handle events
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            if self.start_button_rect.collidepoint(event.pos):
                                instructions = MapMaestros.PartOne.Instructions(self.gameStateManager)
                                instructions.run_game()
                                running = False 
                            if self.exit_button_rect.collidepoint(event.pos):
                                running = False

                    # Update the frame (for all screens)
                    current_time = pygame.time.get_ticks() / 1000
                    if current_time - self.frame_time >= self.video_duration / (self.fps * 12):
                        self.current_frame = (self.current_frame + 1) % int(self.video_duration * self.fps)
                        self.frame_time = current_time
                        ret, frame = self.video_clip.read()
                        video_surface = pygame.transform.scale(
                            pygame.surfarray.make_surface(frame.astype('uint8')),
                            (int(self.video_width * self.zoom_factor), int(self.video_height * self.zoom_factor))
                        )
                        video_surface = pygame.transform.flip(video_surface, True, False)
                        video_surface = pygame.transform.rotate(video_surface, 90)
                        x_offset = (WINDOW_WIDTH - video_surface.get_width()) // 2
                        y_offset = (WINDOW_HEIGHT - video_surface.get_height()) // 2

                    # Draw background
                    self.screen.blit(video_surface, (x_offset, y_offset))

                    # Draw buttons
                    self.screen.blit(self.start_button_image, self.start_button_rect)
                    self.screen.blit(self.exit_button_image, self.exit_button_rect)

                    # Update the display
                    pygame.display.flip()

                # Quit Pygame
                pygame.quit()

        class Instructions:
            def __init__(self, gameStateManager):
                # Initialize Pygame
                pygame.init()
                self.gameStateManager = gameStateManager

                # Screen dimensions
                WINDOW_WIDTH = 1280
                WINDOW_HEIGHT = 720
                self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
                pygame.display.set_caption("Map Maestros - Instructions")

                # Load images
                self.background_image = pygame.image.load(join('images', 'josh', 'instructions.png')).convert()
                self.next_button_image = pygame.image.load(join('images', 'josh', "next_button.png")).convert_alpha()

                # Resize the "next_button" image (adjust the dimensions as needed)
                self.next_button_image = pygame.transform.scale(self.next_button_image, (300, 200))

                # Set button position
                self.next_button_rect = self.next_button_image.get_rect(bottomright=(WINDOW_WIDTH - 20, WINDOW_HEIGHT - 20))

                # Load and convert images to PNG format
                self.blue_box_image = pygame.image.load(join('images', 'josh', "map_text2.png")).convert_alpha()
                self.blue_box_image = pygame.transform.scale(self.blue_box_image, (500,300))
                self.red_box_image = pygame.image.load(join('images', 'josh', "map_text1.png")).convert_alpha()
                self.red_box_image = pygame.transform.scale(self.red_box_image, (600,300))

                # Set box positions (center on the screen)
                self.blue_box_rect = self.blue_box_image.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
                self.red_box_rect = self.red_box_image.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40))

                # Set box visibility
                self.show_blue_box = True
                self.show_red_box = False

                self.next_button_clicked = 0

            def run_game(self):
                # Game loop
                running = True
                while running:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            if self.next_button_rect.collidepoint(event.pos):
                                self.next_button_clicked += 1
                                print("Next button clicked!")
                                self.show_blue_box = not self.show_blue_box
                                self.show_red_box = not self.show_red_box
                                if self.next_button_clicked == 2:
                                    # Stop background music
                                    pygame.mixer.music.stop()

                                    # Start the PartTwo class
                                    countdown_screen = MapMaestros.PartTwo.CountdownScreen(self.gameStateManager)
                                    countdown_screen.run()
                                    self.transition_to_countdown()
                                    running = False

                    # Display the background image
                    self.screen.blit(self.background_image, (0, 0))

                    # Draw the appropriate box
                    if self.show_blue_box:
                        self.screen.blit(self.blue_box_image, self.blue_box_rect)
                    elif self.show_red_box:
                        self.screen.blit(self.red_box_image, self.red_box_rect)

                    # Display the "Next" button
                    self.screen.blit(self.next_button_image, self.next_button_rect)

                    # Update the display
                    pygame.display.flip()

                pygame.quit()

            def transition_to_countdown(self):
                # Fade out the current screen
                fade_out_speed = 10
                for alpha in range(255, 0, -fade_out_speed):
                    self.screen.fill((0, 0, 0, alpha))
                    pygame.display.flip()
                    time.sleep(0.01)

                # Start the PartTwo class
                countdown_screen = MapMaestros.PartTwo.CountdownScreen()
                countdown_screen.run()

    # Part Two: Countdown Screen
    class PartTwo:
        class CountdownScreen:
            def __init__(self, gameStateManager):
                # Initialize Pygame
                pygame.init()
                self.gameStateManager = gameStateManager

                # Screen dimensions
                WINDOW_WIDTH = 1280
                WINDOW_HEIGHT = 720
                self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
                pygame.display.set_caption("Countdown")

                # Load countdown image
                self.countdown_image = pygame.image.load(join('images', 'josh', "countdown.png")).convert_alpha()

                # Set initial countdown value
                self.countdown_value = 3

                # Load and play countdown music
                self.countdown_music = pygame.mixer.Sound(join('audio', 'SFX', "countdown_sound.mp3"))
                self.countdown_music.play()

            def run(self):
                # Game loop
                running = True
                while running:
                    # Handle events
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False

                    # Update countdown
                    self.countdown_value -= 1
                    if self.countdown_value == 0:
                        running = False

                    # Draw countdown image
                    self.screen.blit(self.countdown_image, (0, 0))

                    # Update the display
                    pygame.display.flip()

                    # Wait for a short time
                    time.sleep(1)

                # Quit Pygame
                pygame.quit()


        def transition_to_countdown(self):
            # Fade out the current screen
            fade_out_speed = 5  # Lower value for faster fade
            for alpha in range(255, 0, -fade_out_speed):
                self.screen.fill((0, 0, 0, alpha))  # Fill with black and alpha
                pygame.display.flip()
                time.sleep(0.3)  # Adjust sleep duration for fade speed

            # Start the PartTwo class
            countdown_screen = MapMaestros.PartTwo.CountdownScreen(self.gameStateManager)  # Directly start PartTwo
            countdown_screen.run()

    class PartTwo:
        class CountdownScreen:
            def __init__(self, gameStateManager):
                pygame.init()
                self.gameStateManager = gameStateManager
                self.screen = pygame.display.set_mode((1280, 720))
                pygame.display.set_caption("Countdown")

                WINDOW_WIDTH, WINDOW_HEIGHT = self.screen.get_size()
                self.background_image = pygame.image.load(join('images', 'josh', 'actual_laro.png')).convert_alpha()
                self.background_image = pygame.transform.scale(self.background_image, (1280, 720))

                # Load the PNG images for countdown numbers
                self.number_three = pygame.image.load(join('images', 'josh', 'number_three.png')).convert_alpha()
                self.number_two = pygame.image.load(join('images', 'josh', 'number_two.png')).convert_alpha()
                self.number_one = pygame.image.load(join('images', 'josh', 'number_one.png')).convert_alpha()

                # Resize countdown images to be smaller
                self.number_three = pygame.transform.scale(self.number_three, (300, 300))  # Adjust size here
                self.number_two = pygame.transform.scale(self.number_two, (390, 300))      # Adjust size here
                self.number_one = pygame.transform.scale(self.number_one, (300, 300))      # Adjust size here
                pygame.mixer.init()
                self.music = pygame.mixer.music.load(join('audio', 'SFX', 'count_downmusic.mp3'))
            def display_countdown(self):
                countdown_images = [self.number_three, self.number_two, self.number_one]
                for img in countdown_images:
                    self.screen.blit(self.background_image, (0, 0))  # Blit background
                    img_rect = img.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))  # Adjust position lower
                    self.screen.blit(img, img_rect)  # Blit countdown image
                    pygame.display.flip()
                    pygame.time.wait(1000)  # Wait for 1 second

            def run(self):
                pygame.mixer.music.play()
                pygame.mixer.init()
                self.display_countdown()

                game = MapMaestros.PartThree.ContinentMatchGame(self.gameStateManager)
                game.run()    

    class PartThree:        
        class ContinentMatchGame:
            def __init__(self, gameStateManager):
                pygame.init()
                self.screen = pygame.display.set_mode((1280, 720))
                self.gameStateManager = gameStateManager
                pygame.display.set_caption("Continent Match")

                WINDOW_WIDTH, WINDOW_HEIGHT = self.screen.get_size()
                self.background_image = pygame.image.load(join('images', 'josh', 'actual_game.png')).convert_alpha()
                self.background_image = pygame.transform.scale(self.background_image, (1280, 720))

                self.box_image = pygame.image.load(join('images', 'josh', 'the_box.png')).convert_alpha()
                self.box_image = pygame.transform.scale(self.box_image, (WINDOW_WIDTH, WINDOW_HEIGHT))
                
                self.box_width, self.box_height = 180, 160
                self.ice_cube_image = pygame.image.load(join('images', 'josh', 'ice_cube.png')).convert_alpha()
                self.ice_cube_image = pygame.transform.scale(self.ice_cube_image, (self.box_width, self.box_height))

                self.collide_points = {
                    'yellow': {
                        'rect': pygame.Rect(1460, 1539, 100, 100),
                        'active': True
                    },
                    'green': {
                        'rect': pygame.Rect(2648, 1842, 100, 100),
                        'active': True
                    },
                    'blue': {
                        'rect': pygame.Rect(2722, 908, 100, 100),
                        'active': False
                    },
                    'orange': {
                        'rect': pygame.Rect(1700, 672, 100, 100),
                        'active': False
                    },
                    'red': {
                        'rect': pygame.Rect(2134, 1632, 100, 100),
                        'active': True
                    },
                    'purple': {
                        'rect': pygame.Rect(2081, 1135, 100, 100),
                        'active': True
                    }
                }

                self.gap_x, self.gap_y = 10, 10
                self.time_limit = 30

                # Define colors
                self.dark_blue = (0, 0, 139)           # Dark blue for timer and score text
                self.dark_cyan = (0, 139, 139)         # Dark cyan for continent and country text

                # Load fonts
                self.font = pygame.font.Font(join('fonts', 'Benguiat.ttf'), 36)
                self.small_font = pygame.font.Font(join('fonts', 'Benguiat.ttf'), 28)
                self.timer_font = pygame.font.Font(join('fonts', 'Benguiat.ttf'), 32)

                self.countries = [
        ("Brazil", "South America"), ("Nigeria", "Africa"), ("China", "Asia"), 
        ("France", "Europe"), ("Australia", "Oceania"), ("Canada", "North America"), 
        ("Antarctica", "Antarctica"), ("Argentina", "South America"), ("Kenya", "Africa"), 
        ("Japan", "Asia"), ("Germany", "Europe"), ("New Zealand", "Oceania"),
        ("United States", "North America"), ("Chile", "South America"), ("Egypt", "Africa"), 
        ("India", "Asia"), ("Italy", "Europe"), ("Fiji", "Oceania"), ("Mexico", "North America"),
        ("Peru", "South America"), ("South Africa", "Africa"), ("Thailand", "Asia"), 
        ("United Kingdom", "Europe"), ("Papua New Guinea", "Oceania"), ("Cuba", "North America"),
        ("Colombia", "South America"), ("Ethiopia", "Africa"), ("Russia", "Asia"), 
        ("Spain", "Europe"), ("Philippines", "Asia"), ("Iceland", "Europe"), 
        ("Jamaica", "North America"), ("Uruguay", "South America"), ("Turkey", "Asia"), 
        ("Saudi Arabia", "Asia"), ("Portugal", "Europe"), ("Venezuela", "South America"),
        ("Indonesia", "Asia"), ("Algeria", "Africa"), ("Poland", "Europe"), ("Iran", "Asia"),
        ("Morocco", "Africa"), ("Vietnam", "Asia"), ("Belgium", "Europe"), ("Pakistan", "Asia"),
        ("Sudan", "Africa"), ("Sweden", "Europe"), ("Malaysia", "Asia"), ("Netherlands", "Europe"),
        ("Ecuador", "South America"), ("Ghana", "Africa"), ("Romania", "Europe"), ("Bangladesh", "Asia"),
        ("Myanmar", "Asia"), ("South Korea", "Asia"), ("Czech Republic", "Europe"), ("Kazakhstan", "Asia"),
        ("Ukraine", "Europe"), ("Hungary", "Europe"), ("Tanzania", "Africa"), ("Cameroon", "Africa"),
        ("Afghanistan", "Asia"), ("Mozambique", "Africa"), ("United Arab Emirates", "Asia"), ("Singapore", "Asia")
    ]

                self.reset_game()

                # Load PNG images
                self.try_again_image = pygame.image.load(join('images', 'josh', 'try_again.png')).convert_alpha()
                # Assuming 1cm = 37.7953 pixels (approximately)
                self.try_again_image = pygame.transform.scale(self.try_again_image, (int(10 * 37.7953), int(10 * 37.7953)))  
                self.exit_button_image = pygame.image.load(join('images', 'josh', 'exit_button.png')).convert_alpha()
                self.exit_button_image = pygame.transform.scale(self.exit_button_image, (200, 90))
                self.you_won_image = pygame.image.load(join('images', 'josh', 'you_won.png')).convert_alpha()
                self.you_won_image = pygame.transform.scale(self.you_won_image, (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

            def reset_game(self):
                random.shuffle(self.countries)
                self.country_list = self.countries.copy()
                self.selected_country, self.correct_continent = self.country_list.pop()
                self.score = 0
                self.dragging = False
                self.game_start_time = time.time()
                self.running = True
                self.show_try_again = False

                top_row_start_x = (WINDOW_WIDTH - (4 * 150 + 3 * self.gap_x)) // 2
                bottom_row_start_x = (WINDOW_WIDTH - (3 * 150 + 2 * self.gap_x)) // 2
                top_row_y = (WINDOW_HEIGHT - 2 * 140 - self.gap_y) // 2
                bottom_row_y = top_row_y + 140 + self.gap_y
                
                self.continents = {
                    "Africa": pygame.Rect(top_row_start_x, top_row_y, 150, 140),
                    "Asia": pygame.Rect(top_row_start_x + (150 + self.gap_x), top_row_y, 150, 140),
                    "Europe": pygame.Rect(top_row_start_x + 2 * (150 + self.gap_x), top_row_y, 150, 140),
                    "North America": pygame.Rect(top_row_start_x + 3 * (150 + self.gap_x), top_row_y, 150, 140),
                    "South America": pygame.Rect(bottom_row_start_x, bottom_row_y, 150, 140),
                    "Oceania": pygame.Rect(bottom_row_start_x + (150 + self.gap_x), bottom_row_y, 150, 140),
                    "Antarctica": pygame.Rect(bottom_row_start_x + 2 * (150 + self.gap_x), bottom_row_y, 150, 140)
                }

                self.country_rect = pygame.Rect((WINDOW_WIDTH - self.box_width) // 2, bottom_row_y + 140 + self.gap_y, self.box_width, self.box_height)
                self.country_rect_original_pos = self.country_rect.topleft
                # Assuming 1cm = 37.7953 pixels (approximately)
                self.try_again_button = pygame.Rect((WINDOW_WIDTH // 2 - int(10 * 37.7953) // 2), WINDOW_HEIGHT // 2 - int(10 * 37.7953) // 2, int(10 * 37.7953), int(10 * 37.7953))  
                self.exit_button = pygame.Rect((WINDOW_WIDTH - 200) // 2, WINDOW_HEIGHT // 2 + 120, 200, 50) # Moved exit button down

                self.timer_x = self.country_rect.x - 200
                self.score_x = self.country_rect.x + self.country_rect.width + 50
                self.text_y = self.country_rect.y

            def get_fitting_font(self, text, rect_width, rect_height, max_font_size=48):
                fitting_font = pygame.font.Font(join('fonts', 'Benguiat.ttf'), max_font_size)
                while fitting_font.size(text)[0] > rect_width - 10 or fitting_font.size(text)[1] > rect_height - 10:
                    max_font_size -= 2
                    fitting_font = pygame.font.Font(join('fonts', 'Benguiat.ttf'), max_font_size)
                return fitting_font

            def run(self):
                
                while self.running:
                    self.screen.blit(self.background_image, (0, 0))
                    current_time = time.time()
                    elapsed_time = current_time - self.game_start_time
                    remaining_time = max(0, self.time_limit - int(elapsed_time))

                    # Check win condition
                    if self.score >= 10:
                        self.display_win_screen()
                        # Wait for 3 seconds then break the loop
                        pygame.time.delay(3000)
                        break
                    # Check lose condition
                    elif remaining_time == 0:
                        self.display_lose_screen()
                        self.show_try_again = True

                    self.handle_events()
                    self.draw_continents()
                    self.draw_country()
                    self.draw_timer_and_score(remaining_time)

                    # Only draw the "Try Again" button if the player has lost
                    if self.show_try_again:
                        self.draw_try_again_button()

                    pygame.display.flip()

            def handle_events(self):
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                    # Handle "Try Again" button click
                    if self.show_try_again and event.type == pygame.MOUSEBUTTONDOWN and self.try_again_button.collidepoint(event.pos):
                        # Reset the game
                        self.reset_game() 
                    # Handle game events
                    if event.type == pygame.MOUSEBUTTONDOWN and not self.show_try_again:
                        if self.country_rect.collidepoint(event.pos):
                            self.dragging = True
                    if event.type == pygame.MOUSEBUTTONUP:
                        if self.dragging:
                            self.dragging = False
                            if self.continents[self.correct_continent].colliderect(self.country_rect):
                                self.score += 1
                            if not self.country_list:
                                self.reset_game()
                            else:
                                self.selected_country, self.correct_continent = self.country_list.pop()
                            self.country_rect.topleft = self.country_rect_original_pos
                        # Remove the "Try Again" button after the player clicked it
                        if self.show_try_again:
                            self.show_try_again = False
                    if event.type == pygame.MOUSEMOTION and self.dragging:
                        self.country_rect.x += event.rel[0]
                        self.country_rect.y += event.rel[1]

            def draw_country(self):
                self.screen.blit(self.ice_cube_image, self.country_rect.topleft)
                country_font = self.get_fitting_font(self.selected_country, self.country_rect.width, self.country_rect.height, max_font_size=48)
                country_text = country_font.render(self.selected_country, True, self.dark_cyan)
                country_text_rect = country_text.get_rect(center=self.country_rect.center)
                self.screen.blit(country_text, country_text_rect)

            def draw_continents(self):
                for continent, rect in self.continents.items():
                    self.screen.blit(pygame.transform.scale(self.box_image, (150, 140)), rect)
                    continent_font = self.get_fitting_font(continent, rect.width, rect.height, max_font_size=28)
                    continent_text = continent_font.render(continent, True, self.dark_cyan)
                    continent_text_rect = continent_text.get_rect(center=rect.center)
                    self.screen.blit(continent_text, continent_text_rect)

            def draw_timer_and_score(self, remaining_time):
                timer_text = self.timer_font.render(f"Time: {remaining_time}", True, self.dark_blue)
                self.screen.blit(timer_text, (self.timer_x, self.text_y))
                score_text = self.timer_font.render(f"Score: {self.score}", True, self.dark_blue)
                self.screen.blit(score_text, (self.score_x, self.text_y))

            def display_text(self, message, font, color=(255, 0, 0)):
                text_surface = font.render(message, True, color)
                text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
                self.screen.blit(text_surface, text_rect)
                pygame.display.flip()

            def draw_try_again_button(self):
                self.screen.blit(self.try_again_image, self.try_again_button.topleft)

            def display_win_screen(self):
                # Display "YOU WON!" message
                self.screen.blit(self.you_won_image, (WINDOW_WIDTH // 2 - self.you_won_image.get_width() // 2, WINDOW_HEIGHT // 2 - self.you_won_image.get_height() // 2)) 
                # Draw button
                self.screen.blit(self.exit_button_image, self.exit_button.topleft)
                pygame.display.flip()

                # Wait for user to click Exit button
                while True:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            exit()
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            if self.exit_button.collidepoint(event.pos):
                                Maze(self.screen, self.gameStateManager, self.collide_points).run()
            def display_lose_screen(self):
                # Draw buttons
                self.screen.blit(self.try_again_image, self.try_again_button.topleft)
                self.screen.blit(self.exit_button_image, self.exit_button.topleft)
                pygame.display.flip()

                # Wait for user to click a button
                while True:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            exit()
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            if self.try_again_button.collidepoint(event.pos):
                                self.reset_game()
                                return
                            elif self.exit_button.collidepoint(event.pos):
                                Maze(self.screen, self.gameStateManager, self.collide_points).run()
                    pygame.quit()

class MathOlympus:
    def __init__(self, display, gameStateManager):
        self.screen = display
        self.gameStateManager = gameStateManager
        
        # Load images
        self.run_image = pygame.image.load(join('images', 'trisha', 'main_menu.png'))
        self.run_image = pygame.transform.scale(self.run_image, (WINDOW_WIDTH, WINDOW_HEIGHT))
        
        self.question_bg_image = pygame.image.load(join('images', 'trisha', 'question_bg.png'))
        self.question_bg_image = pygame.transform.scale(self.question_bg_image, (WINDOW_WIDTH, WINDOW_HEIGHT))

        self.positive_feedback_image = pygame.image.load(join('images', 'trisha', 'positive_feedback.png'))
        self.positive_feedback_image = pygame.transform.scale(self.positive_feedback_image, (WINDOW_WIDTH, WINDOW_HEIGHT))
        
        self.negative_feedback_image = pygame.image.load(join('images', 'trisha', 'negative_feedback.png'))
        self.negative_feedback_image = pygame.transform.scale(self.negative_feedback_image, (WINDOW_WIDTH, WINDOW_HEIGHT))

        self.congratulations_image = pygame.image.load(join('images', 'trisha', 'congratulations.png'))
        self.congratulations_image = pygame.transform.scale(self.congratulations_image, (WINDOW_WIDTH, WINDOW_HEIGHT))

        self.failure_image = pygame.image.load(join('images', 'trisha', 'failure.png'))
        self.failure_image = pygame.transform.scale(self.failure_image, (WINDOW_WIDTH, WINDOW_HEIGHT))

        self.live_image = pygame.image.load(join('images', 'trisha', 'lives.png'))
        self.live_image = pygame.transform.scale(self.live_image, (40, 40))

        self.instructions_bg = pygame.image.load(join('images', 'trisha',"instructions.png"))
        self.instructions_bg = pygame.transform.scale(self.instructions_bg, (WINDOW_WIDTH, WINDOW_HEIGHT))

        pygame.mixer.music.load(join('audio', 'BGM', 'bg_music.mp3'))
        pygame.mixer.music.play(-1) 

        self.collide_points = {
            'yellow': {
                'rect': pygame.Rect(1460, 1539, 100, 100),
                'active': False
            },
            'green': {
                'rect': pygame.Rect(2648, 1842, 100, 100),
                'active': True
            },
            'blue': {
                'rect': pygame.Rect(2722, 908, 100, 100),
                'active': False
            },
            'orange': {
                'rect': pygame.Rect(1700, 672, 100, 100),
                'active': False
            },
            'red': {
                'rect': pygame.Rect(2134, 1632, 100, 100),
                'active': True
            },
            'purple': {
                'rect': pygame.Rect(2081, 1135, 100, 100),
                'active': False
            }
        }
        self.instructions_bg = pygame.image.load(join('images', 'trisha', "instructions.png"))
        self.instructions_bg = pygame.transform.scale(self.instructions_bg, (WINDOW_WIDTH, WINDOW_HEIGHT))


        # Set font settings
        self.pixel_font_display = pygame.font.Font(join('fonts', 'Benguiat.ttf'), 50)
        self.pixel_font_feedback = pygame.font.Font(join('fonts', 'Benguiat.ttf'), 70)
        self.pixel_font_large = pygame.font.Font(join('fonts', 'Benguiat.ttf'), 42)
        self.pixel_font_small = pygame.font.Font(join('fonts', 'Benguiat.ttf'), 32)
        self.pixel_font_instructions = pygame.font.Font(join('fonts', 'Benguiat.ttf'), 18)

        # Define colors
        self.white_text_color = (255, 255, 255)
        self.clue_text_color = (255, 255, 247)
        self.faded_text_color = (249, 246, 238)
        self.blue_text_color = (137, 207, 240)

        # Initialize game variables
        self.is_running = True
        self.clock = pygame.time.Clock()
        self.selected_option = 0
        self.current_question_index = 0
        self.total_questions = 5
        self.mistakes_count = 0
        self.lives_count = 3
        self.score = 0  
        self.time_limit = 20000  
        self.start_time = pygame.time.get_ticks() 

        # POOL OF MATH QUESTIONS
        self.questions_pool = [
        {"question": "A train travels 120 miles at 60 mph. How long is the journey?", 
        "clue": "Use: time = distance / speed.", 
        "options": ["1 hour", "2 hours", "3 hours"], 
        "answer": "2 hours"},
        
        {"question": "Solve 2(x - 4) = 10. What is x?", 
        "clue": "Expand and solve for x.", 
        "options": ["9", "7", "10"], 
        "answer": "9"},
        
        {"question": "A circle's diameter is 14 cm. What is its circumference? (Use pi = 3.14)", 
        "clue": "Circumference = pi x diameter.", 
        "options": ["28 cm", "44 cm", "14 cm"], 
        "answer": "44 cm"},
        
        {"question": "If 3x + 2 = 11, what is x?", 
        "clue": "Isolate x in the equation.", 
        "options": ["3", "2", "5"], 
        "answer": "3"},
        
        {"question": "A rectangular garden is 12 m long and 5 m wide. What is the area?", 
        "clue": "Area = length x width.", 
        "options": ["60 m²", "70 m²", "40 m²"], 
        "answer": "60 m²"},
        
        {"question": "The sum of three consecutive even numbers is 48. What are they?", 
        "clue": "Let the numbers be x, x+2, x+4.", 
        "options": ["14, 16, 18", "12, 14, 16", "10, 12, 14"], 
        "answer": "14, 16, 18"},
        
        {"question": "For a triangle with sides 7, 8, and 9, what is the area?", 
        "clue": "Use Heron's formula.", 
        "options": ["26.83", "27.00", "25.00"], 
        "answer": "26.83"},
        
        {"question": "For a right triangle with side lengths in a 3:4 ratio, what is the hypotenuse?", 
        "clue": "Use the Pythagorean theorem: a² + b² = c².", 
        "options": ["5", "7", "8"], 
        "answer": "5"},
        
        {"question": "Calculate 2^3 + 3^2. What is the result?", 
        "clue": "Calculate the powers before adding.", 
        "options": ["17", "18", "19"], 
        "answer": "17"},
        
        {"question": "A rectangle has a perimeter of 36 cm, and its length is twice the width. What are the dimensions?", 
        "clue": "Set up equations for length and width.", 
        "options": ["6 cm by 12 cm", "8 cm by 16 cm", "9 cm by 18 cm"], 
        "answer": "6 cm by 12 cm"},
        
        {"question": "What is the probability of rolling a 7 with two dice?", 
        "clue": "Count the combinations for a sum of 7.", 
        "options": ["1/6", "1/12", "1/36"], 
        "answer": "1/6"},
        
        {"question": "For p(x) = x² - 5x + 6, what are the roots?", 
        "clue": "Factor the polynomial.", 
        "options": ["-2 and -3", "1 and 6", "0 and 5"], 
        "answer": "-2 and -3"},
        
        {"question": "The father-son age ratio is 7:2. If the son is 8, how old is the father?", 
        "clue": "Use the ratio to find the father's age.", 
        "options": ["16", "28", "32"], 
        "answer": "28"},
        
        {"question": "What is the least common multiple (LCM) of 12 and 18?", 
        "clue": "Find multiples of each number.", 
        "options": ["36", "72", "24"], 
        "answer": "36"},
        
        {"question": "What is the slope of the line 2y - 4x = 8?", 
        "clue": "Rearrange to slope-intercept form.", 
        "options": ["2", "4", "1"], 
        "answer": "2"},
        
        {"question": "In a bag with 5 red, 6 blue, and 9 green marbles, what is the probability of drawing a blue marble?", 
        "clue": "Total marbles = 5 + 6 + 9.", 
        "options": ["2/5", "3/10", "1/2"], 
        "answer": "3/10"},
        
        {"question": "Solve for x in 5x - 3 = 2x + 9.", 
        "clue": "Combine like terms to find x.", 
        "options": ["4", "5", "6"], 
        "answer": "4"},
        
        {"question": "What is the measure of an interior angle in a regular hexagon?", 
        "clue": "Use: (n-2) * 180 / n.", 
        "options": ["120", "108", "135"], 
        "answer": "120"},
        
        {"question": "In a right triangle with legs of 6 cm and 8 cm, what is the hypotenuse?", 
        "clue": "Use the Pythagorean theorem.", 
        "options": ["10", "12", "14"], 
        "answer": "10"},
        
        {"question": "What is x in |2x - 3| = 5?", 
        "clue": "Consider both cases for absolute values.", 
        "options": ["-1 and -4", "-4 and 1", "-1 and 4"], 
        "answer": "-1 and 4"},
        
        {"question": "What does the equation x² + 6x + 9 = 0 factor into?", 
        "clue": "Look for perfect squares.", 
        "options": ["(x + 3)²", "(x + 4)²", "(x - 3)²"], 
        "answer": "(x + 3)²"},
        
        {"question": "One company has 3 times the employees of another. If the smaller has 12, how many does the larger have?", 
        "clue": "Multiply to find the answer.", 
        "options": ["36", "24", "12"], 
        "answer": "36"},
        
        {"question": "If f(x) = 3x² - 2x + 1, what is f(2)?", 
        "clue": "Substitute 2 into the function.", 
        "options": ["5", "9", "15"], 
        "answer": "9"},
        
        {"question": "A number multiplied by 4 and decreased by 12 gives 8. What is the number?", 
        "clue": "Set up 4x - 12 = 8 and solve.", 
        "options": ["5", "6", "7"], 
        "answer": "5"},
        
        {"question": "A bottle has a water-juice ratio of 3:1. If there are 12 liters total, how much water is there?", 
        "clue": "Find 3 parts of the total mixture.", 
        "options": ["9 liters", "8 liters", "6 liters"], 
        "answer": "9 liters"}
    ]
        self.questions = self.get_random_questions(self.total_questions)

        # FEEDBACK MESSAGES
        self.positive_feedbacks = [
            "AWESOME! YOU NAILED IT!",
            "WELL DONE! YOU'RE A MATH WHIZ!",
            "FANTASTIC! KEEP THAT MOMENTUM GOING!",
            "SPOT ON! YOU'RE ON FIRE!",
            "GREAT JOB! YOU LEVELED UP YOUR SKILLS!",
            "YES! THAT'S EXACTLY RIGHT!"
        ]

        self.negative_feedbacks = [
            "OOPS! NOT QUITE. GIVE IT ANOTHER SHOT!",
            "HMM, NOT THIS TIME. TRY AGAIN.",
            "INCORRECT. DUST YOURSELF OFF AND TRY AGAIN.",
            "NOT THE RIGHT ANSWER. THINK IT THROUGH AGAIN!",
            "WRONG! BUT LEARNING TAKES TIME!"
            
        ]

    def get_random_questions(self, num_questions=5):
        """
        Selects a random subset of questions from the question pool. 
        """
        random_questions = random.sample(self.questions_pool, num_questions)
        for question in random_questions:
            random.shuffle(question["options"])
        return random_questions
    
    # TEXT FORMATTING
    def draw_wrapped_text(self, surface, text, font, color, rect, line_height=40):
        """
        Draws text within a specified rectangle to ensure the text fits both the height and width constraints. This ensures that the text is clearly visible against the background image without obscuring important elements.
        """
        words = text.split()
        lines = []
        line = ""
        for word in words:
            test_line = line + word + " "
            test_line_surface = font.render(test_line, True, color)
            if test_line_surface.get_width() > rect.width:
                lines.append(line)
                line = word + " "
            else:
                line = test_line
        lines.append(line)

        y = rect.y
        for line in lines:
            line_surface = font.render(line, True, color)
            line_rect = line_surface.get_rect(center=(rect.centerx, y + line_height // 2))
            surface.blit(line_surface, line_rect)
            y += line_height

    def fade_in_text(self, surface, text_surface, text_rect, speed=5):
        """Handles smooth fade-in for text."""
        for alpha in range(0, 255, speed):
            text_surface.set_alpha(alpha)  
            surface.blit(text_surface, text_rect) 
            pygame.display.update()  
            pygame.time.delay(10)

    def fade_out_text(self, surface, text_surface, text_rect, speed=5):
        """Handles smooth fade-out for text."""
        for alpha in range(255, 0, -speed):
            text_surface.set_alpha(alpha)  
            surface.blit(text_surface, text_rect) 
            pygame.display.update() 
            pygame.time.delay(10)

    def draw_centered_text(self, surface, text, font, color, rect, alpha=900):
        """
        Center-align the text within the specified area.
        """
        text_surface = font.render(text, True, color)
        text_surface.set_alpha(alpha)
        text_rect = text_surface.get_rect(center=(rect.centerx, rect.centery))
        surface.blit(text_surface, text_rect)

    # ANIMATION   
    def shake_screen(self, duration=200, intensity=5):
        """Shakes the screen when the player answers incorrectly."""
        original_position = self.screen.get_rect()
        shake_time = pygame.time.get_ticks()
        
        while pygame.time.get_ticks() - shake_time < duration:
            offset_x = random.randint(-intensity, intensity)
            offset_y = random.randint(-intensity, intensity)
            self.screen.blit(self.question_bg_image, (offset_x, offset_y))
            pygame.display.flip()
            pygame.time.delay(10)
        # Fade transition effect
    
    def fade_transition(self, duration=500):
        fade_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        fade_surface.fill((0, 0, 0))  # Black fade color
        for alpha in range(0, 255, int(255 / (duration / 20))):
            fade_surface.set_alpha(alpha)
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.update()
            pygame.time.delay(20)
    
    def fade_out(self, duration=500):
        fade_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        fade_surface.fill((0, 0, 0))  # Black fade color
        for alpha in range(0, 255, int(255 / (duration / 20))):
            fade_surface.set_alpha(alpha)
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.update()
            pygame.time.delay(20)
    
    # GAME FEATURES 
    def draw_lives(self):
        """
        Displays the player's remaining lives with live assets at the top right corner of the screen. 
        """
        lives_text = self.pixel_font_small.render("Lives:", True, self.white_text_color)
        self.screen.blit(lives_text, (WINDOW_WIDTH - 60 - lives_text.get_width() - (self.lives_count * 30), 35))

        for i in range(self.lives_count):
            self.screen.blit(self.live_image, (WINDOW_WIDTH - 90 - (i * 30), 30))

    def draw_timer(self, remaining_time):
        """Draws the countdown timer on the screen."""
        timer_text = self.pixel_font_small.render(f"Time: {remaining_time // 1000}", True, self.white_text_color)
        self.screen.blit(timer_text, (WINDOW_WIDTH - 450, 35))

    def handle_timer(self):
        """Handles the timer and deducts life if time runs out."""
        elapsed_time = pygame.time.get_ticks() - self.start_time
        remaining_time = self.time_limit - elapsed_time

        if remaining_time <= 0:
            self.lives_count -= 1
            self.shake_screen()
            self.reset_timer()  # Reset the timer for the next question
            return 0  
        return remaining_time

    def reset_timer(self):
        """Resets the timer to 20 seconds when a new question is presented."""
        self.start_time = pygame.time.get_ticks()  # Restart the timer from the current time
    
    def handle_time_up(self):
        self.current_question_index += 1  
        self.reset_timer() 

    def draw_score(self):
        """
        Display the player's score at the top-left corner of the screen.
        """
        score_text = self.pixel_font_small.render(f"Score: {self.score}/{self.total_questions}", True, self.white_text_color)
        self.screen.blit(score_text, (30, 35))

    # FEEDBACK MECHANISM
    def show_feedback(self, is_correct):
        """Display feedback to the user indicating whether they got the correct answer or not."""
        feedback_image = self.positive_feedback_image if is_correct else self.negative_feedback_image
        self.screen.blit(feedback_image, (0, 0))

        feedback_message = random.choice(self.positive_feedbacks) if is_correct else random.choice(self.negative_feedbacks)
     
        max_text_width = 700  
        feedback_lines = []
        words = feedback_message.split()
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            test_surface = self.pixel_font_feedback.render(test_line, True, self.white_text_color)
            if test_surface.get_width() > max_text_width:
                feedback_lines.append(current_line.strip())
                current_line = word + " "
            else:
                current_line = test_line
        feedback_lines.append(current_line.strip())  

        text_block_height = len(feedback_lines) * self.pixel_font_feedback.get_height()
        text_y = (WINDOW_HEIGHT - text_block_height) // 2

        full_text_surface = pygame.Surface((max_text_width, text_block_height), pygame.SRCALPHA)
        for i, line in enumerate(feedback_lines):
            line_surface = self.pixel_font_feedback.render(line, True, self.white_text_color)
            line_x = (max_text_width - line_surface.get_width()) // 2 
            full_text_surface.blit(line_surface, (line_x, i * self.pixel_font_feedback.get_height()))

        self.fade_in_text(self.screen, full_text_surface, pygame.Rect((WINDOW_WIDTH - max_text_width) // 2, text_y, max_text_width, text_block_height), speed=10)

        pygame.display.flip()
        pygame.time.wait(1000)
         
        self.fade_out_text(self.screen, full_text_surface, pygame.Rect((WINDOW_WIDTH - max_text_width) // 2, text_y, max_text_width, text_block_height), speed=10)
        pygame.event.clear()
        pygame.display.flip()

    # START AND END SCREEN
    def start_screen(self):
        """" 
        Displays the start screen and waits for user input to start the game.
        """
        while True:
            self.screen.blit(self.run_image, (0, 0))  # Show main menu image
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.fade_transition()  
                    self.fade_out()
                    return  # Start the game

    def display_end_screen(self, is_successful):
        """
        Displays an end screen with a success or failure message based on the player's performance.
        """
        if is_successful:
            self.fade_transition()
            self.fade_out()
            self.screen.blit(self.congratulations_image, (0, 0))
        else:
            self.collide_points = {
                'yellow': {
                    'rect': pygame.Rect(1460, 1539, 100, 100),
                    'active': False
                },
                'green': {
                    'rect': pygame.Rect(2648, 1842, 100, 100),
                    'active': True
                },
                'blue': {
                    'rect': pygame.Rect(2722, 908, 100, 100),
                    'active': False
                },
                'orange': {
                    'rect': pygame.Rect(1700, 672, 100, 100),
                    'active': False
                },
                'red': {
                    'rect': pygame.Rect(2134, 1632, 100, 100),
                    'active': True
                },
                'purple': {
                    'rect': pygame.Rect(2081, 1135, 100, 100),
                    'active': False
                }
            }
            self.fade_transition()
            self.fade_out()
            self.screen.blit(self.failure_image, (0, 0))        
        pygame.display.flip()
        pygame.time.wait(3000)


        # INSTRUCTIONS 
   
    def display_instructions(self):
        """
        Displays the instructions screen with a typewriter animation effect and waits for the user to press a key to start.
        """
        self.screen.blit(self.instructions_bg, (0, 0))

        instructions_text = [
            "Prepare to tackle a series of mathematical equations!",
            "You have to answer 5 questions correctly.",
            "Use the UP and DOWN arrow keys to select an answer.",
            "Press ENTER to submit.",
            "",
            "Warning: You have only 20 seconds to answer each question!",
            "You'll start with three lives, but beware: each incorrect answer",
            "or time-out will cost you a life. If you lose all three lives,",
            "your trial will end, and you'll forfeit the Fourth Stone of Truth.",
            "",
            "Good luck!"
        ]

        box_width = 600
        box_height = 450
        start_x = WINDOW_WIDTH - box_width - 150 
        start_y = WINDOW_HEIGHT - box_height - 20  

        line_spacing = 25  
        typing_speed = 30

        current_line = 0
        current_char = 0
        last_update = pygame.time.get_ticks()
        typing_finished = False

        waiting = True
        while waiting:
            now = pygame.time.get_ticks()

            if now - last_update > typing_speed and not typing_finished:
                last_update = now  

                if current_line < len(instructions_text):  
                    if current_char < len(instructions_text[current_line]):
                        current_char += 1
                    else:
                        current_line += 1
                        current_char = 0

                if current_line >= len(instructions_text):
                    typing_finished = True

                self.screen.blit(self.instructions_bg, (0, 0))

                y_offset = start_y
                for line_num in range(min(current_line + 1, len(instructions_text))):
                    line_text = instructions_text[line_num][:current_char] if line_num == current_line else instructions_text[line_num]
                    text_surface = self.pixel_font_instructions.render(line_text, True, self.white_text_color)
                    text_rect = text_surface.get_rect(center=(start_x + box_width // 2, y_offset))
                    self.screen.blit(text_surface, text_rect)
                    y_offset += line_spacing

            if typing_finished:
                start_prompt = "Press any key to start"
                start_prompt_surface = self.pixel_font_instructions.render(start_prompt, True, self.blue_text_color)
                start_prompt_rect = start_prompt_surface.get_rect(center=(start_x + box_width // 2, WINDOW_HEIGHT - 180))
                self.screen.blit(start_prompt_surface, start_prompt_rect)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    waiting = False
                if event.type == pygame.KEYDOWN and typing_finished:
                    waiting = False

    #GAME LOOP
    def run_game_loop(self):
        """ 
        Main game loop where questions are presented, player input is processed, 
        and scores and lives are updated based on player's responses. 
        """
        # Start the timer when the first question appears
        self.start_time = pygame.time.get_ticks()

        while self.is_running:
            # Display background, lives, score, and timer.
            self.screen.blit(self.question_bg_image, (0, 0))
            self.draw_lives()
            self.draw_score()

            # Get remaining time
            remaining_time = self.handle_timer()
            self.draw_timer(remaining_time)

            if remaining_time <= 0:  
                self.handle_time_up()

            # Check if game has ended.
            if self.current_question_index >= self.total_questions or self.lives_count <= 0:
                break

            # Get the current question and options.
            question_data = self.questions[self.current_question_index]
            question_text = question_data["question"]
            clue_text = question_data["clue"]
            options = question_data["options"]

            # Display background, lives, and score.
            text_area_rect = pygame.Rect((WINDOW_WIDTH - 900) // 2, (WINDOW_HEIGHT - 300) // 2, 900, 500)
            question_rect = pygame.Rect(text_area_rect.x, text_area_rect.y, text_area_rect.width, 120)
            self.draw_wrapped_text(self.screen, question_text, self.pixel_font_large, self.white_text_color, question_rect)

            clue_rect = pygame.Rect(text_area_rect.x, question_rect.bottom + 5, text_area_rect.width, 30)
            self.draw_wrapped_text(self.screen, f"Clue: {clue_text}", self.pixel_font_small, self.clue_text_color, clue_rect)

            option_start_y = clue_rect.bottom + 40
            for i, option in enumerate(options):
                alpha = 255 if i == self.selected_option else 100
                color = self.blue_text_color if i == self.selected_option else self.faded_text_color
                option_rect = pygame.Rect(text_area_rect.x, option_start_y + i * 50, text_area_rect.width, 30)
                self.draw_centered_text(self.screen, option, self.pixel_font_large, color, option_rect, alpha)

            # Handle player input.
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        self.selected_option = (self.selected_option + 1) % len(options)
                    elif event.key == pygame.K_UP:
                        self.selected_option = (self.selected_option - 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        if options[self.selected_option] == question_data["answer"]:
                            self.current_question_index += 1
                            self.selected_option = 0
                            self.score += 1
                            self.show_feedback(True)  
                            self.reset_timer()
                        else:
                            self.mistakes_count += 1
                            self.lives_count -= 1
                            self.shake_screen()
                            self.show_feedback(False)  

            pygame.display.flip()
            self.clock.tick(30)

        self.display_end_screen(self.lives_count > 0 and self.score >= self.total_questions)

    def stop_music(self):
        pygame.mixer.music.stop()

    def run(self):
        self.fade_transition()
        self.start_screen()  # Show start screen
        self.display_instructions()
        self.fade_transition()
        self.run_game_loop()  # Start the game loop
        self.fade_transition()
        self.fade_out()
        Maze(self.screen, self.gameStateManager, self.collide_points).run()

class SequenceSurge:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager
        
        # Load background images and fonts
        self.background_image = pygame.image.load(join('images', 'zuri', 'background.png'))
        self.menu = pygame.image.load(join('images', 'zuri', 'main_menu.png'))
        
        self.music = pygame.mixer.Sound(join('audio', 'BGM', 'SS_music.mp3'))
        self.music.play(loops = -1)
        
        self.pixel_font_display = pygame.font.Font(join('fonts','Benguiat.ttf'), 40)
        self.pixel_font_large = pygame.font.Font(join('fonts','Benguiat.ttf'), 28)
        self.pixel_font_small = pygame.font.Font(join('fonts','Benguiat.ttf'), 20)

        self.collide_points = {
            'yellow': {
                'rect': pygame.Rect(1460, 1539, 100, 100),
                'active': True
            },
            'green': {
                'rect': pygame.Rect(2648, 1842, 100, 100),
                'active': True
            },
            'blue': {
                'rect': pygame.Rect(2722, 908, 100, 100),
                'active': False
            },
            'orange': {
                'rect': pygame.Rect(1700, 672, 100, 100),
                'active': False
            },
            'red': {
                'rect': pygame.Rect(2134, 1632, 100, 100),
                'active': True
            },
            'purple': {
                'rect': pygame.Rect(2081, 1135, 100, 100),
                'active': False
            }
        }
        
        # Score tracking
        self.previous_score = 0
        self.high_score = 0
        
    # Fade transition effect
    def fade_transition(self, duration=500):
        fade_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        fade_surface.fill((0, 0, 0))  # Black fade color
        for alpha in range(0, 255, int(255 / (duration / 20))):
            fade_surface.set_alpha(alpha)
            self.display.blit(fade_surface, (0, 0))
            pygame.display.update()
            pygame.time.delay(20)
    def fade_out(self, duration=500):
        fade_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        fade_surface.fill((0, 0, 0))  # Black fade color
        for alpha in range(0, 255, int(255 / (duration / 20))):
            fade_surface.set_alpha(alpha)
            self.display.blit(fade_surface, (0, 0))
            pygame.display.update()
            pygame.time.delay(20)

    # Display text method
    def display_text(self, text, position, font=None):
        if font is None:
            font = self.pixel_font_display
        text_surface = font.render(text, True, 'white')
        self.display.blit(text_surface, position)

    # Draw button method
    def draw_button(self, rect, text,):
        button_text = self.pixel_font_large.render(text, True, 'white')
        self.display.blit(button_text, (rect.x + (rect.width - button_text.get_width()) // 2, 
                                       rect.y + (rect.height - button_text.get_height()) // 2))

    def show_sequence(self, sequence, interval):
        for number in sequence:
            self.display.blit(self.background_image, (0, 0))
            
            self.display_text(str(number), (WINDOW_WIDTH // 2 - 20, WINDOW_HEIGHT // 2 - 20))
            pygame.display.update()
            time.sleep(interval)
            self.display.blit(self.background_image, (0, 0))
            
            pygame.display.update()
            time.sleep(0.5)

    def display_correct_sequence(self, sequence):
        self.display.blit(self.background_image, (0, 0))
        
        self.display_text("Correct Sequence:", (WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 - 50))

        x_start = WINDOW_WIDTH // 2 - (len(sequence) * 50) // 2  # Center the numbers
        for number in sequence:
            number_text = str(number)
            number_width = self.pixel_font_small.size(number_text)[0]
            self.display_text(number_text, (x_start, WINDOW_HEIGHT // 2))
            x_start += number_width + 20  # Increment position for next number
        pygame.display.update()
        time.sleep(3)  # Show for 3 seconds

    def get_player_input(self, sequence_length):
        
        input_box = pygame.Rect(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 - 25, 300, 50)
        user_input = ''
        player_sequence = []

        button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 75, WINDOW_HEIGHT // 2 + 60, 150, 50)

        input_active = True
        start_time = time.time()

        while input_active and len(player_sequence) < sequence_length:
            self.display.blit(self.background_image, (0, 0))
            
            self.display_text(f"Enter number {len(player_sequence) + 1}/{sequence_length}:", 
                              (WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 - 100), self.pixel_font_small)
            pygame.draw.rect(self.display, 'white', input_box)
            pygame.draw.rect(self.display, 'black', input_box, 2)

            input_surface = self.pixel_font_small.render(user_input, True, 'black')
            self.display.blit(input_surface, (input_box.x + 10, input_box.y + 10))

            self.draw_button(button_rect, "Submit")

            elapsed_time = int(10 - (time.time() - start_time))
            timer_text = self.pixel_font_small.render(f"Time: {elapsed_time}", True, 'white')
            self.display.blit(timer_text, (WINDOW_WIDTH - 200, 150))

            if elapsed_time <= 0:
                player_sequence.append(None)
                user_input = ''
                start_time = time.time()

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and user_input:
                        try:
                            player_sequence.append(float(user_input))
                        except ValueError:
                            pass
                        user_input = ''
                        start_time = time.time()
                    elif event.key == pygame.K_BACKSPACE:
                        user_input = user_input[:-1]
                    elif event.unicode.isdigit() or event.unicode == '.':
                        user_input += event.unicode

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if button_rect.collidepoint(event.pos) and user_input:
                        try:
                            player_sequence.append(float(user_input))
                        except ValueError:
                            pass
                        user_input = ''
                        start_time = time.time()

        return player_sequence

    def check_sequence(self, player_input, correct_sequence, round_num):
        points_per_correct = 1 if round_num <= 2 else 2 if round_num in [3, 4] else 3
        correct_count = 0
        for i in range(min(len(player_input), len(correct_sequence))):
            if player_input[i] == correct_sequence[i]:
                correct_count += points_per_correct
        return correct_count
    
    def draw_paragraph(self, text, position, font, line_spacing=5):
        
    # Split the text by '\n' to get manual line breaks
        lines = text.split('\n')
    
        x, y = position
        line_height = font.get_linesize() + line_spacing  # Calculate height including extra line spacing

        for line in lines:
            line_surface = font.render(line, True, 'white')  # Render the line
            self.display.blit(line_surface, (x, y))          # Draw the line
            y += line_height                                 # Move down for the next line
        


        

    def show_ready_screen(self):
        """Display a ready screen with a 'Ready' button."""
        
        
        
                        
                        
        # Show the background image
        self.display.blit(self.background_image, (0, 0))
        
         # Draw the paragraph on screen
        instructions = ("You will be flashed 4 numbers for a brief period of time.\n"
                        
                        "You must memorize the numbers and their order\n"
                        
                        "and input them one by one in order to score points.\n" 
                        
                        "You must go through a total of five rounds.\n" 
                        "Each round increases in difficulty.\n" 
                        
                        "The time intervals between each number will grow shorter,\n" 
                        
                        "while requiring you to memorize more and more numbers.\n" 
                        
                        "Your score will be totaled at the end of 5 rounds.\n"
                        
                        "If it does not reach the minimum of 20,\n"
                        "Good luck.\n")
                    
        self.draw_paragraph(instructions, (380 ,200), self.pixel_font_small)
        

               
        
        # Draw 'Ready' button
        button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 75, WINDOW_HEIGHT // 2 + 140, 150, 50)
        self.draw_button(button_rect, "Click 'Ready'")
        
        pygame.display.update()
        
        # Wait for the player to click the 'Ready' button
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if button_rect.collidepoint(event.pos):
                        return  # Proceed to the main game


    def main_menu(self):
        self.display.blit(self.menu, (0, 0))
        
        
        self.display_text(f"Previous Score: {self.previous_score}", (WINDOW_WIDTH // 2 -550, WINDOW_HEIGHT // 2 + 200), self.pixel_font_small)
        self.display_text(f"High Score: {self.high_score}", (WINDOW_WIDTH // 2 - 550, WINDOW_HEIGHT // 2 + 250), self.pixel_font_small)

        start_button = pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 100, 200, 50)
        exit_button = pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 200, 200, 50)

        self.draw_button(start_button, "Start")
        self.draw_button(exit_button, "Exit")

        pygame.display.update()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if start_button.collidepoint(event.pos):
                        self.fade_transition()  
                        self.fade_out()
                        self.show_ready_screen()
                        return True
                    elif exit_button.collidepoint(event.pos):
                        Maze(self.display, self.gameStateManager, self.collide_points).run()
    
    

    def run(self):
        """Main function of the game.
        1. Initializes mnimum score to pass
        2. Initializes round number
        3. Increases round number per level
        4. Initializes score and base interval
        5. Applies different conditions depending on the round number, especially at rounds 3,4 and 5
        6. Displays the current score after each round
        7. Checks if player has the minimum score to pass
        8. If player does, they pass the game. If not, they fail """
        minimum_score = 20
        while True:
            if not self.main_menu():
                break

            round_num = 1
            score = 0
            base_interval = 1.5
            running = True

            while running and round_num <= 5:
                self.display.blit(self.background_image, (0,0))
                
                
                self.display_text(f"Round {round_num}", (WINDOW_WIDTH // 2 - 80, WINDOW_HEIGHT // 2 - 20))
                pygame.display.update()
                time.sleep(3)

                if round_num == 3:
                    self.display.blit(self.background_image, (0,0))
                    
                    self.display_text("Sequence increases by one!", (WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 - 40), self.pixel_font_small)
                    self.display_text("Double digit numbers will now be included!", (WINDOW_WIDTH // 2 - 250, WINDOW_HEIGHT // 2 + 40), self.pixel_font_small)
                    self.display_text("Two points each correct answer!", (WINDOW_WIDTH // 2 - 200, WINDOW_HEIGHT // 2 ), self.pixel_font_small)
                    pygame.display.update()
                    time.sleep(4)
                if round_num == 5:
                    self.display.blit(self.background_image, (0,0))
                    
                    self.display_text("Sequence increases by one!", (WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 - 40), self.pixel_font_small)
                    self.display_text("Special number included!", (WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 + 40), self.pixel_font_small)
                    self.display_text("Three points each correct answer!", (WINDOW_WIDTH // 2 - 200, WINDOW_HEIGHT // 2 ), self.pixel_font_small)
                    pygame.display.update()
                    time.sleep(4)

                sequence_length = 4 
                number_range = (0, 99 if round_num >= 3 else 9)
                if round_num == 3:
                    sequence_length = 5
                    base_interval = 1.0
                elif round_num == 4:
                    sequence_length = 5
                    base_interval = 0.8

                    
                elif round_num == 5:
                    sequence_length = 6
                    base_interval = 0.3

                sequence = [random.randint(*number_range) for _ in range(sequence_length)]
                if round_num == 5:
                    sequence[random.randint(0, sequence_length - 1)] = round(math.pi,5)

                self.show_sequence(sequence, base_interval)
                player_input = self.get_player_input(sequence_length)

                if player_input is None:
                    running = False
                    continue

                score += self.check_sequence(player_input, sequence, round_num)
                self.display_correct_sequence(sequence)
                
                round_num += 1
                player_input = sequence
                
                self.display.blit(self.background_image, (0,0))
                
                
                self.display_text(f"Current Score: {score}", (WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 -10 ))
                pygame.display.update()
                time.sleep(2)

            if score <= minimum_score or score >=minimum_score:
                self.previous_score = score
                self.high_score = max(self.high_score, self.previous_score)
            if running:
                self.display.blit(self.background_image, (0,0))
                
    
                self.display_text("Game Over!", (WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 - 50), self.pixel_font_large)
                
                if score >= minimum_score:
                    self.display_text("Congratulations! You Passed!", (WINDOW_WIDTH // 2 - 250, WINDOW_HEIGHT // 2))    
                else:
                    self.display_text("Try Again!", (WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2))
                    self.display_text(f"Final Score: {score}", (WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 60), self.pixel_font_small)
                    self.display_text(f"Minimum Score: {minimum_score}", (WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 100), self.pixel_font_small)
                
                pygame.display.update()
                time.sleep(3)
                self.fade_out()
                if score >= minimum_score:
                        self.display_text("You may now Exit the Dimension!", (WINDOW_WIDTH // 2 - 300, WINDOW_HEIGHT // 2))
                        pygame.display.update()
                        time.sleep(3)
                self.fade_out()

class MazeTrazze:
    def __init__(self, display, gameStateManager):
        # Set up background music
        pygame.mixer.music.load(join('audio', 'BGM', 'final_level_Bg.mp3'))  # Load the background music file
        pygame.mixer.music.set_volume(0.5)  # Set the volume (range from 0.0 to 1.0)
        pygame.mixer.music.play(-1)  # Play the music in a loop (-1 means infinite loop)

        self.screen = display
        self.gameStateManager = gameStateManager

        # Load background images
        self.menu_background_image = pygame.image.load(join('images', 'dale', "1.png")).convert()  # Menu background
        self.menu_background_image = pygame.transform.scale(self.menu_background_image, (WINDOW_WIDTH, WINDOW_HEIGHT))

        self.question_background_image = pygame.image.load(join('images', 'dale', "4.png")).convert()  # Question background
        self.question_background_image = pygame.transform.scale(self.question_background_image, (WINDOW_WIDTH, WINDOW_HEIGHT))

        self.question_box_image = pygame.image.load(join('images', 'dale', "2.png")).convert_alpha()  # Question box
        self.question_box_image = pygame.transform.scale(self.question_box_image, (800, 200))

        # Load the background for each answer choice box
        self.choice_box_image = pygame.image.load(join('images', 'dale', "3.png")).convert_alpha()  # Choice box image
        self.choice_box_image = pygame.transform.scale(self.choice_box_image, (600, 80))  # Scale to fit the buttons

        # Load the background for the start button
        self.start_button_image = pygame.image.load(join('images', 'dale', "5.png")).convert_alpha()  # Start button image
        self.start_button_image = pygame.transform.scale(self.start_button_image, (400, 80))  # Scale to fit the button

        # Load the "Correct.png" and "Wrong.png" images for the result boxes
        self.correct_box_image = pygame.image.load(join('images', 'dale', "Correct.png")).convert_alpha()  # Correct result box
        self.correct_box_image = pygame.transform.scale(self.correct_box_image, (600, 100))  # Scale to fit the message box
        
        self.wrong_box_image = pygame.image.load(join('images', 'dale', "Wrong.png")).convert_alpha()  # Wrong result box
        self.wrong_box_image = pygame.transform.scale(self.wrong_box_image, (600, 100))  # Scale to fit the message box

        # Load the "Restart.png" image for the restart button
        self.restart_button_image = pygame.image.load(join('images', 'dale', "Restart.png")).convert_alpha()  # Restart button image
        self.restart_button_image = pygame.transform.scale(self.restart_button_image, (300, 80))  # Scale to fit the button

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BLUE = (70, 130, 180)
        self.GREEN = (0, 255, 0)
        self.ORANGE = (255, 165, 0)  # Orange color
        self.RED = (255, 69, 0)
        self.YELLOW = (255, 215, 0)

        # Font settings
        self.font = pygame.font.Font(join('fonts', 'Benguiat.ttf'), 30)
        self.large_font = pygame.font.Font(join('fonts', 'Benguiat.ttf'), 50)

        # Game variables
        self.level = 1
        self.max_level = 3
        self.questions_per_level = 3
        self.current_questions = []
        self.current_question_index = 0
        self.correct_answer = None
        self.choices = []
        self.question = ""
        self.correct_answers = 0
        self.score = 0
        self.state = "menu"  # Default to menu state
        self.result_text = ""
        self.used_questions = set()

        self.collide_points = {
            'yellow': {
                'rect': pygame.Rect(1460, 1539, 100, 100),
                'active': True
            },
            'green': {
                'rect': pygame.Rect(2648, 1842, 100, 100),
                'active': True
            },
            'blue': {
                'rect': pygame.Rect(2722, 908, 100, 100),
                'active': True
            },
            'orange': {
                'rect': pygame.Rect(1700, 672, 100, 100),
                'active': False
            },
            'red': {
                'rect': pygame.Rect(2134, 1632, 100, 100),
                'active': True
            },
            'purple': {
                'rect': pygame.Rect(2081, 1135, 100, 100),
                'active': True
            }
        }

        # Passing score threshold
        self.passing_score = 30

        # Question and answer pairs
        self.qa_pairs = [
            ("Which planet is known as the 'Morning Star' or the 'Evening Star'?", "Venus", ["Mercury", "Mars", "Jupiter"]),
            ("What gas do plants absorb from the atmosphere for photosynthesis?", "Carbon Dioxide", ["Oxygen", "Nitrogen", "Hydrogen"]),
            ("What is the most abundant gas in Earth's atmosphere?", "Nitrogen", ["Oxygen", "Carbon Dioxide", "Hydrogen"]),
            ("What is the chemical symbol for water?", "H₂O", ["CO₂", "O₂", "H₂"]),
            ("Who is known as the father of modern physics?", "Albert Einstein", ["Isaac Newton", "Galileo Galilei", "Nikola Tesla"]),
            ("What is the smallest unit of life that can replicate independently?", "Cell", ["Atom", "Molecule", "Organ"]),
            ("What type of animal is a dolphin?", "Mammal", ["Fish", "Amphibian", "Reptile"]),
            ("What is the main element found in the Sun?", "Hydrogen", ["Helium", "Oxygen", "Carbon"]),
            ("What is the powerhouse of the cell?", "Mitochondria", ["Nucleus", "Ribosome", "Endoplasmic Reticulum"]),
            ("What force keeps us anchored to the Earth?", "Gravity", ["Magnetism", "Friction", "Electromagnetic Force"])
        ]

    def get_random_questions(self, num):
        """Get unique questions for a level and avoid running out of questions."""
        available_questions = [
            (q[0], q[1], q[2])  # Tuple of question, correct answer, and wrong choices
            for q in self.qa_pairs if (q[0], q[1]) not in self.used_questions
        ]
        if len(available_questions) < num:
            num = len(available_questions)  # Limit to available questions
        selected_questions = random.sample(available_questions, num)
        self.used_questions.update((q[0], q[1]) for q in selected_questions)  # Store only question and answer tuple
        return selected_questions

    def set_question(self):
        """Set the current question and choices"""
        if self.current_questions:
            self.question, self.correct_answer, wrong_choices = self.current_questions[self.current_question_index]
            self.choices = wrong_choices + [self.correct_answer]
            random.shuffle(self.choices)

    def draw_menu(self):
        """Draw the menu screen"""
        self.screen.blit(self.menu_background_image, (0, 0))  # Draw menu background

        # Draw the start button with "5.png" as background
        start_button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 200, WINDOW_HEIGHT // 2, 400, 80)
        self.screen.blit(self.start_button_image, start_button_rect.topleft)

        # Draw the "Start Game" text in orange color on top of the image
        start_text = self.font.render("Start Game", True, self.ORANGE)
        start_text_rect = start_text.get_rect(center=start_button_rect.center)
        self.screen.blit(start_text, start_text_rect)

        return start_button_rect

    def draw_question(self):
        """Draw the question and choices"""
        self.screen.blit(self.question_background_image, (0, 0))  # Draw question background

        # Score display
        score_text = self.font.render(f"Score: {self.score}", True, self.YELLOW)
        self.screen.blit(score_text, (20, 20))

        # Draw the question box and center the question text inside it
        question_box_rect = self.question_box_image.get_rect(center=(WINDOW_WIDTH // 2, 150))
        self.screen.blit(self.question_box_image, question_box_rect)

        question_text = self.font.render(self.question, True, self.BLACK)
        question_text_rect = question_text.get_rect(center=question_box_rect.center)
        self.screen.blit(question_text, question_text_rect)

        # Draw answer choice buttons
        answer_buttons = []
        for i, choice in enumerate(self.choices):
            button = pygame.Rect(WINDOW_WIDTH // 2 - 300, 300 + i * 100, 600, 80)

            # Draw the "3.png" image as the background for each answer choice box
            self.screen.blit(self.choice_box_image, button.topleft)
            
            choice_text = self.font.render(choice, True, self.WHITE)
            choice_text_rect = choice_text.get_rect(center=button.center)
            self.screen.blit(choice_text, choice_text_rect)

            answer_buttons.append((button, choice))

        return answer_buttons

    def draw_result(self):
        """Draw the result screen with 'Correct!' or 'Wrong!'"""
        self.screen.blit(self.question_background_image, (0, 0))  # Draw background

        result_box_rect = pygame.Rect(WINDOW_WIDTH // 2 - 300, WINDOW_HEIGHT // 2 - 50, 600, 100)
        if self.result_text == "Correct!":
            self.screen.blit(self.correct_box_image, result_box_rect.topleft)
        else:
            self.screen.blit(self.wrong_box_image, result_box_rect.topleft)

        result_message = self.large_font.render(self.result_text, True, self.YELLOW)
        result_message_rect = result_message.get_rect(center=result_box_rect.center)
        self.screen.blit(result_message, result_message_rect)

        pygame.display.update()
        pygame.time.wait(1000)  # Short pause before next question

    def draw_game_over(self):
        """Draw the game over screen"""
        self.screen.blit(self.menu_background_image, (0, 0))  # Draw menu background

        # Final score message
        final_score_text = self.large_font.render(f"Final Score: {self.score}", True, self.YELLOW)
        final_score_rect = final_score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100))
        self.screen.blit(final_score_text, final_score_rect)

        # Check if the player passed or failed
        if self.score >= self.passing_score:
            result_text = self.large_font.render("You Passed! Exiting...", True, self.GREEN)
        else:
            result_text = self.large_font.render("You Failed! Restarting...", True, self.RED)
        
        result_rect = result_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(result_text, result_rect)

        # Draw the restart button with "Restart.png" as background
        restart_button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 + 100, 300, 80)
        self.screen.blit(self.restart_button_image, restart_button_rect.topleft)

        # Restart game text on top of the button
        restart_text = self.font.render("Restart Game", True, self.ORANGE)
        restart_text_rect = restart_text.get_rect(center=restart_button_rect.center)
        self.screen.blit(restart_text, restart_text_rect)

        return restart_button_rect

    def run(self):
        """Main game loop"""
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()

                    if self.state == "menu":
                        start_button_rect = self.draw_menu()
                        if start_button_rect.collidepoint(mouse_pos):
                            self.state = "question"
                            self.current_questions = self.get_random_questions(self.questions_per_level)
                            self.current_question_index = 0
                            self.set_question()
                    elif self.state == "question":
                        answer_buttons = self.draw_question()
                        for button, choice in answer_buttons:
                            if button.collidepoint(mouse_pos):
                                if choice == self.correct_answer:
                                    self.result_text = "Correct!"
                                    self.score += 10
                                    self.correct_answers += 1
                                else:
                                    self.result_text = "Wrong!"
                                self.state = "result"
                    elif self.state == "result":
                        self.current_question_index += 1
                        if self.current_question_index < len(self.current_questions):
                            self.set_question()
                            self.state = "question"
                        else:
                            self.level += 1
                            if self.level > self.max_level:
                                self.state = "game_over"
                            else:
                                self.current_questions = self.get_random_questions(self.questions_per_level)
                                self.current_question_index = 0
                                self.set_question()
                                self.state = "question"
                    elif self.state == "game_over":
                        restart_button_rect = self.draw_game_over()
                        if restart_button_rect.collidepoint(mouse_pos):
                            if self.score >= self.passing_score:
                                Maze(self.screen, self.gameStateManager, self.collide_points).run()
                            else:
                                self.level = 1
                                self.score = 0
                                self.used_questions.clear()
                                self.current_questions = self.get_random_questions(self.questions_per_level)
                                self.current_question_index = 0
                                self.set_question()
                                self.state = "question"

            # Draw the current screen based on the state
            if self.state == "menu":
                self.draw_menu()
            elif self.state == "question":
                self.draw_question()
            elif self.state == "result":
                self.draw_result()
            elif self.state == "game_over":
                self.draw_game_over()

            pygame.display.flip()
            clock.tick(60)

class CreditsScene:
    def __init__(self, display, gameStateManager):
        self.display_surface = display
        self.gameStateManager = gameStateManager
        self.clock = pygame.time.Clock()

        # Define font and colors
        self.font = pygame.font.Font(join('fonts', 'Minecraft.ttf'), 36)
        self.text_color = (237, 233, 232)
        self.bg_color = (0, 0, 0)

        # Credits text
        self.credits_text = [
            "Congratulations! You have escaped and beaten BRAINSCAPE!!!",
            "Please approach any member of LT3 to claim your prize.",
            "",
            "CREDITS",
            "",
            "Intro Video: Angela Chrysler Tana",
            "Main Menu: Angela Chrysler Tana",
            "Library Tile Map: Dan Gochuico",
            "Library Tile Set: Trisha Espiritu",
            "Maze Tile Map: Dan Gochuico",
            "Maze Tile Set: ?",
            "Player Sprite: Dan Gochuico",
            "Collisions: Dan Gochuico",
            "",
            "MINIGAMES",
            "Jumble Mania: Angela Chrysler Tana",
            "Sequence Surge: Jan Zuri Reyes",
            "Map Maestros: Joshua Licarte",
            "Maze Trazze: Dale Cordero",
            "Math Olympus: Trisha Espiritu",
            "Final Game: Dan Gochuico",
            "",
            "ROLES",
            "Programming Lead: Dan Gochuico",
            "Assistant Programmer: Dan Gochuico",
            "Project Director: Dan Gochuico",
            "Project Manager: Dan Gochuico",
            "Code Editor: Dan Gochuico",
            "Game Integration & Compiler: Dan Gochuico",
            "Credits: Dan Gochuico",
            "Music: Dale Cordero",
            "SFX: Dale Cordero",
            "Script & Storyline: Jan Zuri Reyes",
            "Graphics: Joshua Licarte & Ace Tana",
            "Presentation Video: Joshua Licarte & Ace Tana",
            "Infographic Poster: Trisha Espiritu",
            "",
            "TOOLS",
            "Fonts: www.dafont.com",
            "IDE: Visual Studio Code",
            "",
            "Thanks for playing!",
        ]

        # Scrolling parameters
        self.text_height = len(self.credits_text) * 40  # Height of all the text combined
        self.scroll_speed = 2  # Speed at which the text scrolls
        self.y_position = 600  # Start at the bottom of the screen

    def display_credits(self):
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Exit if the user closes the window
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Exit if ESC is pressed
                    return False

        # Fill the screen with the background color
        self.display_surface.fill(self.bg_color)

        # Draw the credits text, scrolling upwards
        for i, line in enumerate(self.credits_text):
            text_surface = self.font.render(line, True, self.text_color)
            self.display_surface.blit(text_surface, 
                             (self.display_surface.get_width() // 2 - text_surface.get_width() // 2, self.y_position + i * 40))

        # Move the text upwards
        self.y_position -= self.scroll_speed

        # Reset the position if the text has moved off the screen
        if self.y_position + self.text_height < 0:
            self.y_position = 600

        # Update the screen
        pygame.display.flip()

        return True  # Return True to indicate the credits scene is still running

    def run(self):
        running = True
        while running:
            running = self.display_credits()
            self.clock.tick(60)  # Limit frame rate to 60 FPS

        # Quit Pygame when done
        pygame.quit()
        sys.exit()