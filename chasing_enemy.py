import heapq
from enemy import Enemy

class ChasingEnemy(Enemy):
    def __init__(self, row, col, maze, player):
        super().__init__(row, col, maze, [])
        self.player = player

    def update(self):
        path = self.maze.astar((self.row, self.col), (self.player.row, self.player.col))
        if path and len(path) > 1:
            next_cell = path[1]
            self.row, self.col = next_cell
