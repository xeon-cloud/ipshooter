from __future__ import annotations

import datetime
import os
import random
import time
from typing import Iterable
from dataclasses import replace

import pygame

import end
import menu
import methods
import pause_menu

from .config import GameConfig, SUPER_1_KEYS, SUPER_2_KEYS
from .difficulty import compute_game_properties, enemy_spawn_weights, enemy_templates
from .entities import Enemy, Laser, Player


class GameSession:
    def __init__(self, config: GameConfig | None = None) -> None:
        pygame.init()

        self.config = config or GameConfig()
        self.screen = pygame.display.set_mode((self.config.width, self.config.height))
        pygame.display.set_caption("Space Shooter")
        self.clock = pygame.time.Clock()

        self.background_y_offset = 1.0
        self.background_image = pygame.image.load("images/fone2.jpg")
        self.background_image = pygame.transform.scale(self.background_image, (self.config.width, self.config.height))
        self.starfield_image = self._build_starfield(100)

        self.pause_button = pygame.transform.scale(
            pygame.image.load("menu_images/pause_button.png"),
            (45, 45),
        )
        self.pause_button_rect = self.pause_button.get_rect(topleft=(10, 10))
        self.super_icon_1 = pygame.transform.scale(pygame.image.load("menu_images/super1.png"), (50, 50))
        self.super_icon_2 = pygame.transform.scale(pygame.image.load("menu_images/super2.png"), (50, 50))

        self.main_menu = menu.Menu(self.screen, self.start_new_game, width=self.config.width, height=self.config.height)
        self.main_menu.menu.enable()
        self.pause_menu = pause_menu.Menu(
            self.screen,
            self.start_new_game,
            self.disable_pause,
            width=self.config.width,
            height=self.config.height,
        )
        self.pause_menu.menu.disable()

        self.running = True
        self.loading = True
        self._init_game_state()

    # -------------------------------
    # Public API
    # -------------------------------
    def run(self) -> None:
        while self.running:
            if self.main_menu.menu.is_enabled():
                self.main_menu.menu.mainloop(self.screen)
            elif self.pause_menu.menu.is_enabled():
                self.pause_menu.menu.mainloop(self.screen)

            if self.loading:
                self._run_loading_screen()
                if not self.running:
                    continue

            self.clock.tick(self.config.fps)
            keys = pygame.key.get_pressed()
            self._apply_keyboard_movement(keys)

            self._handle_events()
            if not self.running:
                break

            self._update_supers()
            self._handle_shooting()
            self._update_entities()
            self._process_collisions()
            self._draw_frame()

        pygame.quit()

    def start_new_game(self) -> None:
        self._init_game_state()
        pygame.time.set_timer(self.config.enemy_reload_event, self.properties.timer_enemies_ms)

    def disable_pause(self) -> None:
        self.pauses.append(int(round(time.time() - self.pause_time, 0)))

    # -------------------------------
    # Initialization helpers
    # -------------------------------
    def _init_game_state(self) -> None:
        stats = methods.getData()["stats"]
        self.properties = compute_game_properties(methods.getLvlDiff(), stats)
        self.base_fire_rate = self.properties.fire_rate

        self.score = 0
        self.money = 0
        self.rewards_saved = False

        self.start_time = time.time()
        self.pauses: list[int] = []
        self.pause_time = 0.0

        self.shots_count = 0.0
        self.laser_timestamps: list[list[float]] = []
        self.is_reloading = False
        self.reload_ready_at = time.time()

        self.contusion = False
        self.supers: dict[int, list[float | bool]] = {1: [False], 2: [False]}

        self.dragging = False

        self.max_health = self.properties.player_health
        self.current_health = self.max_health

        self.enemies = pygame.sprite.Group()
        self.lasers = pygame.sprite.Group()
        self.players = pygame.sprite.Group()
        self._create_player()

    def _create_player(self) -> None:
        x = self.config.width // 2 - self.config.ship_width // 2
        y = 550
        self.player = Player(
            x=x,
            y=y,
            width=self.config.ship_width,
            height=self.config.ship_height,
            player_speed=self.properties.player_speed,
        )
        self.players.empty()
        self.players.add(self.player)

    def _build_starfield(self, stars_count: int) -> pygame.Surface:
        surface = pygame.Surface((self.config.width, self.config.height), pygame.SRCALPHA)
        for _ in range(stars_count):
            x = random.randint(0, self.config.width)
            y = random.randint(0, self.config.height)
            pygame.draw.circle(surface, (255, 255, 255), (x, y), random.randint(1, 3))
        return surface

    # -------------------------------
    # Input / events
    # -------------------------------
    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue

            if event.type == pygame.KEYDOWN:
                if event.key in SUPER_1_KEYS:
                    self._activate_super(1)
                elif event.key in SUPER_2_KEYS:
                    self._activate_super(2)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.pause_button_rect.collidepoint(event.pos):
                    self.pause_time = time.time()
                    self.pause_menu.menu.enable()

                mouse_x, mouse_y = event.pos
                self.dragging = self.player.rect.collidepoint(mouse_x, mouse_y)

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.dragging = False

            if event.type == pygame.MOUSEMOTION and self.dragging:
                self._apply_mouse_drag(event.pos)

            if event.type == self.config.enemy_reload_event:
                self._spawn_enemy()

    def _apply_keyboard_movement(self, keys: Iterable[bool]) -> None:
        move_x = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * self.properties.player_speed
        move_y = (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * self.properties.player_speed
        if move_x and move_y:
            move_x *= 0.7071
            move_y *= 0.7071

        self.player.rect.x += int(round(move_x))
        self.player.rect.y += int(round(move_y))
        self._clamp_player()

    def _apply_mouse_drag(self, pos: tuple[int, int]) -> None:
        mouse_x, mouse_y = pos
        half_w = self.player.image.get_width() // 2
        half_h = self.player.image.get_height() // 2
        self.player.rect.x = mouse_x - half_w
        self.player.rect.y = mouse_y - half_h
        self._clamp_player()

    def _clamp_player(self) -> None:
        max_x = self.config.width - self.player.image.get_width()
        max_y = self.config.height - self.player.image.get_height()
        self.player.rect.x = max(0, min(max_x, self.player.rect.x))
        self.player.rect.y = max(0, min(max_y, self.player.rect.y))

    # -------------------------------
    # Core gameplay
    # -------------------------------
    def _activate_super(self, index: int) -> None:
        if index not in self.supers or len(self.supers[index]) != 1:
            return

        if index == 1:
            self.properties = replace(self.properties, fire_rate=self.properties.fire_rate * 0.5)
        elif index == 2:
            self.contusion = True
        else:
            return

        self.supers[index] = [True, time.time() + 5]

    def _update_supers(self) -> None:
        if 1 in self.supers and self.supers[1][0] and time.time() >= self.supers[1][1]:
            self.properties = replace(self.properties, fire_rate=self.base_fire_rate)
            del self.supers[1]

        if 2 in self.supers and self.supers[2][0] and time.time() >= self.supers[2][1]:
            self.contusion = False
            del self.supers[2]

    def _spawn_enemy(self) -> None:
        if len(self.enemies) >= self.properties.max_enemies_on_screen:
            return

        templates = enemy_templates()
        weights = enemy_spawn_weights(methods.getLvlDiff())
        enemy_id = random.choices(list(templates.keys()), weights=[weights[i] for i in templates], k=1)[0]
        tpl = templates[enemy_id]

        hp = max(1, int(round(tpl.hp * self.properties.enemies_hp_scale)))
        speed = self.properties.enemies_speed * tpl.speed_mult
        offset_x = random.choice([-1, 1]) * max(0.3, speed * 0.6)
        spawn_x = random.randint(20, self.config.width - 20 - 90)

        self.enemies.add(Enemy(spawn_x, tpl.image, hp, offset_x, speed, tpl.reward))

    def _handle_shooting(self) -> None:
        if not self.is_reloading:
            self._shoot(methods.getBulletCount())
            if self.shots_count >= 60:
                self.is_reloading = True
                self.reload_ready_at = time.time() + self.properties.reload_time
                self.shots_count = 0
        elif time.time() >= self.reload_ready_at:
            self.is_reloading = False

    def _shoot(self, num_lasers: int) -> None:
        while len(self.laser_timestamps) < num_lasers:
            self.laser_timestamps.append([])
        while len(self.laser_timestamps) > num_lasers:
            self.laser_timestamps.pop()

        if num_lasers == 1:
            x_offset = 55
            self._emit_laser(0, x_offset)
            return

        total_width = 40
        base_offset = 35
        spacing_multiplier = 2.5
        spacing = (total_width / (num_lasers + 1)) * spacing_multiplier
        start_offset = base_offset + (total_width - spacing * (num_lasers - 1)) / 2

        for idx in range(num_lasers):
            self._emit_laser(idx, start_offset + spacing * idx, multi=True, total=num_lasers)

    def _emit_laser(self, idx: int, x_offset: float, multi: bool = False, total: int = 1) -> None:
        now = time.time()
        timestamps = self.laser_timestamps[idx]
        can_fire = (not timestamps) or (now - timestamps[-1] > self.properties.fire_rate)
        if not can_fire:
            return

        self.lasers.add(Laser(self.player.rect.x + x_offset, self.player.rect.y))
        timestamps.append(now)
        self.shots_count += (1 / total) if multi else 1

    def _update_entities(self) -> None:
        for enemy in list(self.enemies):
            enemy.update(self.contusion, self.config.width)
        self.lasers.update()

    def _process_collisions(self) -> None:
        damage = methods.getStatsElem("Damage")
        laser_hits = pygame.sprite.groupcollide(self.enemies, self.lasers, False, True)

        for enemy, hits in laser_hits.items():
            enemy.hp -= damage * len(hits)

        for enemy in list(self.enemies):
            if enemy.hp <= 0:
                self.enemies.remove(enemy)
                self.score += 1
                self.money += enemy.reward
                if self.score >= self.properties.need_score:
                    self._win_game()
                    return

        for enemy in list(self.enemies):
            if pygame.sprite.spritecollideany(enemy, self.players):
                self.current_health -= 10
                self.enemies.remove(enemy)
                if self.current_health <= 0:
                    self._lose_game()
                    return
                continue

            if enemy.rect.bottom - (enemy.image.get_height() // 2) > self.config.height:
                self.score = max(0, self.score - self.properties.miss_penalty)
                self.enemies.remove(enemy)

        for laser in list(self.lasers):
            if laser.rect.bottom < 0:
                self.lasers.remove(laser)

    # -------------------------------
    # Render
    # -------------------------------
    def _draw_frame(self) -> None:
        self.background_y_offset += self.config.background_speed
        if self.background_y_offset >= self.config.height:
            self.background_y_offset = 0

        y = int(self.background_y_offset)
        self.screen.blit(self.background_image, (0, -y))
        self.screen.blit(self.background_image, (0, self.config.height - y))
        self.screen.blit(self.starfield_image, (0, -y))
        self.screen.blit(self.starfield_image, (0, self.config.height - y))

        self.screen.blit(self.pause_button, self.pause_button_rect)

        self.player.draw_thrusters(self.screen)
        self.enemies.draw(self.screen)
        self.lasers.draw(self.screen)
        self.players.draw(self.screen)

        self._render_hud()
        pygame.display.flip()

    def _render_hud(self) -> None:
        self._render_health()
        if self.is_reloading:
            self._render_reload()

        if 1 in self.supers:
            self.screen.blit(self.super_icon_1, (self.config.width - 150, 120))
            if self.supers[1][0]:
                self._render_super_bar(1)

        if 2 in self.supers:
            self.screen.blit(self.super_icon_2, (self.config.width - 90, 120))
            if self.supers[2][0]:
                self._render_super_bar(2)

        font_main = pygame.font.Font(methods.load_font("PressStart2P-Regular"), 20)
        self.screen.blit(font_main.render(f"Счет: {self.score}/{self.properties.need_score}", True, (255, 255, 255)), (730, 20))
        self.screen.blit(font_main.render(f"Монеты: {self.money}", True, (255, 255, 255)), (730, 80))
        self.screen.blit(font_main.render(f"Уровень: {methods.getLvlDiff()}", True, (255, 255, 255)), (400, 80))

        minutes, seconds = self._duration()
        self.screen.blit(font_main.render(f"{minutes}:{seconds}", True, (255, 255, 255)), (460, 20))

        hint_font = pygame.font.Font(methods.load_font("PressStart2P-Regular"), 12)
        hints = ["Управление: стрелки", "Супер 1: Z или 1", "Супер 2: X или 2"]
        for idx, line in enumerate(hints):
            self.screen.blit(hint_font.render(line, True, (255, 255, 255)), (40, 115 + idx * 20))

    def _render_health(self) -> None:
        bar_width, bar_height = 250, 10
        pygame.draw.rect(self.screen, (255, 0, 0), (70, 30, bar_width, bar_height), border_radius=10)
        ratio = self.current_health / self.max_health
        pygame.draw.rect(self.screen, (0, 255, 0), (70, 30, bar_width * ratio, bar_height), border_radius=10)

    def _render_reload(self) -> None:
        bar_width, bar_height = 250, 10
        pygame.draw.rect(self.screen, (181, 184, 177), (70, 50, bar_width, bar_height), border_radius=10)
        ratio = (self.reload_ready_at - time.time()) / self.properties.reload_time
        ratio = max(0.0, min(1.0, ratio))
        pygame.draw.rect(self.screen, (66, 170, 255), (70, 50, bar_width * ratio, bar_height), border_radius=10)

    def _render_super_bar(self, index: int) -> None:
        if index == 1:
            y, color = 70, (251, 0, 255)
        else:
            y, color = 90, (255, 200, 0)

        bar_width, bar_height = 250, 10
        pygame.draw.rect(self.screen, (181, 184, 177), (70, y, bar_width, bar_height), border_radius=10)
        ratio = (self.supers[index][1] - time.time()) / 5
        ratio = max(0.0, min(1.0, ratio))
        pygame.draw.rect(self.screen, color, (70, y, bar_width * ratio, bar_height), border_radius=10)

    # -------------------------------
    # Endgame / persistence
    # -------------------------------
    def _duration(self) -> tuple[int, int]:
        seconds = int(round(time.time() - self.start_time - sum(self.pauses)))
        return seconds // 60, seconds - 60 * (seconds // 60)

    def _save_earned_money(self) -> None:
        if self.rewards_saved:
            return
        methods.updateCoins(methods.getCoins() + int(self.money))
        self.rewards_saved = True

    def _lose_game(self) -> None:
        self._save_earned_money()
        minutes, seconds = self._duration()
        methods.addNoteHistory(datetime.datetime.now().strftime("%d.%m.%Y"), f"{minutes} m {seconds} s", 0)

        pygame.mixer.music.stop()
        pygame.mixer.music.load(os.path.join("Sounds", "Lose theme.mp3"))
        pygame.mixer.music.play()
        end.End_screen(self.screen, "defeat", self.money, self.start_new_game, width=self.config.width, height=self.config.height)

    def _win_game(self) -> None:
        self._save_earned_money()
        minutes, seconds = self._duration()
        methods.addNoteHistory(datetime.datetime.now().strftime("%d.%m.%Y"), f"{minutes} m {seconds} s", 1)

        pygame.mixer.music.stop()
        pygame.mixer.music.load(os.path.join("Sounds", "Victory theme.mp3"))
        pygame.mixer.music.play()

        methods.up_lvl_of_difficulty()
        end.End_screen(self.screen, "victory", self.money, self.start_new_game, width=self.config.width, height=self.config.height)

    # -------------------------------
    # Loading screen
    # -------------------------------
    def _run_loading_screen(self) -> None:
        font = pygame.font.Font(methods.load_font("PressStart2P-Regular"), 60)
        progress = 0.0
        dots = 0
        next_dots_at = time.time()

        while self.loading and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.screen.blit(
                pygame.transform.scale(pygame.image.load("images/fone3.jpg"), (self.config.width, self.config.height)),
                (0, 0),
            )

            if time.time() >= next_dots_at:
                dots += 1 if dots < 3 else -3
                next_dots_at = time.time() + 0.3

            text = font.render(f"Загрузка{''.join(['.' for _ in range(dots)])}", True, (255, 255, 255))
            self.screen.blit(
                text,
                (
                    self.config.width // 2 - text.get_width() // 2,
                    self.config.height // 2 - text.get_height() // 2 - 50,
                ),
            )

            bar_width = 600
            bar_height = 50
            bar_x = (self.config.width - bar_width) // 2
            bar_y = self.config.height // 2 + 20
            pygame.draw.rect(self.screen, (31, 12, 242), (bar_x, bar_y, bar_width, bar_height), 2)
            pygame.draw.rect(
                self.screen,
                (98, 0, 255),
                (bar_x + 2, bar_y + 2, (bar_width - 4) * (progress / 100), bar_height - 4),
            )

            perc_font = pygame.font.Font(methods.load_font("PressStart2P-Regular"), 25)
            self.screen.blit(perc_font.render(f"{int(round(progress, 0))}%", True, (255, 255, 255)), (850, self.config.height // 2 + 35))

            if progress < 100:
                progress += 0.5
            else:
                self.loading = False

            self.clock.tick(self.config.fps)
            pygame.display.flip()
