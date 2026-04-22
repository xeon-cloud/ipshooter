from __future__ import annotations

import os
import time
import pygame

import methods


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x: int, image: str, hp: int, offset_x: float, speed: float, reward: int) -> None:
        super().__init__()
        self.image = pygame.image.load(f"images/{image}")
        self.image = pygame.transform.scale(self.image, (90, 90))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = 100

        self.hp = hp
        self.reward = reward
        self.speed = speed
        self.offset_x = offset_x
        self._contusion_tick = 0

    def update(self, contusion: bool, world_width: int) -> None:
        if contusion:
            self._contusion_tick = (self._contusion_tick + 1) % 4
            if self._contusion_tick != 3:
                return

        self.rect.y += self.speed
        self.rect.x += self.offset_x
        if self.rect.x < 0 or self.rect.x + self.image.get_width() > world_width:
            self.offset_x = -self.offset_x


class Laser(pygame.sprite.Sprite):
    def __init__(self, x: float, y: float) -> None:
        super().__init__()
        bullet_num = methods.getBulletCount()
        self.image = pygame.image.load(f"images/bullet_{bullet_num}.png")
        self.image = pygame.transform.scale(self.image, (20, 38))
        self.rect = self.image.get_rect()
        self.rect.x = int(x)
        self.rect.y = int(y)
        self.speed = 8

    def update(self) -> None:
        self.rect.y -= self.speed


class Player(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, width: int, height: int, player_speed: int) -> None:
        super().__init__()
        ship_path = methods.getSpaceship() if methods.getLvl() <= 20 else "Ships/ship_lvl_20.png"
        self.image = pygame.image.load(ship_path)
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = player_speed

        self._thruster_sizes = {
            "1, 2, 3, 4, 5, 6, 7, 8, 9": (25, 50),
            "10, 11, 12, 13, 14": (40, 70),
            f"{', '.join([str(i) for i in range(15, 500)])}": (40, 70),
        }
        self._thruster_frames = self._load_thruster_frames()
        self._frame_index = 0
        self._next_thruster_frame_at = time.time()

    def _load_thruster_frames(self) -> list[pygame.Surface]:
        frames: list[pygame.Surface] = []
        ship_index = methods.getIndexShip()

        for frame_index in range(8):
            image = pygame.image.load(os.path.join("fires", f"00{frame_index}.png"))
            for key, size in self._thruster_sizes.items():
                if ship_index in list(map(int, key.split(", "))):
                    image = pygame.transform.scale(pygame.transform.rotate(image, 180), size)
            frames.append(image)
        return frames

    def _thruster_positions(self) -> list[tuple[float, float]]:
        ship_index = methods.getIndexShip()
        mapping = {
            "1, 2, 3, 4": [
                (self.rect.x + self.image.get_width() // 2.5, self.rect.y + self.image.get_height() - 12),
            ],
            "5, 6, 7, 8, 9": [
                (self.rect.x + self.image.get_width() // 8, self.rect.y + self.image.get_height() + 3),
                (self.rect.x + self.image.get_width() // 1.5, self.rect.y + self.image.get_height() + 3),
            ],
            "10, 11, 12, 13, 14": [
                (self.rect.x + self.image.get_width() // 3, self.rect.y + self.image.get_height() - 10),
            ],
            f"{', '.join([str(i) for i in range(15, 500)])}": [
                (self.rect.x + self.image.get_width() // 8, self.rect.y + self.image.get_height() + 3),
                (self.rect.x + self.image.get_width() // 1.5, self.rect.y + self.image.get_height() + 3),
            ],
        }

        for key, positions in mapping.items():
            if ship_index in list(map(int, key.split(", "))):
                return positions
        return []

    def draw_thrusters(self, screen: pygame.Surface) -> None:
        if time.time() >= self._next_thruster_frame_at:
            self._frame_index = (self._frame_index + 1) % len(self._thruster_frames)
            self._next_thruster_frame_at = time.time() + 0.01

        frame = self._thruster_frames[self._frame_index]
        for pos in self._thruster_positions():
            screen.blit(frame, pos)
