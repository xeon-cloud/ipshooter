from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EnemyTemplate:
    image: str
    hp: int
    speed_mult: float
    reward: int


@dataclass(frozen=True)
class GameProperties:
    enemies_speed: float
    enemies_hp_scale: float
    timer_enemies_ms: int
    need_score: int
    max_enemies_on_screen: int
    miss_penalty: int
    player_speed: int
    reload_time: float
    player_health: int
    fire_rate: float


class StockProperties:
    enemies_speed = 1.0
    enemies_hp_scale = 1.0
    player_speed = 7
    timer_enemies_ms = 820
    min_timer_enemies_ms = 230
    need_score = 22


def compute_game_properties(level_diff: int, stats: dict) -> GameProperties:
    lvl = max(1, level_diff)
    growth = lvl - 1

    enemies_speed = min(3.2, StockProperties.enemies_speed + 0.09 * growth + 0.02 * (growth ** 1.15))
    enemies_hp_scale = StockProperties.enemies_hp_scale + 0.16 * growth + 0.02 * (growth ** 1.25)
    timer_enemies_ms = max(
        StockProperties.min_timer_enemies_ms,
        int(round(StockProperties.timer_enemies_ms - (22 * growth + 2.5 * (growth ** 1.35))))
    )
    need_score = int(round(StockProperties.need_score + 5 * growth + 1.8 * (growth ** 1.2)))
    max_enemies = min(18, 4 + growth // 2 + int(growth ** 0.5))
    miss_penalty = min(6, 1 + growth // 4)

    return GameProperties(
        enemies_speed=enemies_speed,
        enemies_hp_scale=enemies_hp_scale,
        timer_enemies_ms=timer_enemies_ms,
        need_score=need_score,
        max_enemies_on_screen=max_enemies,
        miss_penalty=miss_penalty,
        player_speed=StockProperties.player_speed,
        reload_time=float(stats["Cooldown"]),
        player_health=int(stats["Health"]),
        fire_rate=float(stats["FireRate"]),
    )


def enemy_templates() -> dict[int, EnemyTemplate]:
    return {
        1: EnemyTemplate("enemy1.png", hp=8, speed_mult=0.90, reward=1),
        2: EnemyTemplate("enemy2.png", hp=10, speed_mult=1.00, reward=2),
        3: EnemyTemplate("enemy3.png", hp=12, speed_mult=1.08, reward=2),
        4: EnemyTemplate("enemy4.png", hp=14, speed_mult=1.15, reward=3),
        5: EnemyTemplate("enemy5.png", hp=18, speed_mult=1.22, reward=4),
    }


def enemy_spawn_weights(level_diff: int) -> dict[int, int]:
    growth = max(0, level_diff - 1)
    return {
        1: max(20, 50 - 3 * growth),
        2: 32 + growth,
        3: 10 + 2 * max(0, growth - 1),
        4: 4 + 2 * max(0, growth - 4),
        5: 1 + 2 * max(0, growth - 7),
    }
