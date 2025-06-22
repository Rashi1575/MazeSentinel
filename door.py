import pygame
import time

BLUE = (0, 0, 255)
GRAY = (100, 100, 100)

class Door:
    def __init__(self, row, col, cell_size, required_key, time_locked=False, unlock_time=5):
        self.row = row
        self.col = col
        self.cell_size = cell_size
        self.required_key = required_key
        self.locked = True
        self.time_locked = time_locked
        self.unlock_time = unlock_time
        self.unlock_timer_start = None

    def draw(self, screen):
        color = BLUE if self.locked else GRAY
        x = self.col * self.cell_size
        y = self.row * self.cell_size
        pygame.draw.rect(screen, color, (x, y, self.cell_size, self.cell_size))

    def check_unlock(self, player):
        if self.locked and (self.row, self.col) == (player.row, player.col):
            if self.required_key in player.keys:
                self.locked = False
                player.keys.remove(self.required_key)
            elif self.time_locked:
                if self.unlock_timer_start is None:
                    self.unlock_timer_start = time.time()
                elif time.time() - self.unlock_timer_start >= self.unlock_time:
                    self.locked = False

    def blocks_player(self):
        return self.locked
