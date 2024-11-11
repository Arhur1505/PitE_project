# Możesz tu umieścić funkcje pomocnicze, np. do ładowania zasobów
import pygame
import os

def load_image(name, colorkey=None):
    fullname = os.path.join('assets', 'images', name)
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image.set_colorkey(colorkey)
    return image

def load_sound(name):
    fullname = os.path.join('assets', 'sounds', name)
    return pygame.mixer.Sound(fullname)
