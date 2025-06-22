import pygame
import os

def load_image(name, cell_size):
    path = os.path.join("assets", name)
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(img, (cell_size, cell_size))

def load_assets(cell_size):
    return {
        "player": load_image("player.png", cell_size),
        "enemy": load_image("enemy.png", cell_size),
        "goal": load_image("goal.png", cell_size),
        "key": load_image("key.png", cell_size),
        "door": load_image("door.png", cell_size),
        "shield": load_image("shield.png", cell_size),
        "speed": load_image("speed.png", cell_size),
        "invisibility": load_image("invisibility.png", cell_size),
    }
