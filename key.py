import pygame

YELLOW = (255, 255, 0)

class Key:
    def __init__(self, row, col, cell_size, key_id):
        self.row = row
        self.col = col
        self.cell_size = cell_size
        self.collected = False
        self.key_id = key_id  # Used to match with doors

    def draw(self, screen):
        if self.collected:
            return
        x = self.col * self.cell_size + self.cell_size // 3
        y = self.row * self.cell_size + self.cell_size // 3
        size = self.cell_size // 3
        pygame.draw.rect(screen, YELLOW, (x, y, size, size))

    def check_collect(self, player):
        if not self.collected and (self.row, self.col) == (player.row, player.col):
            self.collected = True
            player.keys.append(self.key_id)

    