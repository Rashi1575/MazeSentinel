import pygame
from game import run_single_level

# ─── Initialization ────────────────────────────────
pygame.init()
screen = pygame.display.set_mode((400, 400))  # Temporary placeholder size
pygame.display.set_caption("Maze Sentinel – Levels")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# ─── Level Specifications ───────────────────────────
LEVELS = [
    {"size": 12, "patrol": 1, "chase": 0, "level": 1},
    {"size": 14, "patrol": 2, "chase": 0, "level": 2},
    {"size": 16, "patrol": 0, "chase": 1, "level": 3},
    {"size": 18, "patrol": 0, "chase": 1, "level": 4},
    {"size": 20, "patrol": 0, "chase": 1, "level": 5},
]

# ─── Level Loop ─────────────────────────────────────
for spec in LEVELS:
    cell_size = 30
    width = height = spec["size"] * cell_size
    screen = pygame.display.set_mode((width, height))  # Resize window

    won = run_single_level(spec, screen, clock, font)
    if not won:
        break  # Player died or exited

    # ─── Show "Level Complete" splash ───
    screen.fill((0, 0, 0))
    splash = font.render("✅ Level Complete!", True, (0, 255, 0))
    rect = splash.get_rect(center=(width // 2, height // 2))
    screen.blit(splash, rect)
    pygame.display.flip()
    pygame.time.wait(1200)

# ─── All Levels Completed ───────────────────────────
else:
    screen.fill((0, 0, 0))
    final = font.render("🏆 You beat all 5 levels!", True, (255, 215, 0))
    rect = final.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.blit(final, rect)
    pygame.display.flip()
    pygame.time.wait(2000)

pygame.quit()
