from __future__ import annotations

from dataclasses import dataclass
import pygame


@dataclass(frozen=True)
class GameConfig:
    width: int = 1000
    height: int = 750
    ship_width: int = 115
    ship_height: int = 155
    enemy_reload_event: int = 20
    fps: int = 120
    background_speed: float = 1.0


SUPER_KEY_1 = pygame.K_z
SUPER_KEY_2 = pygame.K_x
SUPER_1_KEYS = {SUPER_KEY_1, pygame.K_1, pygame.K_KP1}
SUPER_2_KEYS = {SUPER_KEY_2, pygame.K_2, pygame.K_KP2}
