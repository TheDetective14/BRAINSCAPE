from settings import *

class DialogueSystem:
    def __init__(self, dialogue, display, font):
        self.dialogue = dialogue  # List of dialogue lines
        self.display_surface = display     # Pygame screen
        self.font = font          # Font for text rendering
        self.box_color = (50, 50, 50)
        self.text_speed = 5  # Speed of text display
        self.dialogue_index = 0       # Tracks current line in dialogue
        self.current_text = ""        # Text currently shown in the dialogue box
        self.text_timer = 0           # Timer for typewriter effect

    def draw_dialogue_box(self):
        # Load the background image for the dialogue box (make sure the image is properly sized)
        dialogue_box_image = pygame.image.load(join('images', 'dialogue_box.png')).convert_alpha()

        # Set the position and dimensions for the dialogue box
        dialogue_box_rect = dialogue_box_image.get_rect(topleft=(50, WINDOW_HEIGHT - 200))

        # Blit the image onto the display surface
        self.display_surface.blit(dialogue_box_image, dialogue_box_rect)

        # Display the current text in the dialogue box
        text_surface = self.font.render(self.current_text, True, 'white')
        self.display_surface.blit(text_surface, (dialogue_box_rect.x + 100, dialogue_box_rect.y + 70))


    def update_text(self):
        # Check if we're at the end of the dialogue
        if self.dialogue_index < len(self.dialogue):
            # Set the full text of the current line
            full_text = self.dialogue[self.dialogue_index]
            
            # Add one character at a time to create typewriter effect
            if self.text_timer > self.text_speed and len(self.current_text) < len(full_text):
                self.current_text += full_text[len(self.current_text)]
                self.text_timer = 0  # Reset timer for next character
        else:
            self.current_text = "Find the exit."

        # Increment the text timer
        self.text_timer += 1

    def handle_input(self):
        # Move to the next line if space is pressed and the line is fully displayed
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.dialogue_index < len(self.dialogue) and len(self.current_text) == len(self.dialogue[self.dialogue_index]):
            self.dialogue_index += 1
            self.current_text = ""  # Reset text for the new line

    def is_finished(self):
        # Returns True if dialogue is finished
        return self.dialogue_index >= len(self.dialogue)