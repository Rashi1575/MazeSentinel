import pygame

RED = (255, 0, 0)

class Enemy:
    def __init__(self, row, col, maze, path):
        self.row = row
        self.col = col
        self.maze = maze
        self.path = path
        self.step = 0
        self.alive = True
        self.forward = True
        self.index = 0
        self.move_delay = 15   # frames to wait before moving again
        self.move_counter = 0

    def update(self):
        self.move_counter += 1
        if self.move_counter < self.move_delay:
            return  # skip movement until delay is reached

        self.move_counter = 0  # reset delay

        if self.forward:
            self.index += 1
            if self.index >= len(self.path):
                self.index = len(self.path) - 2
                self.forward = False
        else:
            self.index -= 1
            if self.index < 0:
                self.index = 1
                self.forward = True

        self.row, self.col = self.path[self.index]

    def draw(self, screen, cell_size, image):
        screen.blit(image, (self.col * cell_size, self.row * cell_size))

    def position(self):
        return self.path[self.index]
