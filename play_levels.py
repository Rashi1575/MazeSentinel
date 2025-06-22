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

def play_from_level(start_level=1):
    pygame.font.init()
    font = pygame.font.SysFont(None, 24)
    clock = pygame.time.Clock()

    for i in range(start_level - 1, len(LEVELS)):
        spec = LEVELS[i]
        cell_size = 30
        width = height = spec["size"] * cell_size
        screen = pygame.display.set_mode((width, height))

        won = run_single_level(spec, screen, clock, font)
        if not won:
            return  # player died or quit

        # Level complete splash
        screen.fill((0, 0, 0))
        msg = font.render(f"✅ Level {spec['level']} Complete!", True, (0, 255, 0))
        screen.blit(msg, msg.get_rect(center=(width // 2, height // 2)))
        pygame.display.flip()
        pygame.time.wait(1200)

    # Final completion screen
    screen.fill((0, 0, 0))
    msg = font.render("🏆 You beat all 5 levels!", True, (255, 215, 0))
    screen.blit(msg, msg.get_rect(center=(width // 2, height // 2)))
    pygame.display.flip()
    pygame.time.wait(2000)

