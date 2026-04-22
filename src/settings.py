import pygame
import pygame_menu
import pygame_menu.events
import pygame_menu.themes

import methods


class Panel:
    def __init__(self, screen, width=800, height=550):
        self.screen = screen
        self.width, self.height = width, height
        mytheme = pygame_menu.themes.THEME_DARK.copy()
        mytheme.widget_selection_effect = None
        mytheme.title_bar_style = pygame_menu.widgets.MENUBAR_STYLE_NONE
        mytheme.title_font_size = 1
        self.menu = pygame_menu.Menu('Настройки', width, height, theme=mytheme, center_content=False)

        self.menu.add.banner(methods.load_image("return_button"), self.Return).scale(3, 1).set_margin(-455, 0)

        self.menu.add.frame_v(50, 100)

        self.volume_slider = self.menu.add.range_slider("Звук", pygame.mixer.music.get_volume() * 100, (0, 100), 1,
                                                        onchange=self.set_volume).update_font(
                                                        style={"name": methods.load_font("PressStart2P-Regular")})


        self.menu.mainloop(screen)

    def set_volume(self, value):
        #меняем звук
        data = methods.getData()
        data["user"]["volume"] = value / 100
        pygame.mixer.music.set_volume(value / 100)
        methods.dump(data)

    def Return(self):
        self.menu.disable()
