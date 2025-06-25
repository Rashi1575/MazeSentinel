import pygame
from game import run_single_level
from maze import set_theme  # Import the setter for theme

# 🎉 Show Congrats Screen with Transparent Pause-Style Overlay
def show_level_complete_screen(screen, font, current_level):
    celebration_sound = pygame.mixer.Sound("celebration.mp3")
    click_sound = pygame.mixer.Sound("click.mp3")
    celebration_sound.play()

    button_font = pygame.font.SysFont("Georgia", 24)
    clock = pygame.time.Clock()

    next_button = pygame.Rect(screen.get_width() // 2 - 150, 350, 300, 60)
    exit_button = pygame.Rect(screen.get_width() // 2 - 150, 450, 300, 60)

    while True:
        overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        title = font.render(f"CONGRATS! You cleared Level {current_level}!", True, (0, 255, 0))
        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 250)))

        pygame.draw.rect(screen, (30, 30, 30, 200), next_button, border_radius=12)
        pygame.draw.rect(screen, (100, 255, 255), next_button, 3, border_radius=12)
        next_label = button_font.render("NEXT", True, (255, 255, 255))
        screen.blit(next_label, next_label.get_rect(center=next_button.center))

        pygame.draw.rect(screen, (30, 30, 30, 200), exit_button, border_radius=12)
        pygame.draw.rect(screen, (100, 255, 255), exit_button, 3, border_radius=12)
        exit_label = button_font.render("EXIT", True, (255, 255, 255))
        screen.blit(exit_label, exit_label.get_rect(center=exit_button.center))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if next_button.collidepoint(event.pos):
                    click_sound.play()
                    celebration_sound.stop()
                    return "next"
                elif exit_button.collidepoint(event.pos):
                    click_sound.play()
                    celebration_sound.stop()
                    return "exit"

        clock.tick(60)


# 🧊 Theme Selection Menu
def theme_selection_screen(screen, clock, click_sound):
    font = pygame.font.SysFont("Georgia", 30, bold=True)
    themes = ["jungle", "Cyber", "ice","Dungeon","Nebula / Space"]

    buttons = []
    btn_w, btn_h = 300, 70
    center_x = screen.get_width() // 2
    base_y = 200
    spacing = 100

    for i, theme in enumerate(themes):
        rect = pygame.Rect(center_x - btn_w // 2, base_y + i * spacing, btn_w, btn_h)
        buttons.append((theme, rect))

    while True:
        screen.fill((10, 10, 10))

        title = font.render("Select a Theme", True, (0, 255, 255))
        screen.blit(title, title.get_rect(center=(center_x, 150)))

        for theme, rect in buttons:
            pygame.draw.rect(screen, (30, 30, 30), rect, border_radius=12)
            pygame.draw.rect(screen, (100, 255, 255), rect, 3, border_radius=12)
            label = font.render(theme.capitalize(), True, (255, 255, 255))
            screen.blit(label, label.get_rect(center=rect.center))

        pygame.display.flip()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                for theme, rect in buttons:
                    if rect.collidepoint(ev.pos):
                        click_sound.play()
                        return theme

        clock.tick(30)


# 🔢 Level Specs
LEVELS = [
    {"size": 12, "patrol": 1, "chase": 0, "level": 1},
    {"size": 14, "patrol": 2, "chase": 0, "level": 2},
    {"size": 16, "patrol": 0, "chase": 1, "level": 3},
    {"size": 18, "patrol": 0, "chase": 2, "level": 4},
    {"size": 20, "patrol": 1, "chase": 2, "level": 5},
]


# 🎮 Play Levels
def play_from_level(start_level=1):
    pygame.font.init()
    pygame.mixer.init()

    font = pygame.font.SysFont("Georgia", 24)
    clock = pygame.time.Clock()

    SCREEN_WIDTH = 1024
    SCREEN_HEIGHT = 750
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    click_sound = pygame.mixer.Sound("click.mp3")

    for i in range(start_level - 1, len(LEVELS)):
        spec = LEVELS[i]
        maze_size = spec["size"]

        # Ask for theme before this level
        theme = theme_selection_screen(screen, clock, click_sound)
        set_theme(theme)  # Store selected theme in maze.py

        cell_size_w = SCREEN_WIDTH // maze_size
        cell_size_h = SCREEN_HEIGHT // maze_size
        cell_size = min(cell_size_w, cell_size_h)

        won = run_single_level(spec, screen, clock, font, cell_size)
        if not won:
            return

        result = show_level_complete_screen(screen, font, spec["level"])
        if result == "exit":
            return

    # 🎖 All Levels Complete
    screen.fill((0, 0, 0))
    msg = font.render("🎖 You beat all 5 levels!", True, (255, 215, 0))
    screen.blit(msg, msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))
    pygame.display.flip()
    pygame.time.wait(2000)
