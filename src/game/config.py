from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GameConfig:
    width: int = 1000
    height: int = 750
    ship_width: int = 115
    ship_height: int = 155
    enemy_reload_event: int = 20
    fps: int = 120
    background_speed: float = 1.0
