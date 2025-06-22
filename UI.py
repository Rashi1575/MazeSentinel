import pygame
import sys
import os
import random
import math
import cv2


# Initialize pygame
pygame.init()
pygame.mixer.init()

# Load video using OpenCV
video = cv2.VideoCapture("56481-479644998_small.mp4")  # Put your video file in the game folder
success, video_frame = video.read()




# Screen dimensions
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 790
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Maze Sentinel")

# Color Definitions
DARK_BLACK = (15, 15, 25)
DARK_BLUE = (20, 25, 45)
CYAN_BLUE = (0, 200, 255)
LIGHT_CYAN = (100, 255, 255)
EMERALD = (0, 255, 150)
PURPLE = (175, 100, 255)
WHITE = (255, 255, 255)
GRAY = (80, 80, 90)
LIGHT_GRAY = (180, 180, 190)
GOLD = (255, 215, 0)
# Red Color Shades
CRIMSON = (220, 20, 60)
FIRE_RED = (255, 45, 0)
DARK_RED = (139, 0, 0)
BRIGHT_RED = (255, 0, 0)
LIGHT_RED = (255, 102, 102)
SALMON = (250, 128, 114)
INDIAN_RED = (205, 92, 92)
MAROON = (128, 0, 0)
ROSE = (255, 0, 127)


# # Font handling with Cabin font
# try:
#     # Try to load Cabin font (make sure 'Cabin-Regular.ttf' is in your game directory)
#     cabin_font = pygame.font.Font("Cabin-Regular.ttf", 32)
#     title_font = pygame.font.Font("Cabin-Regular.ttf", 64)
#     button_font = pygame.font.Font("Cabin-Regular.ttf", 32)
#     text_font = pygame.font.Font("Cabin-Regular.ttf", 24)
# except:
#     # Fallback to system fonts if Cabin isn't available
cabin_font = pygame.font.SysFont('Impact', 32)
title_font = pygame.font.SysFont('Georgia', 64, bold=True)
button_font = pygame.font.SysFont('Comic Sans MS', 32, bold=True)
text_font = pygame.font.SysFont('Georgia', 24)

# Game states
STATE_MAIN = 0
STATE_RULES = 1
STATE_SETTINGS = 2
STATE_ABOUT = 3
STATE_LEVELS = 4
current_state = STATE_MAIN

show_transition = False
transition_alpha = 255
selected_level = 0
transition_timer = 0
TRANSITION_DURATION = 1000  # milliseconds

# Audio Setup with error handling
sound_objects = {}
try:
    # Load sound files (place these in your game directory)
    sound_objects["click"] = pygame.mixer.Sound("click.mp3")
    sound_objects["ambience"] = pygame.mixer.Sound("maze_ambience.mp3")
    pygame.mixer.music.load("maze_soundtrack.mp3")
    audio_available = True
except:
    # Create silent dummy sounds if audio files aren't found
    silent_sound = pygame.mixer.Sound(buffer=bytearray(44))
    sound_objects["click"] = silent_sound
    sound_objects["ambience"] = silent_sound
    audio_available = False

# Volume settings
master_volume = 0.8
music_volume = 0.7
sfx_volume = 0.85

# Set initial volumes
if audio_available:
    pygame.mixer.music.set_volume(master_volume * music_volume)
    sound_objects["click"].set_volume(master_volume * sfx_volume)
    sound_objects["ambience"].set_volume(master_volume * sfx_volume * 0.5)  # Quieter ambience
    pygame.mixer.music.play(-1)  # Loop background music
    sound_objects["ambience"].play(-1)  # Loop ambient sound

# Particle system
class Particle:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.size = random.randint(1, 3)
        self.speed = random.uniform(0.1, 0.3)
        self.color = (100, 200, 255)  # Simple cyan color
        
    def update(self):
        self.x += random.uniform(-0.5, 0.5)
        self.y += random.uniform(-0.5, 0.5)
        self.x = max(0, min(SCREEN_WIDTH, self.x))
        self.y = max(0, min(SCREEN_HEIGHT, self.y))
        
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)

particles = [Particle() for _ in range(150)]

# Slider class for volume controls
class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val):
        self.rect = pygame.Rect(x, y, width, height)
        self.knob_rect = pygame.Rect(x, y, 20, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.dragging = False
        self.update_knob()
        
    def update_knob(self):
        knob_x = self.rect.x + (self.value - self.min_val) / (self.max_val - self.min_val) * (self.rect.width - 20)
        self.knob_rect.x = knob_x
        
    def draw(self, surface):
        # Draw track
        pygame.draw.rect(surface, GRAY, self.rect, border_radius=5)
        # Draw filled portion
        filled_width = self.knob_rect.x - self.rect.x + 10
        pygame.draw.rect(surface, CYAN_BLUE, (self.rect.x, self.rect.y, filled_width, self.rect.height), border_radius=5)
        # Draw knob
        pygame.draw.rect(surface, WHITE, self.knob_rect, border_radius=5)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.knob_rect.collidepoint(event.pos):
                self.dragging = True
            elif self.rect.collidepoint(event.pos):
                self.value = ((event.pos[0] - self.rect.x) / self.rect.width) * (self.max_val - self.min_val) + self.min_val
                self.update_knob()
                return True
                
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
            
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.value = ((event.pos[0] - self.rect.x) / self.rect.width) * (self.max_val - self.min_val) + self.min_val
            self.value = max(self.min_val, min(self.max_val, self.value))
            self.update_knob()
            return True
            
        return False

# Button class with Cabin font
class Button:
    def __init__(self, x, y, width, height, text, base_color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.base_color = base_color
        self.hover_color = hover_color
        self.current_color = base_color
        self.is_hovered = False
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.base_color
        
        # Draw button
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)
        
        # Draw text with Cabin font
        text_surf = cabin_font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
        
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(pos) and audio_available:
                sound_objects["click"].play()
            return self.rect.collidepoint(pos)
        return False
    
class AnimatedRobot:
    def __init__(self, x, y, frames):
        self.x = x
        self.y = y
        self.frames = frames
        self.index = 0
        self.timer = 0
        self.anim_speed = 0.2
        self.direction = 1
        self.speed = 2
        self.max_left = 100
        self.max_right = SCREEN_WIDTH - 128

    def update(self):
        self.timer += self.anim_speed
        if self.timer >= len(self.frames):
            self.timer = 0
        self.index = int(self.timer)

        self.x += self.direction * self.speed
        if self.x > self.max_right:
            self.direction = -1
        elif self.x < self.max_left:
            self.direction = 1

    def draw(self, surface):
        frame = self.frames[self.index]
        if self.direction == -1:
            frame = pygame.transform.flip(frame, True, False)
        surface.blit(frame, (self.x, self.y))


# Create buttons with Cabin font
play_button = Button(SCREEN_WIDTH//2 - 150, 300, 300, 60, " PLAY", DARK_BLACK, (200, 120, 255))
rules_button = Button(SCREEN_WIDTH//2 - 150, 380, 300, 60, " RULES", DARK_BLACK, (200, 120, 255))
settings_button = Button(SCREEN_WIDTH//2 - 150, 460, 300, 60, " SETTINGS", DARK_BLACK, (200, 120, 255))
about_button = Button(SCREEN_WIDTH//2 - 150, 540, 300, 60, "ABOUT", DARK_BLACK, (200, 120, 255))
exit_button = Button(SCREEN_WIDTH//2 - 150, 620, 300, 60, "  EXIT", DARK_BLACK, (200, 120, 255))
back_button = Button(50, SCREEN_HEIGHT - 100, 200, 50, "  BACK", GRAY, (200, 120, 255))

# Level selection buttons
# level_buttons = []
# for i in range(5):
#     level_color = (150 + i*20, 100 + i*30, 200 - i*10)
#     hover_color = (min(255, level_color[0]+50), min(255, level_color[1]+50), min(255, level_color[2]+50))
#     level_buttons.append(Button(
#         SCREEN_WIDTH//2 - 150,
#         200 + i*90,
#         300, 60,
#         f"LEVEL {i+1}",
#         level_color,
#         hover_color
#     ))
level_buttons = []
red_shades = [
    (255, 180, 180),  # Light Red
    (255, 120, 120),
    (220, 60, 60),
    (180, 30, 30),
    (120, 0, 0)       # Dark Red
]

for i in range(5):
    level_color = red_shades[i]
    hover_color = (
        min(255, level_color[0] + 40),
        min(255, level_color[1] + 40),
        min(255, level_color[2] + 40)
    )
    level_buttons.append(Button(
        SCREEN_WIDTH // 2 - 150,
        200 + i * 90,
        300, 60,
        f"LEVEL {i+1}",
        level_color,
        hover_color
    ))


# Create volume sliders
master_slider = Slider(SCREEN_WIDTH//1.7 - 50, 190, 200, 10, 0, 100, master_volume * 100)
music_slider = Slider(SCREEN_WIDTH//1.7 - 50, 240, 200, 10, 0, 100, music_volume * 100)
sfx_slider = Slider(SCREEN_WIDTH//1.7 - 50, 290, 200, 10, 0, 100, sfx_volume * 100)

def draw_background():
    # Solid background with particles
    screen.fill(DARK_BLACK)
    for particle in particles:
        particle.update()
        particle.draw(screen)

def draw_main_container():
    # Semi-transparent main container
    container = pygame.Surface((900, SCREEN_HEIGHT - 100), pygame.SRCALPHA)
    pygame.draw.rect(container, (*DARK_BLUE, 0), (0, 0, 900, SCREEN_HEIGHT-100), border_radius=12)
    screen.blit(container, ((SCREEN_WIDTH - 900) // 2, 50))

def draw_title(text, y_pos, color=WHITE):
    title = title_font.render(text, True, color)
    screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//1.9, y_pos)))

# Main game loop
clock = pygame.time.Clock()
running = True

while running:
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        # State handling      
        if current_state == STATE_MAIN:
            if play_button.is_clicked(mouse_pos, event):
                current_state = STATE_LEVELS
            elif rules_button.is_clicked(mouse_pos, event):
                current_state = STATE_RULES
            elif settings_button.is_clicked(mouse_pos, event):
                current_state = STATE_SETTINGS
            elif about_button.is_clicked(mouse_pos, event):
                current_state = STATE_ABOUT
            elif exit_button.is_clicked(mouse_pos, event):
                running = False

        elif current_state == STATE_LEVELS:
            if back_button.is_clicked(mouse_pos, event):
                current_state = STATE_MAIN
            # for i, button in enumerate(level_buttons):
            #     if button.is_clicked(mouse_pos, event):
            #         print(f"Starting Level {i+1}")
            for i, button in enumerate(level_buttons):
                if button.is_clicked(mouse_pos, event):
                     selected_level = i + 1
                     show_transition = True
                     transition_alpha = 255
                     transition_timer = pygame.time.get_ticks()

        elif current_state == STATE_SETTINGS:
            if back_button.is_clicked(mouse_pos, event):
                current_state = STATE_MAIN
            # Handle slider events
            if master_slider.handle_event(event):
                master_volume = master_slider.value / 100
                if audio_available:
                    pygame.mixer.music.set_volume(master_volume * music_volume)
                    for sound in sound_objects.values():
                        sound.set_volume(master_volume * sfx_volume)
            elif music_slider.handle_event(event):
                music_volume = music_slider.value / 100
                if audio_available:
                    pygame.mixer.music.set_volume(master_volume * music_volume)
            elif sfx_slider.handle_event(event):
                sfx_volume = sfx_slider.value / 100
                if audio_available:
                    for sound in sound_objects.values():
                        sound.set_volume(master_volume * sfx_volume)
        else:
            if back_button.is_clicked(mouse_pos, event):
                current_state = STATE_MAIN
    
    # Update hover states
    if current_state == STATE_MAIN:
        play_button.check_hover(mouse_pos)
        rules_button.check_hover(mouse_pos)
        settings_button.check_hover(mouse_pos)
        about_button.check_hover(mouse_pos)
        exit_button.check_hover(mouse_pos)
    elif current_state == STATE_LEVELS:
        for button in level_buttons:
            button.check_hover(mouse_pos)
    back_button.check_hover(mouse_pos)
    
    # Drawing
    draw_background()
    draw_main_container()
    
    if current_state == STATE_MAIN:
        # draw_title("MAZE SENTINEL", 130, (100, 255, 255))
        # subtitle = text_font.render("Clear the labyrinth's secrets", True, LIGHT_CYAN)
        # screen.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH//2, 200)))
        
        # play_button.draw(screen)
        # rules_button.draw(screen)
        # settings_button.draw(screen)
        # about_button.draw(screen)
        success, video_frame = video.read()
        if not success:
            video.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Loop video
            success, video_frame = video.read()
        video_frame = cv2.cvtColor(video_frame, cv2.COLOR_BGR2RGB)
        video_frame = cv2.resize(video_frame, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # Convert to Pygame surface
        frame_surface = pygame.surfarray.make_surface(video_frame.swapaxes(0, 1))
        screen.blit(frame_surface, (0, 0))
        
        draw_main_container()
        draw_title("MAZE SENTINEL", 130, (100, 255, 255))
        subtitle = text_font.render("Clear the labyrinth's secrets", True, LIGHT_CYAN)
        screen.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH//2, 200)))

        play_button.draw(screen)
        rules_button.draw(screen)
        settings_button.draw(screen)
        about_button.draw(screen)
        exit_button.draw(screen)

    elif current_state == STATE_LEVELS:
        draw_title("SELECT LEVEL", 120, CYAN_BLUE)
        for button in level_buttons:
            button.draw(screen)
        back_button.draw(screen)
        
    elif current_state == STATE_RULES:
        draw_title("GAME RULES", 100, PURPLE)
        rules = [
            "1. Navigate the maze as the Sentinel",
            "2. Collect power-ups",
            "3. Unlock the locked path with keys ",
            "4. Survive as long as possible",
            "",
            "Controls: WASD to move",
        ]
        for i, rule in enumerate(rules):
            text = text_font.render(rule, True, WHITE)
            screen.blit(text, (SCREEN_WIDTH//2 - 250, 180 + i * 35))
        back_button.draw(screen)
        
    elif current_state == STATE_SETTINGS:
        draw_title("SETTINGS", 100, WHITE)
        
        # Draw volume controls
        master_text = text_font.render(f"Master Volume: {int(master_slider.value)}%", True, WHITE)
        screen.blit(master_text, (SCREEN_WIDTH//2 - 200, 180))
        master_slider.draw(screen)
        
        music_text = text_font.render(f"Music Volume: {int(music_slider.value)}%", True, WHITE)
        screen.blit(music_text, (SCREEN_WIDTH//2 - 200, 230))
        music_slider.draw(screen)
        
        sfx_text = text_font.render(f"SFX Volume: {int(sfx_slider.value)}%", True, WHITE)
        screen.blit(sfx_text, (SCREEN_WIDTH//2 - 200, 280))
        sfx_slider.draw(screen)
        
        # Audio status indicator
        status_text = text_font.render("Audio: " + ("Enabled" if audio_available else "Disabled"), 
                                     True, EMERALD if audio_available else (255, 45, 0) )
        screen.blit(status_text, (SCREEN_WIDTH//2 - 100, 330))
        
        back_button.draw(screen)
        
    elif current_state == STATE_ABOUT:
        draw_title("ABOUT", 100, EMERALD)
        about = [
            "MAZE SENTINEL v1.0",
            "Developed with Pygame",
            "",
            "Graphics & Design: YourStudio",
            "Programming: You",
            "© 2023 All Rights Reserved"
        ]
        for i, line in enumerate(about):
            text = text_font.render(line, True, WHITE)
            screen.blit(text, (SCREEN_WIDTH//2 - 200, 180 + i * 35))
        back_button.draw(screen)
    if show_transition:
        elapsed = pygame.time.get_ticks() - transition_timer
        fade_ratio = elapsed / TRANSITION_DURATION
        if fade_ratio >= 1.0:
            show_transition = False
            # You can call your actual gameplay code here
            print(f"Now entering Level {selected_level}")
        else:
            transition_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            current_alpha = int(255 * (1 - fade_ratio))
            transition_surface.fill((0, 0, 0, current_alpha))  # fade out to transparent
            level_text = title_font.render(f"LEVEL {selected_level}", True, WHITE)
            level_rect = level_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            transition_surface.blit(level_text, level_rect)
            screen.blit(transition_surface, (0, 0))

    pygame.display.flip()
    clock.tick(60)
pygame.quit()
sys.exit()
