import pygame
import pygame_menu
import pygame_menu.events
import pygame_menu.themes

import methods


class Panel:
    def __init__(self, screen, width=800, height=550):
        self.screen = screen
        self.width, self.height = width, height
        data = methods.getData()
        self.awaiting_super_idx: int | None = None
        mytheme = pygame_menu.themes.THEME_DARK.copy()
        mytheme.widget_selection_effect = None
        mytheme.title_bar_style = pygame_menu.widgets.MENUBAR_STYLE_NONE
        mytheme.title_font_size = 1
        self.menu = pygame_menu.Menu('Настройки', width, height, theme=mytheme, center_content=False)

        self.menu.add.banner(methods.load_image("return_button"), self.Return).scale(3, 1).set_margin(-455, 0)

        self.menu.add.frame_v(50, 100)

        current_volume = data["user"].get("volume", pygame.mixer.music.get_volume()) * 100
        self.volume_slider = self.menu.add.range_slider(
            "Звук", current_volume, (0, 100), 1, onchange=self.set_volume
        ).update_font(style={"name": methods.load_font("PressStart2P-Regular")})

        current_fps = methods.getFPS()
        self.fps_slider = self.menu.add.range_slider(
            "FPS", current_fps, (30, 120), 10, onchange=self.set_fps
        ).update_font(style={"name": methods.load_font("PressStart2P-Regular")})

        self.super_1_button = self.menu.add.button(
            self._super_button_title(1), lambda: self.start_rebind(1)
        ).update_font(style={"name": methods.load_font("PressStart2P-Regular")})
        self.super_2_button = self.menu.add.button(
            self._super_button_title(2), lambda: self.start_rebind(2)
        ).update_font(style={"name": methods.load_font("PressStart2P-Regular")})
        self.bind_hint_label = self.menu.add.label("").update_font(
            style={"name": methods.load_font("PressStart2P-Regular"), "size": 13}
        )

        self._set_bind_hint("Нажмите на строку супера, затем на нужную клавишу")
        self._loop()

    def set_volume(self, value):
        #меняем звук
        data = methods.getData()
        data["user"]["volume"] = value / 100
        pygame.mixer.music.set_volume(value / 100)
        methods.dump(data)

    def set_fps(self, value):
        methods.setFPS(int(value))

    def start_rebind(self, index: int):
        self.awaiting_super_idx = index
        self._set_bind_hint(f"Нажмите клавишу для Супер {index} (ESC - отмена)")

    def _set_bind_hint(self, text: str):
        self.bind_hint_label.set_title(text)
        self.super_1_button.set_title(self._super_button_title(1))
        self.super_2_button.set_title(self._super_button_title(2))

    def _super_button_title(self, index: int) -> str:
        return f"Супер {index}: {methods.getSuperKeyDisplay(index)}"

    def _loop(self):
        self.menu.enable()
        while self.menu.is_enabled():
            events = pygame.event.get()
            menu_events = []
            for event in events:
                if event.type == pygame.QUIT:
                    self.menu.disable()
                    pygame.event.post(event)
                    continue

                if self.awaiting_super_idx is not None and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.awaiting_super_idx = None
                        self._set_bind_hint("Назначение отменено")
                    else:
                        methods.setSuperKeyCode(self.awaiting_super_idx, event.key)
                        self.awaiting_super_idx = None
                        self._set_bind_hint("Клавиша назначена")
                    continue

                menu_events.append(event)

            self.menu.update(menu_events)
            if not self.menu.is_enabled():
                break
            self.menu.draw(self.screen)
            pygame.display.flip()

    def Return(self):
        self.awaiting_super_idx = None
        self.menu.disable()
