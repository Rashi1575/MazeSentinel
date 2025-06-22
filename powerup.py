import pygame

GREEN = (0, 255, 0)
CYAN = (0, 255, 255)

class PowerUp:
    def __init__(self, row, col, cell_size, effect, duration):
        self.row = row
        self.col = col
        self.cell_size = cell_size
        self.effect = effect  # 'speed', 'invisibility'
        self.duration = duration
        self.collected = False

    def draw(self, screen):
        if self.collected:
            return
        color = GREEN if self.effect == "speed" else CYAN
        x = self.col * self.cell_size + self.cell_size // 4
        y = self.row * self.cell_size + self.cell_size // 4
        size = self.cell_size // 2
        pygame.draw.circle(screen, color, (x + size // 2, y + size // 2), size // 2)

    def check_collect(self, player):
        if not self.collected and (self.row, self.col) == (player.row, player.col):
            self.collected = True
            player.apply_powerup(self.effect, self.duration)
