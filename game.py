import random
import pygame
from maze import Maze
from player import Player
from enemy import Enemy
from chasing_enemy import ChasingEnemy
from assets import load_assets

def run_single_level(spec, screen, clock, font, cell_size):
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
        start_r = 2 + i * 6
        start_c = 2
        path = [
            (start_r, start_c), (start_r, start_c + 1), (start_r, start_c + 2), (start_r, start_c + 3),
            (start_r + 1, start_c + 3), (start_r + 2, start_c + 3), (start_r + 3, start_c + 3),
            (start_r + 3, start_c + 2), (start_r + 3, start_c + 1), (start_r + 3, start_c),
            (start_r + 2, start_c), (start_r + 1, start_c)
        ]
        path = [(r, c) for r, c in path if 0 <= r < size and 0 <= c < size]
        if path:
            enemies.append(Enemy(path[0][0], path[0][1], maze, path))

    for i in range(chase_count):
        spawn_r, spawn_c = maze.enemy_pos_list[i]
        enemies.append(ChasingEnemy(spawn_r, spawn_c, maze, player))

    pygame.mixer.init()
    click_sound = pygame.mixer.Sound("click.mp3")
    step_sound = pygame.mixer.Sound("wood-step-sample-1-47664.mp3")
    caught_sound = pygame.mixer.Sound("explode3-87806.mp3")  # 🎵 Load caught sound
    pygame.mixer.music.load("maze_soundtrack.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

    btn_font = pygame.font.SysFont('Comic Sans MS', 30, bold=True)
    legend_font = pygame.font.SysFont('Georgia', 24)

    splash = font.render(f" Level {level_number} starting...", True, (0, 255, 255))
    screen.fill((0, 0, 0))
    screen.blit(splash, splash.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2)))
    pygame.display.flip()
    pygame.time.wait(1500)

    defeated = 0
    running = True
    paused = False
    show_pause_menu = False
    pause_btn_rect = pygame.Rect(screen.get_width() - 60, 10, 50, 50)

    def draw_legend():
        legend_lines = [
            f"Level {level_number}/5",
            f"Keys: {player.keys}",
            f"Shields: {player.shield_uses}",
            f"Enemies Defeated: {defeated}"
        ]
        spacing = 32
        total_height = spacing * len(legend_lines)
        box_width = 240
        start_x = screen.get_width() - box_width - 20
        start_y = (screen.get_height() - total_height) // 2

        for i, text in enumerate(legend_lines):
            txt_surface = legend_font.render(text, True, (255, 255, 255))
            text_rect = txt_surface.get_rect(center=(start_x + box_width // 2, start_y + i * spacing))
            screen.blit(txt_surface, text_rect)

        pygame.draw.rect(screen, (50, 50, 50), pause_btn_rect, border_radius=8)
        pygame.draw.rect(screen, (255, 255, 255), pause_btn_rect, 2, border_radius=8)
        bar_width = 8
        bar_height = 24
        gap = 10
        center_x = pause_btn_rect.centerx
        center_y = pause_btn_rect.centery
        pygame.draw.rect(screen, (255, 255, 255),
                         (center_x - gap // 2 - bar_width, center_y - bar_height // 2, bar_width, bar_height))
        pygame.draw.rect(screen, (255, 255, 255),
                         (center_x + gap // 2, center_y - bar_height // 2, bar_width, bar_height))

    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.mixer.music.stop()
                return False
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                if pause_btn_rect.collidepoint(*pygame.mouse.get_pos()):
                    click_sound.play()
                    paused = True
                    show_pause_menu = True
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
                    step_sound.play()
                    for e in enemies:
                        if isinstance(e, ChasingEnemy):
                            e.update()

        if paused and show_pause_menu:
            menu_result = show_pause_menu_screen(screen, clock, click_sound, spec, font, cell_size)
            if menu_result == 'exit':
                pygame.mixer.music.stop()
                return None
            elif menu_result == 'restart':
                pygame.mixer.music.stop()
                return run_single_level(spec, screen, clock, font, cell_size)
            paused = False
            show_pause_menu = False
            continue


        if (player.row, player.col) in maze.keys[:]:
            player.keys += 1
            maze.keys.remove((player.row, player.col))

        for ptype, lst in maze.powerups.items():
            if (player.row, player.col) in lst[:]:
                player.apply_powerup(ptype)
                lst.remove((player.row, player.col))

        for e in enemies[:]:
            if not isinstance(e, ChasingEnemy):
                e.update()
            if (e.row, e.col) == (player.row, player.col):
                if player.shield_uses:
                    enemies.remove(e)
                    defeated += 1
                    player.consume_shield()
                else:
                    caught_sound.play()  # 🎵 Play caught sound
                    pygame.mixer.music.stop()
                    action = show_caught_screen(screen, clock, click_sound, spec, font, cell_size)
                    if action == 'retry':
                        return run_single_level(spec, screen, clock, font, cell_size)
                    else:
                        return None

        if (player.row, player.col) == goal:
            screen.fill((0, 0, 0))
            msg = font.render(f" You won Level {level_number}!", True, (0, 255, 0))
            screen.blit(msg, msg.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2)))
            pygame.display.flip()
            pygame.time.wait(1500)
            pygame.mixer.music.stop()
            return True

        screen.fill((0, 0, 0))
        
        maze.draw(screen, cell_size)
        maze.draw_keys(screen, cell_size, assets)
        maze.draw_doors(screen, cell_size, assets)
        maze.draw_powerups(screen, cell_size, assets)

        screen.blit(assets["goal"], (goal[1] * cell_size, goal[0] * cell_size))
        player.draw(screen, cell_size, assets["player"])
        for e in enemies:
            e.draw(screen, cell_size, assets["enemy"])

        draw_legend()

        pygame.display.flip()
        clock.tick(60)


def show_pause_menu_screen(screen, clock, click_sound, spec, font, cell_size):
    btn_font = pygame.font.SysFont('Comic Sans MS', 30, bold=True)
    overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    btn_w, btn_h = 300, 60
    center_x = screen.get_width() // 2
    y_base = screen.get_height() // 2 - 90
    resume_rect = pygame.Rect(center_x - btn_w // 2, y_base, btn_w, btn_h)
    restart_rect = pygame.Rect(center_x - btn_w // 2, y_base + 80, btn_w, btn_h)
    exit_rect = pygame.Rect(center_x - btn_w // 2, y_base + 160, btn_w, btn_h)

    for rect, text in [(resume_rect, " RESUME"), (restart_rect, " RESTART"), (exit_rect, " EXIT")]:
        pygame.draw.rect(screen, (20, 25, 45), rect, border_radius=12)
        pygame.draw.rect(screen, (100, 255, 255), rect, 3, border_radius=12)
        label = btn_font.render(text, True, (255, 255, 255))
        screen.blit(label, label.get_rect(center=rect.center))

    pygame.display.flip()

    waiting = True
    while waiting:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if resume_rect.collidepoint(mx, my):
                    click_sound.play()
                    return 'resume'
                elif restart_rect.collidepoint(mx, my):
                    click_sound.play()
                    return 'restart'
                elif exit_rect.collidepoint(mx, my):
                    click_sound.play()
                    return 'exit'
        clock.tick(15)


def show_caught_screen(screen, clock, click_sound, spec, font, cell_size):
    overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    btn_font = pygame.font.SysFont('Georgia', 24, bold=True)
    title_font = pygame.font.SysFont('Georgia', 36, bold=True)

    # "You were caught!" message
    caught_text = title_font.render("You were caught!", True, (255, 50, 50))
    screen.blit(caught_text, caught_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 120)))

    btn_w, btn_h = 300, 60
    center_x = screen.get_width() // 2
    y_base = screen.get_height() // 2 - 30
    retry_rect = pygame.Rect(center_x - btn_w // 2, y_base, btn_w, btn_h)
    exit_rect = pygame.Rect(center_x - btn_w // 2, y_base + 80, btn_w, btn_h)

    for rect, text in [(retry_rect, "RETRY"), (exit_rect, "EXIT")]:
        pygame.draw.rect(screen, (20, 25, 45), rect, border_radius=12)
        pygame.draw.rect(screen, (100, 255, 255), rect, 3, border_radius=12)
        label = btn_font.render(text, True, (255, 255, 255))
        screen.blit(label, label.get_rect(center=rect.center))

    pygame.display.flip()

    waiting = True
    while waiting:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if retry_rect.collidepoint(mx, my):
                    click_sound.play()
                    return 'retry'
                elif exit_rect.collidepoint(mx, my):
                    click_sound.play()
                    return 'exit'
        clock.tick(15)
