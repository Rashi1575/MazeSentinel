import random
import pygame
from maze import Maze
from player import Player
from enemy import Enemy
from chasing_enemy import ChasingEnemy
from assets import load_assets

cell_size = 30

def run_single_level(spec, screen, clock, font):
    size = spec["size"]
    patrol_count = spec["patrol"]
    chase_count = spec["chase"]
    level_number = spec["level"]

    maze = Maze(size, size)
    player = Player(0, 0, cell_size)
    goal = (size - 1, size - 1)
    assets = load_assets(cell_size)

    enemies = []

    for i in range(patrol_count):
        r = size // 2 + i
        path = [(r, 1), (r, 2)]
        enemies.append(Enemy(path[0][0], path[0][1], maze, path))

    for i in range(chase_count):
        spawn_r, spawn_c = maze.enemy_pos_list[i]
        enemies.append(ChasingEnemy(spawn_r, spawn_c, maze, player))

    screen.fill((0, 0, 0))
    splash = font.render(f"🚀 Level {level_number} starting...", True, (0, 255, 255))
    screen.blit(splash, splash.get_rect(center=(screen.get_width()//2, screen.get_height()//2)))
    pygame.display.flip()
    pygame.time.wait(1500)

    defeated = 0
    running = True

    def draw_legend():
        lines = [
            f"Level {level_number}/5",
            f"Keys: {player.keys}",
            f"Shields: {player.shield_uses}",
            f"Enemies Defeated: {defeated}",
        ]
        for i, txt in enumerate(lines):
            img = font.render(txt, True, (255, 255, 255))
            screen.blit(img, (8, 8 + i * 20))

    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            elif ev.type == pygame.KEYDOWN:
                moved = False
                if ev.key == pygame.K_w:
                    player.move("up", maze)
                    moved = True
                elif ev.key == pygame.K_s:
                    player.move("down", maze)
                    moved = True
                elif ev.key == pygame.K_a:
                    player.move("left", maze)
                    moved = True
                elif ev.key == pygame.K_d:
                    player.move("right", maze)
                    moved = True

                if moved:
                    for e in enemies:
                        if isinstance(e, ChasingEnemy):
                            e.update()

        if (player.row, player.col) in maze.keys[:]:
            player.keys += 1
            maze.keys.remove((player.row, player.col))

        for ptype, lst in maze.powerups.items():
            if (player.row, player.col) in lst[:]:
                player.apply_powerup(ptype)
                lst.remove((player.row, player.col))

        for e in enemies[:]:
            if not isinstance(e, ChasingEnemy):  # patrollers update continuously
                e.update()
            if (e.row, e.col) == (player.row, player.col):
                if player.shield_uses:
                    enemies.remove(e)
                    defeated += 1
                    player.consume_shield()
                else:
                    return False

        if (player.row, player.col) == goal:
            screen.fill((0, 0, 0))
            msg = font.render(f"🎉 You won Level {level_number}!", True, (0, 255, 0))
            screen.blit(msg, msg.get_rect(center=(screen.get_width()//2, screen.get_height()//2)))
            pygame.display.flip()
            pygame.time.wait(1500)
            return True

        screen.fill((0, 0, 0))
        maze.draw(screen, cell_size)
        maze.draw_keys(screen, cell_size, assets)
        maze.draw_doors(screen, cell_size, assets)
        maze.draw_powerups(screen, cell_size, assets)

        screen.blit(assets["goal"], (goal[1] * cell_size, goal[0] * cell_size))
        player.draw(screen, cell_size, assets["player"])
        for e in enemies:
            img_key = "enemy"
            e.draw(screen, cell_size, assets[img_key])

        draw_legend()
        pygame.display.flip()
        clock.tick(60)
