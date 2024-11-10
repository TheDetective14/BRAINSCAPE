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
        self.font = pygame.font.Font(join('fonts', 'Minecraft.ttf'), 36)

        self.collide_points = {
                'maze': pygame.Rect(496, 880, 20, 20),
                'locked': pygame.Rect(494, 288, 100, 100)
            }
        
        self.dialogue_lines = [
            "Hello, welcome to the game!",
            "This is an example of a dialogue system in Pygame.",
            "You can use this to create conversations between characters.",
            "Press SPACE to continue..."
        ]
        self.dialogue_system = DialogueSystem(self.dialogue_lines, self.display_surface, self.font)

        # self.music = pygame.mixer.Sound(join('audio', 'BGM', 'Background Music.mp3'))
        # self.music.play(loops = -1)
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
                MathOlympus(self.display_surface, self.gameStateManager).run()
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
    def __init__(self, display, gameStateManager):
        self.display_surface = display
        self.gameStateManager = gameStateManager
        self.running = True
        self.clock = pygame.time.Clock()
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()

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
                FinalGame(self.display_surface, self.gameStateManager).run()
            if blue_point['active'] and self.player.hitbox_rect.colliderect(blue_point['rect']):
                self.gameStateManager.set_state('blue')
                blue_point['active'] = False
                MapMaestros(self.display_surface, self.gameStateManager).run()
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
    pass

class MapMaestros:
    pass

class MathOlympus:
    def __init__(self, display, gameStateManager):
        self.display_surface = display
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

        self.instructions_bg = pygame.image.load("instructions.png")
        self.instructions_bg = pygame.transform.scale(self.instructions_bg, (WINDOW_WIDTH, WINDOW_HEIGHT))


        # Set font settings
        self.pixel_font_display = pygame.font.Font(join('fonts', 'Benguiat.ttf'), 50)
        self.pixel_font_feedback = pygame.font.Font(join('fonts', 'Benguiat.ttf'), 70)
        self.pixel_font_large = pygame.font.Font(join('fonts', 'Benguiat.ttf'), 42)
        self.pixel_font_small = pygame.font.Font(join('fonts', 'Benguiat.ttf'), 32)

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
        original_position = self.display_surface.get_rect()
        shake_time = pygame.time.get_ticks()
        
        while pygame.time.get_ticks() - shake_time < duration:
            offset_x = random.randint(-intensity, intensity)
            offset_y = random.randint(-intensity, intensity)
            self.display_surface.blit(self.question_bg_image, (offset_x, offset_y))
            pygame.display.flip()
            pygame.time.delay(10)
        # Fade transition effect
    
    def fade_transition(self, duration=500):
        fade_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        fade_surface.fill((0, 0, 0))  # Black fade color
        for alpha in range(0, 255, int(255 / (duration / 20))):
            fade_surface.set_alpha(alpha)
            self.display_surface.blit(fade_surface, (0, 0))
            pygame.display.update()
            pygame.time.delay(20)
    
    def fade_out(self, duration=500):
        fade_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        fade_surface.fill((0, 0, 0))  # Black fade color
        for alpha in range(0, 255, int(255 / (duration / 20))):
            fade_surface.set_alpha(alpha)
            self.display_surface.blit(fade_surface, (0, 0))
            pygame.display.update()
            pygame.time.delay(20)
    
    # GAME FEATURES 
    def draw_lives(self):
        """
        Displays the player's remaining lives with live assets at the top right corner of the screen. 
        """
        lives_text = self.pixel_font_small.render("Lives:", True, self.white_text_color)
        self.display_surface.blit(lives_text, (WINDOW_WIDTH - 60 - lives_text.get_width() - (self.lives_count * 30), 35))

        for i in range(self.lives_count):
            self.display_surface.blit(self.live_image, (WINDOW_WIDTH - 90 - (i * 30), 30))

    def draw_timer(self, remaining_time):
        """Draws the countdown timer on the screen."""
        timer_text = self.pixel_font_small.render(f"Time: {remaining_time // 1000}", True, self.white_text_color)
        self.display_surface.blit(timer_text, (WINDOW_WIDTH - 450, 35))

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
        self.display_surface.blit(score_text, (30, 35))

    # FEEDBACK MECHANISM
    def show_feedback(self, is_correct):
        """Display feedback to the user indicating whether they got the correct answer or not."""
        feedback_image = self.positive_feedback_image if is_correct else self.negative_feedback_image
        self.display_surface.blit(feedback_image, (0, 0))

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

        self.fade_in_text(self.display_surface, full_text_surface, pygame.Rect((WINDOW_WIDTH - max_text_width) // 2, text_y, max_text_width, text_block_height), speed=10)

        pygame.display.flip()
        pygame.time.wait(1000) 
        self.fade_out_text(self.display_surface, full_text_surface, pygame.Rect((WINDOW_WIDTH - max_text_width) // 2, text_y, max_text_width, text_block_height), speed=10)

        pygame.display.flip()

    # START AND END SCREEN
    def start_screen(self):
        """" 
        Displays the start screen and waits for user input to start the game.
        """
        while True:
            self.display_surface.blit(self.run_image, (0, 0))  # Show main menu image
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
            self.display_surface.blit(self.congratulations_image, (0, 0))
        else:
            self.fade_transition()
            self.fade_out()
            self.display_surface.blit(self.failure_image, (0, 0))
        pygame.display.flip()
        pygame.time.wait(3000)

   # GAME LOOP
    def run_game_loop(self):
        """ 
        Main game loop where questions are presented, player input is processed, 
        and scores and lives are updated based on player's responses. 
        """
        while self.is_running:
            # Display background, lives, score, and timer.
            self.display_surface.blit(self.question_bg_image, (0, 0))
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

            # Get the current questions and options.
            question_data = self.questions[self.current_question_index]
            question_text = question_data["question"]
            clue_text = question_data["clue"]
            options = question_data["options"]

            # Display background, lives, and score.
            text_area_rect = pygame.Rect((WINDOW_WIDTH - 900) // 2, (WINDOW_HEIGHT - 300) // 2, 900, 500)
            question_rect = pygame.Rect(text_area_rect.x, text_area_rect.y, text_area_rect.width, 120)
            self.draw_wrapped_text(self.display_surface, question_text, self.pixel_font_large, self.white_text_color, question_rect)

            clue_rect = pygame.Rect(text_area_rect.x, question_rect.bottom + 5, text_area_rect.width, 30)
            self.draw_wrapped_text(self.display_surface, f"Clue: {clue_text}", self.pixel_font_small, self.clue_text_color, clue_rect)

            option_start_y = clue_rect.bottom + 40
            for i, option in enumerate(options):
                alpha = 255 if i == self.selected_option else 100
                color = self.blue_text_color if i == self.selected_option else self.faded_text_color
                option_rect = pygame.Rect(text_area_rect.x, option_start_y + i * 50, text_area_rect.width, 30)
                self.draw_centered_text(self.display_surface, option, self.pixel_font_large, color, option_rect, alpha)

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

    def run(self):
        self.fade_transition()
        self.start_screen()  # Show start screen
        self.fade_transition()
        self.run_game_loop()  # Start the game loop
        self.fade_transition()
        self.fade_out()
        Maze(self.display_surface, self.gameStateManager).run()

class SequenceSurge:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager
        
        # Load background images and fonts
        self.background_image = pygame.image.load(join('images', 'zuri', 'background.png'))
        self.menu = pygame.image.load(join('images', 'zuri', 'main_menu.png'))
        self.stone_slate =pygame.image.load(join('images', 'zuri', 'stone_slate.png'))
        
        self.pixel_font_display = pygame.font.Font(join('fonts','Benguiat.ttf'), 40)
        self.pixel_font_large = pygame.font.Font(join('fonts','Benguiat.ttf'), 28)
        self.pixel_font_small = pygame.font.Font(join('fonts','Benguiat.ttf'), 20)
        
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
    def draw_button(self, rect, text):
        button_text = self.pixel_font_small.render(text, True, 'white')
        self.display.blit(button_text, (rect.x + (rect.width - button_text.get_width()) // 2, 
                                       rect.y + (rect.height - button_text.get_height()) // 2))

    def show_sequence(self, sequence, interval):
        for number in sequence:
            self.display.blit(self.background_image, (0, 0))
            self.display.blit(self.stone_slate, (230, 110))
            self.display_text(str(number), (WINDOW_WIDTH // 2 - 20, WINDOW_HEIGHT // 2 - 20))
            pygame.display.update()
            time.sleep(interval)
            self.display.blit(self.background_image, (0, 0))
            self.display.blit(self.stone_slate, (230, 110))
            pygame.display.update()
            time.sleep(0.5)

    def display_correct_sequence(self, sequence):
        self.display.blit(self.background_image, (0, 0))
        self.display.blit(self.stone_slate, (230, 110))
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
            self.display.blit( self.stone_slate, (230, 110))
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

    def main_menu(self):
        self.display.blit(self.menu, (0, 0))
        self.display_text("Sequence Surge!", (WINDOW_WIDTH // 2 - 180, WINDOW_HEIGHT // 2 - 100))
        self.display_text(f"Previous Score: {self.previous_score}", (WINDOW_WIDTH // 2 -550, WINDOW_HEIGHT // 2 + 200), self.pixel_font_small)
        self.display_text(f"High Score: {self.high_score}", (WINDOW_WIDTH // 2 - 550, WINDOW_HEIGHT // 2 + 250), self.pixel_font_small)

        start_button = pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2, 200, 50)
        exit_button = pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 100, 200, 50)

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
                        return True
                    elif exit_button.collidepoint(event.pos):
                        Maze(self.display, self.gameStateManager).run()

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
                self.display.blit( self.stone_slate, (230, 110))
                
                self.display_text(f"Round {round_num}", (WINDOW_WIDTH // 2 - 80, WINDOW_HEIGHT // 2 - 20))
                pygame.display.update()
                time.sleep(3)

                if round_num == 3:
                    self.display.blit(self.background_image, (0,0))
                    self.display.blit( self.stone_slate, (230, 110))
                    self.display_text("Sequence increases by one!", (WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 - 40), self.pixel_font_small)
                    self.display_text("Double digit numbers will now be included!", (WINDOW_WIDTH // 2 - 250, WINDOW_HEIGHT // 2 + 40), self.pixel_font_small)
                    self.display_text("Two points each correct answer!", (WINDOW_WIDTH // 2 - 200, WINDOW_HEIGHT // 2 ), self.pixel_font_small)
                    pygame.display.update()
                    time.sleep(4)
                if round_num == 5:
                    self.display.blit(self.background_image, (0,0))
                    self.display.blit( self.stone_slate, (230, 110))
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
                self.display.blit( self.stone_slate, (230, 110))
                
                self.display_text(f"Current Score: {score}", (WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 -10 ))
                pygame.display.update()
                time.sleep(2)

            if score <= minimum_score or score >=minimum_score:
                self.previous_score = score
                self.high_score = max(self.high_score, self.previous_score)
            if running:
                self.display.blit(self.background_image, (0,0))
                self.display.blit( self.stone_slate, (230, 110))
    
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
        self.display_surface = display
        self.gameStateManager = gameStateManager

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BLUE = (70, 130, 180)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 69, 0)
        self.YELLOW = (255, 215, 0)
        
        # Load and scale background image
        try:
            self.background = pygame.image.load(join('images', 'background.png'))
            self.background = pygame.transform.scale(self.background, (WINDOW_WIDTH, WINDOW_HEIGHT))
        except pygame.error:
            print("Error loading background image. Please check the file path.")
            sys.exit()
        
        # Load pixel font with fallback
        pixel_font_path = join('fonts', 'Minecraft.ttf')  # Replace with the actual path to your pixel font
        try:
            self.font = pygame.font.Font(pixel_font_path, 30)
            self.large_font = pygame.font.Font(pixel_font_path, 50)
        except FileNotFoundError:
            self.font = pygame.font.SysFont("Arial", 30)
            self.large_font = pygame.font.SysFont("Arial", 50)

        # Question and answer pairs
        self.qa_pairs = [
            ("Closest to the Sun", "Mercury", ["Venus", "Earth", "Mars"]),
            ("Plant food process", "Photosynthesis", ["Respiration", "Digestion", "Fermentation"]),
            ("Water symbol", "H2O", ["O2", "CO2", "H2"]),
            ("Fastest land animal", "Cheetah", ["Lion", "Tiger", "Elephant"]),
            ("Hottest planet", "Venus", ["Mercury", "Earth", "Mars"]),
            ("Largest planet", "Jupiter", ["Saturn", "Uranus", "Neptune"]),
            ("Light is faster than", "Sound", ["Heat", "Gravity", "Water"]),
            ("Keeps us grounded", "Gravity", ["Magnetism", "Friction", "Inertia"]),
            ("Atom center", "Nucleus", ["Electron", "Proton", "Neutron"]),
            ("Cell powerhouse", "Mitochondria", ["Nucleus", "Ribosome", "Chloroplast"]),
            ("Electric current unit", "Ampere", ["Volt", "Watt", "Ohm"]),
            ("Weather study", "Meteorology", ["Geology", "Astronomy", "Biology"]),
            ("Water freeze point", "0°C", ["32°F", "100°C", "-273°C"]),
            ("Most air gas", "Nitrogen", ["Oxygen", "Carbon Dioxide", "Argon"]),
            ("Sun energy source", "Solar", ["Wind", "Nuclear", "Hydro"]),
            ("Closest star", "Sun", ["Proxima Centauri", "Sirius", "Alpha Centauri"]),
            ("We breathe this gas", "Oxygen", ["Carbon Dioxide", "Nitrogen", "Hydrogen"]),
            ("Liquid metal", "Mercury", ["Gallium", "Iron", "Lead"]),
            ("Symbol for 'Fe'", "Iron", ["Gold", "Silver", "Copper"]),
            ("Hardest natural thing", "Diamond", ["Gold", "Iron", "Silver"]),
            ("Red planet", "Mars", ["Jupiter", "Venus", "Mercury"]),
            ("First periodic element", "Hydrogen", ["Helium", "Lithium", "Carbon"]),
            ("Pumps blood", "Heart", ["Lungs", "Liver", "Kidneys"]),
            ("Largest body organ", "Skin", ["Liver", "Heart", "Brain"]),
            ("Smallest element particle", "Atom", ["Molecule", "Compound", "Cell"]),
            ("Plant gas", "Oxygen", ["Nitrogen", "Carbon Dioxide", "Hydrogen"]),
            ("Planet with rings", "Saturn", ["Jupiter", "Uranus", "Neptune"]),
            ("Regrows limbs", "Starfish", ["Lizard", "Octopus", "Snake"]),
            ("Measures temperature", "Thermometer", ["Barometer", "Stethoscope", "Chronometer"]),
            ("Rock study", "Geology", ["Biology", "Physics", "Chemistry"])
        ]
        
        # Game variables
        self.level = 1
        self.max_level = 3
        self.questions_per_level = 5
        self.current_questions = []
        self.current_question_index = 0
        self.correct_answer = None
        self.choices = []
        self.question = ""
        self.correct_answers = 0
        self.score = 0
        self.state = "menu"
        self.result_text = ""
        self.used_questions = set()

    def get_random_questions(self, num):
        available_questions = [q for q in self.qa_pairs if q not in self.used_questions]
        selected_questions = random.sample(available_questions, num)
        self.used_questions.update(selected_questions)
        return selected_questions

    def set_question(self):
        self.question, self.correct_answer, wrong_choices = self.current_questions[self.current_question_index]
        self.choices = wrong_choices + [self.correct_answer]
        random.shuffle(self.choices)

    def draw_menu(self):
        self.display_surface.blit(self.background, (0, 0))
        title_text = self.large_font.render(f"Science Quiz Game - Level {self.level}", True, self.WHITE)
        self.display_surface.blit(title_text, (WINDOW_WIDTH // 2 - title_text.get_width() // 2, 100))
        instruction_text = self.font.render("Answer all questions correctly to move to the next level!", True, self.YELLOW)
        self.display_surface.blit(instruction_text, (WINDOW_WIDTH // 2 - instruction_text.get_width() // 2, 200))
        start_button = pygame.Rect(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2, 300, 80)
        pygame.draw.rect(self.display_surface, self.GREEN, start_button)
        start_text = self.font.render("Start Game", True, self.BLACK)
        self.display_surface.blit(start_text, (start_button.x + 60, start_button.y + 25))
        return start_button

    def draw_question(self):
        self.display_surface.blit(self.background, (0, 0))
        score_text = self.font.render(f"Score: {self.score}", True, self.YELLOW)
        self.display_surface.blit(score_text, (20, 20))
        question_text = self.font.render(self.question, True, self.BLACK)
        self.display_surface.blit(question_text, (WINDOW_WIDTH // 2 - question_text.get_width() // 2, 100))
        answer_buttons = []
        for i, choice in enumerate(self.choices):
            button = pygame.Rect(200, 200 + i * 100, 600, 80)
            pygame.draw.rect(self.display_surface, self.BLUE, button)
            choice_text = self.font.render(choice, True, self.WHITE)
            self.display_surface.blit(choice_text, (button.x + 20, button.y + 20))
            answer_buttons.append((button, choice))
        return answer_buttons

    def draw_result(self):
        self.display_surface.blit(self.background, (0, 0))
        result_message = self.large_font.render(self.result_text, True, self.GREEN if self.result_text == "Correct!" else self.RED)
        self.display_surface.blit(result_message, (WINDOW_WIDTH // 2 - result_message.get_width() // 2, WINDOW_HEIGHT // 2 - 50))
        next_button = pygame.Rect(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 + 50, 300, 80)
        pygame.draw.rect(self.display_surface, self.GREEN, next_button)
        next_text = self.font.render("Next", True, self.BLACK)
        self.display_surface.blit(next_text, (next_button.x + 100, next_button.y + 25))
        return next_button

    def draw_game_over(self):
        self.display_surface.blit(self.background, (0, 0))
        game_over_text = self.large_font.render("Congratulations! You've completed the game!", True, self.YELLOW)
        final_score_text = self.font.render(f"Final Score: {self.score}", True, self.YELLOW)
        self.display_surface.blit(game_over_text, (WINDOW_WIDTH // 2 - game_over_text.get_width() // 2, 200))
        self.display_surface.blit(final_score_text, (WINDOW_WIDTH // 2 - final_score_text.get_width() // 2, 300))

    def run(self):
        running = True
        while running:
            self.display_surface.fill(self.WHITE)
            if self.state == "menu":
                start_button = self.draw_menu()
            elif self.state == "playing":
                answer_buttons = self.draw_question()
            elif self.state == "result":
                next_button = self.draw_result()
            elif self.state == "game_over":
                self.draw_game_over()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if self.state == "menu" and start_button.collidepoint(pos):
                        self.current_questions = self.get_random_questions(self.questions_per_level)
                        self.current_question_index = 0
                        self.correct_answers = 0
                        self.set_question()
                        self.state = "playing"
                    elif self.state == "playing":
                        for button, choice in answer_buttons:
                            if button.collidepoint(pos):
                                if choice == self.correct_answer:
                                    self.result_text = "Correct!"
                                    self.correct_answers += 1
                                    self.score += 10
                                else:
                                    self.result_text = "Wrong!"
                                self.state = "result"
                    elif self.state == "result" and next_button.collidepoint(pos):
                        self.current_question_index += 1
                        if self.current_question_index >= self.questions_per_level:
                            if self.correct_answers == self.questions_per_level:
                                if self.level < self.max_level:
                                    self.level += 1
                                    self.state = "menu"
                                else:
                                    self.state = "game_over"
                            else:
                                self.state = "menu"
                        else:
                            self.set_question()
                            self.state = "playing"
            pygame.display.flip()

class FinalGame:
    def __init__(self, display, gameStateManager):
        self.display_surface = display
        self.gameStateManager = gameStateManager

    def run(self):
        Maze(self.display_surface, self.gameStateManager).run()

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
            "AWARDS",
            "Non-ChatGPT User: Dan Gochuico",
            "Fastest Coder: Dan Gochuico",
            "Most : Dan Gochuico",
            "Most Logical: Dan Gochuico",
            "Most Hours Spent Coding (~40 hours): Dan Gochuico",
            "Most Hours Spent Waiting (~100 hours): Dan Gochuico",
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