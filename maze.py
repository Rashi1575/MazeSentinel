import random
import pygame
import networkx as nx
# from math import dist
import heapq

# ───────── Cell ─────────
class Cell:
    def __init__(self, row, col):
        self.row   = row
        self.col   = col
        self.visited = False
        self.walls = {"top": True, "right": True, "bottom": True, "left": True}

# ───────── Maze ─────────
class Maze:
    def __init__(self, rows, cols):
        self.rows, self.cols = rows, cols
        self.grid = [[Cell(r, c) for c in range(cols)] for r in range(rows)]

        # containers (filled later)
        self.keys     = []
        self.doors    = []
        self.powerups = {"speed": [], "invisibility": [], "shield": []}
        self.enemy_pos_list = []
        self.goal = (rows - 1, cols - 1)

        self._generate_valid_maze()

    # ── DFS carve ──
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
                cell.walls   = {"top": True, "right": True, "bottom": True, "left": True}
        self._dfs(self.grid[0][0])

    def _unvisited_neighbors(self, cell):
        r, c = cell.row, cell.col
        out = []
        if r > 0            and not self.grid[r-1][c].visited: out.append(self.grid[r-1][c])
        if r < self.rows-1  and not self.grid[r+1][c].visited: out.append(self.grid[r+1][c])
        if c > 0            and not self.grid[r][c-1].visited: out.append(self.grid[r][c-1])
        if c < self.cols-1  and not self.grid[r][c+1].visited: out.append(self.grid[r][c+1])
        return out

    def _remove_walls(self, a, b):
        dx, dy = b.col - a.col, b.row - a.row
        if dx == 1:  a.walls["right"]  = b.walls["left"]   = False
        if dx == -1: a.walls["left"]   = b.walls["right"]  = False
        if dy == 1:  a.walls["bottom"] = b.walls["top"]    = False
        if dy == -1: a.walls["top"]    = b.walls["bottom"] = False


    # ── Main generator ensuring ordered path ──
    def _generate_valid_maze(self):
        while True:
            self._fresh_maze()  # carve a new DFS maze

            # 1️⃣ Build graph of all open passages
            G = nx.Graph()
            for r in range(self.rows):
                for c in range(self.cols):
                    cell = self.grid[r][c]
                    if not cell.walls["right"]  and c < self.cols-1:
                        G.add_edge((r, c), (r, c + 1))
                    if not cell.walls["bottom"] and r < self.rows-1:
                        G.add_edge((r, c), (r + 1, c))

            start = (0, 0)
            goal  = self.goal

            # 2️⃣ If no path, regenerate
            try:
                path = nx.shortest_path(G, start, goal)
            except nx.NetworkXNoPath:
                continue

            if len(path) < 6:      # need space for all items
                continue

            # 3️⃣ Pick indices along that path
            shield1_idx = len(path) // 6          # first shield
            shield2_idx = len(path) // 4          # (level‑2 only)
            key_idx     = len(path) // 3
            door_idx    = len(path) // 2
            enemyA_idx  = 2 * len(path) // 7      # first enemy
            enemyB_idx  = 4 * len(path) // 5      # starting search for 2nd enemy

            # 4️⃣ Assign shields
            if self.rows == 14:  # Level 2 (size 14×14) → two shields
                self.powerups["invisibility"] = [path[shield1_idx], path[shield2_idx]]
            else:                # all other levels → one shield
                self.powerups["invisibility"] = [path[shield1_idx]]

            # 5️⃣ Assign key and door
            self.keys  = [path[key_idx]]
            self.doors = [path[door_idx]]

            # 6️⃣ Choose two enemies ≥ 10 Manhattan tiles apart
            enemyA = path[enemyA_idx]
            min_dist = 10  # Manhattan‑distance threshold
            enemyB = None
            for i in range(enemyB_idx, len(path)):
                cand = path[i]
                if abs(cand[0] - enemyA[0]) + abs(cand[1] - enemyA[1]) >= min_dist:
                    enemyB = cand
                    break
            # Fallback if no distant spot found
            if enemyB is None:
                enemyB = path[min(len(path) - 1, enemyB_idx + min_dist)]

            self.enemy_pos_list = [enemyA, enemyB]

            break  # valid maze generated


    # allow game.py to spawn enemies
    def get_enemy_spawns(self):
        return self.enemy_pos_list

    # ── DRAW helpers (no offsets) ──
    def draw(self, screen, cs):
        white = (255, 255, 255)
        wall_thickness = 8  # Increased thickness here

        for row in self.grid:
            for cell in row:
                x, y = cell.col * cs, cell.row * cs
                if cell.walls["top"]:
                    pygame.draw.line(screen, white, (x, y), (x + cs, y), wall_thickness)
                if cell.walls["right"]:
                    pygame.draw.line(screen, white, (x + cs, y), (x + cs, y + cs), wall_thickness)
                if cell.walls["bottom"]:
                    pygame.draw.line(screen, white, (x, y + cs), (x + cs, y + cs), wall_thickness)
                if cell.walls["left"]:
                    pygame.draw.line(screen, white, (x, y), (x, y + cs), wall_thickness)

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
        """Return shortest path from start to goal using A* algorithm."""
        def heuristic(a, b):
            return abs(a[0]-b[0]) + abs(a[1]-b[1])  # Manhattan distance

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

        # Reconstruct path
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
        """Return walkable neighbors of a cell (row, col)."""
        r, c = cell
        neighbors = []
        if r > 0 and not self.grid[r][c].walls["top"]:      neighbors.append((r - 1, c))
        if r < self.rows - 1 and not self.grid[r][c].walls["bottom"]: neighbors.append((r + 1, c))
        if c > 0 and not self.grid[r][c].walls["left"]:     neighbors.append((r, c - 1))
        if c < self.cols - 1 and not self.grid[r][c].walls["right"]:  neighbors.append((r, c + 1))
        return neighbors
