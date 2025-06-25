import random
import pygame
import networkx as nx
import heapq
selected_theme = "ice"  # Default theme
THEMES = {
    "jungle": {
        "background": (25, 35, 25),
        "wall_light": (120, 200, 120),
        "wall_dark": (30, 100, 30)
    },
    "Cyber": {
        "background": (10, 10, 10),
        "wall_light": (0, 255, 200),
        "wall_dark": (0, 120, 100)
    },
    "ice": {
        "background": (0, 20, 50),
        "wall_light": (180, 240, 255),
        "wall_dark": (80, 160, 220)
    },
    "Dungeon": {
        "background": (30, 30, 30),
        "wall_light": (150, 150, 150),
        "wall_dark": (80, 80, 80)
    },
    "Nebula / Space": {
        "background": (10, 10, 30),
        "wall_light": (130, 80, 255),
        "wall_dark":  (60, 20, 120)
    }
}

class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.visited = False
        self.walls = {"top": True, "right": True, "bottom": True, "left": True}

class Maze:
    def __init__(self, rows, cols, theme_name=None, wall_thickness=8):
        global selected_theme
        self.rows, self.cols = rows, cols
        self.grid = [[Cell(r, c) for c in range(cols)] for r in range(rows)]
        self.keys = []
        self.doors = []
        self.powerups = {"speed": [], "invisibility": [], "shield": []}
        self.enemy_pos_list = []
        self.goal = (rows - 1, cols - 1)

        # Use the global theme if not passed explicitly
        self.theme = THEMES[theme_name or selected_theme]
        self.wall_thickness = wall_thickness

        self._generate_valid_maze()

    def _dfs(self, cell):
        cell.visited = True
        while (nbs := self._unvisited_neighbors(cell)):
            nxt = random.choice(nbs)
            self._remove_walls(cell, nxt)
            self._dfs(nxt)

    def _fresh_maze(self):
        for row in self.grid:
            for cell in row:
                cell.visited = False
                cell.walls = {"top": True, "right": True, "bottom": True, "left": True}
        self._dfs(self.grid[0][0])

    def _unvisited_neighbors(self, cell):
        r, c = cell.row, cell.col
        out = []
        if r > 0 and not self.grid[r - 1][c].visited:
            out.append(self.grid[r - 1][c])
        if r < self.rows - 1 and not self.grid[r + 1][c].visited:
            out.append(self.grid[r + 1][c])
        if c > 0 and not self.grid[r][c - 1].visited:
            out.append(self.grid[r][c - 1])
        if c < self.cols - 1 and not self.grid[r][c + 1].visited:
            out.append(self.grid[r][c + 1])
        return out

    def _remove_walls(self, a, b):
        dx, dy = b.col - a.col, b.row - a.row
        if dx == 1:
            a.walls["right"] = b.walls["left"] = False
        if dx == -1:
            a.walls["left"] = b.walls["right"] = False
        if dy == 1:
            a.walls["bottom"] = b.walls["top"] = False
        if dy == -1:
            a.walls["top"] = b.walls["bottom"] = False

    def _generate_valid_maze(self):
        while True:
            self._fresh_maze()

            G = nx.Graph()
            for r in range(self.rows):
                for c in range(self.cols):
                    cell = self.grid[r][c]
                    if not cell.walls["right"] and c < self.cols - 1:
                        G.add_edge((r, c), (r, c + 1))
                    if not cell.walls["bottom"] and r < self.rows - 1:
                        G.add_edge((r, c), (r + 1, c))

            start, goal = (0, 0), self.goal
            try:
                path1 = nx.shortest_path(G, start, goal)
            except nx.NetworkXNoPath:
                continue

            if len(path1) < 6:
                continue

            if self.rows >= 16:
                G = self._force_strict_second_path(G)

            try:
                path = nx.shortest_path(G, start, goal)
            except nx.NetworkXNoPath:
                continue

            # Configure number of shields, keys, and doors based on level
            shield_count = 1
            key_count = 1
            door_count = 1

            if self.rows == 16:
                shield_count = 1
                key_count = 3
                door_count = 3
            elif self.rows == 18:
                shield_count = 2
                key_count = 3
                door_count = 3
            elif self.rows == 20:
                shield_count = 3
                key_count = 3
                door_count = 3

            total_len = len(path)

            # Shields first
            shield_indices = [total_len * (i + 1) // (shield_count + key_count + door_count + 3) for i in range(shield_count)]
            # Keys next
            key_indices = [total_len * (i + 1 + shield_count) // (shield_count + key_count + door_count + 3) for i in range(key_count)]
            # Doors last
            door_indices = [total_len * (i + 1 + shield_count + key_count) // (shield_count + key_count + door_count + 3) for i in range(door_count)]

            self.powerups["invisibility"] = [path[i] for i in shield_indices]
            self.keys = [path[i] for i in key_indices]
            self.doors = [path[i] for i in door_indices]

            # Spawn enemies far away
            bottom_row = self.rows - 1
            enemyA = (bottom_row, 1)
            enemyB = (bottom_row, self.cols - 2)
            enemyC = (bottom_row // 2, self.cols - 2)

            if self.rows == 16:
                self.enemy_pos_list = [enemyA]
            elif self.rows == 18:
                self.enemy_pos_list = [enemyA, enemyB]
            elif self.rows == 20:
                self.enemy_pos_list = [enemyA, enemyB, enemyC]
            else:
                self.enemy_pos_list = [enemyA, enemyB]

            break

    def _force_strict_second_path(self, G):
        alt_start = (0, self.cols - 1)
        alt_goal = self.goal
        alt_path = self._create_manual_path(alt_start, alt_goal)
        for i in range(len(alt_path) - 1):
            self._remove_walls(self.grid[alt_path[i][0]][alt_path[i][1]], self.grid[alt_path[i + 1][0]][alt_path[i + 1][1]])
            G.add_edge(alt_path[i], alt_path[i + 1])
        return G

    def _create_manual_path(self, start, goal):
        path = [start]
        r, c = start
        goal_r, goal_c = goal

        while r < goal_r:
            r += 1
            path.append((r, c))
        while c > goal_c:
            c -= 1
            path.append((r, c))

        return path

    def get_enemy_spawns(self):
        return self.enemy_pos_list

    def draw(self, screen, cs):
        screen.fill(self.theme["background"])

        for row in self.grid:
            for cell in row:
                x, y = cell.col * cs, cell.row * cs
                if cell.walls["top"]:
                    pygame.draw.line(screen, self.theme["wall_light"], (x, y), (x + cs, y), self.wall_thickness)
                if cell.walls["left"]:
                    pygame.draw.line(screen, self.theme["wall_light"], (x, y), (x, y + cs), self.wall_thickness)
                if cell.walls["right"]:
                    pygame.draw.line(screen, self.theme["wall_dark"], (x + cs, y), (x + cs, y + cs), self.wall_thickness)
                if cell.walls["bottom"]:
                    pygame.draw.line(screen, self.theme["wall_dark"], (x, y + cs), (x + cs, y + cs), self.wall_thickness)

    def draw_keys(self, screen, cs, assets):
        for r, c in self.keys:
            screen.blit(assets["key"], (c * cs, r * cs))

    def draw_doors(self, screen, cs, assets):
        for r, c in self.doors:
            screen.blit(assets["door"], (c * cs, r * cs))

    def draw_powerups(self, screen, cs, assets):
        for r, c in self.powerups["invisibility"]:
            screen.blit(assets["shield"], (c * cs, r * cs))

    def astar(self, start, goal):
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}

        while frontier:
            _, current = heapq.heappop(frontier)
            if current == goal:
                break
            for neighbor in self._get_neighbors(current):
                new_cost = cost_so_far[current] + 1
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    priority = new_cost + heuristic(goal, neighbor)
                    heapq.heappush(frontier, (priority, neighbor))
                    came_from[neighbor] = current

        if goal not in came_from:
            return []

        path = []
        curr = goal
        while curr != start:
            path.append(curr)
            curr = came_from[curr]
        path.append(start)
        path.reverse()
        return path

    def _get_neighbors(self, cell):
        r, c = cell
        neighbors = []
        if r > 0 and not self.grid[r][c].walls["top"]:
            neighbors.append((r - 1, c))
        if r < self.rows - 1 and not self.grid[r][c].walls["bottom"]:
            neighbors.append((r + 1, c))
        if c > 0 and not self.grid[r][c].walls["left"]:
            neighbors.append((r, c - 1))
        if c < self.cols - 1 and not self.grid[r][c].walls["right"]:
            neighbors.append((r, c + 1))
        return neighbors
def set_theme(theme):
    global selected_theme
    selected_theme = theme
