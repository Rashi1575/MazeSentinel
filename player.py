import pygame

class Player:
    def __init__(self, row, col, cell_size):
        self.row = row
        self.col = col
        self.cell_size = cell_size
        self.x = col * cell_size
        self.y = row * cell_size
        self.speed = 1
        self.invisible = False
        self.stack = []
        self.keys = 0
        self.powerup = None
        self.update_pixel_pos()
        self.shield_uses = 0

    def move(self, direction, maze):
        cell = maze.grid[self.row][self.col]

        if direction == "up" and self.row > 0:
            if not cell.walls["top"]:
                if (self.row - 1, self.col) in maze.doors and self.keys > 0:
                    maze.doors.remove((self.row - 1, self.col))
                    self.keys -= 1
                if (self.row - 1, self.col) not in maze.doors:
                    self.row -= 1

        elif direction == "down" and self.row < maze.rows - 1:
            if not cell.walls["bottom"]:
                if (self.row + 1, self.col) in maze.doors and self.keys > 0:
                    maze.doors.remove((self.row + 1, self.col))
                    self.keys -= 1
                if (self.row + 1, self.col) not in maze.doors:
                    self.row += 1

        elif direction == "left" and self.col > 0:
            if not cell.walls["left"]:
                if (self.row, self.col - 1) in maze.doors and self.keys > 0:
                    maze.doors.remove((self.row, self.col - 1))
                    self.keys -= 1
                if (self.row, self.col - 1) not in maze.doors:
                    self.col -= 1

        elif direction == "right" and self.col < maze.cols - 1:
            if not cell.walls["right"]:
                if (self.row, self.col + 1) in maze.doors and self.keys > 0:
                    maze.doors.remove((self.row, self.col + 1))
                    self.keys -= 1
                if (self.row, self.col + 1) not in maze.doors:
                    self.col += 1

        self.update_pixel_pos()

    def update_pixel_pos(self):
        self.x = self.col * self.cell_size
        self.y = self.row * self.cell_size
    
    def draw(self, screen, cell_size, image):
        screen.blit(image, (self.col * cell_size, self.row * cell_size))


    # def draw(self, screen, cell_size):
    #     color = (0, 255, 255) if self.invisible else (255, 0, 0)
    #     pygame.draw.rect(screen, color, (self.x, self.y, cell_size, cell_size))

    def apply_powerup(self, ptype):
        # called when you step on a green or purple circle
        if ptype in ("speed", "invisibility"):
            self.powerup = ptype
            if ptype == "speed":
                self.speed = 2
            elif ptype == "invisibility":
                self.invisible = True
                self.shield_uses += 1  # ← every invisibility pickup = +1 shield

    def consume_shield(self):
        if self.shield_uses > 0:
            self.shield_uses -= 1
        if self.shield_uses == 0:
            # shield exhausted → lose invisibility effect
            self.invisible = False
            if self.powerup == "invisibility":
                self.powerup = None

    def reset_powerups(self):
        self.speed = 1
        self.invisible = False
        self.powerup = None
