import pygame
from game import run_single_level

# Specs for each level
LEVELS = [
    {"size": 12, "patrol": 1, "chase": 0, "level": 1},
    {"size": 14, "patrol": 2, "chase": 0, "level": 2},
    {"size": 16, "patrol": 0, "chase": 1, "level": 3},
    {"size": 18, "patrol": 0, "chase": 1, "level": 4},
    {"size": 20, "patrol": 0, "chase": 1, "level": 5},
]
# NEWWWW
def play_from_level(start_level=1):
    pygame.font.init()
    font = pygame.font.SysFont(None, 24)
    clock = pygame.time.Clock()

    SCREEN_WIDTH = 1024
    SCREEN_HEIGHT = 790

    for i in range(start_level - 1, len(LEVELS)):
        spec = LEVELS[i]
        maze_size = spec["size"]

        #  Dynamically calculate cell size
        cell_size_w = SCREEN_WIDTH // maze_size
        cell_size_h = SCREEN_HEIGHT // maze_size
        cell_size = min(cell_size_w, cell_size_h)

        width = height = maze_size * cell_size
        screen = pygame.display.set_mode((width, height))

        #  Pass cell_size to run_single_level
        won = run_single_level(spec, screen, clock, font, cell_size)
        if not won:
            return

        # Level complete splash
        screen.fill((0, 0, 0))
        msg = font.render(f" Level {spec['level']} Complete!", True, (0, 255, 0))
        screen.blit(msg, msg.get_rect(center=(width // 2, height // 2)))
        pygame.display.flip()
        pygame.time.wait(1200)

    screen.fill((0, 0, 0))
    msg = font.render(" You beat all 5 levels!", True, (255, 215, 0))
    screen.blit(msg, msg.get_rect(center=(width // 2, height // 2)))
    pygame.display.flip()
    pygame.time.wait(2000)
