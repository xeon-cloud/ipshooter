import os

import pygame
import pygame_menu
import pygame_menu.events
import pygame_menu.themes
import pygame_menu.widgets
import pygame_menu.widgets.core
import pygame_menu.widgets.core.selection



class Menu:
    def __init__(self, screen, startFunc, width=800, height=550):
        self.startFunc = startFunc
        import methods

        self.screen = screen
        self.width, self.height = width, height

        Theme = pygame_menu.Theme(background_color=methods.load_image("fone"), 
                                  title_bar_style=pygame_menu.widgets.MENUBAR_STYLE_NONE, title_font_size=1)

        Theme.widget_selection_effect = None

        self.menu = pygame_menu.Menu('', width, height, theme=Theme, center_content=False)

        self.menu.add.frame_v(50, 70)

        self.menu.add.image(methods.load_image("game_name")).scale(1.6, 1.6)

        default_values = ["align-left", (25, 0)]

        self.menu.add.image(methods.load_image("buttons_backround")).set_alignment("align-left").set_margin(0, -370).scale(0.25, 0.25)
        self.menu.add.banner(methods.load_image("play_button"), self.startPlay).scale(9, 1.3, False).set_alignment(default_values[0]).set_margin(*default_values[1])
        self.menu.add.banner(methods.load_image("game_history_button"), self.OpenaGamesHistory).scale(9, 1.3, False).set_alignment(default_values[0]).set_margin(*default_values[1])
        self.menu.add.banner(methods.load_image("upgrade_button"), self.OpenUpgrade).scale(9, 1.3, False).set_alignment(default_values[0]).set_margin(*default_values[1])
        self.menu.add.banner(methods.load_image("settings_button"), self.openSettings).scale(9, 1.3, False).set_alignment(default_values[0]).set_margin(*default_values[1])
        self.menu.add.banner(methods.load_image("exit_button"), pygame_menu.events.EXIT).scale(9, 1.3, False).set_alignment(default_values[0]).set_margin(*default_values[1])

        pygame.mixer.music.load(os.path.join("Sounds", "Menu theme.mp3"))
        pygame.mixer.music.play()

        pygame.mixer.music.set_volume(methods.getData()["user"]["volume"])


    def startPlay(self):
        pygame.mixer.music.stop()

        pygame.mixer.music.load(os.path.join("Sounds", "Game theme.mp3"))
        pygame.mixer.music.play()

        self.menu.disable()
        self.startFunc()


    def OpenUpgrade(self):
        import upgrade

        upgrade.Panel(self.screen, width=self.width, height=self.height)

    def OpenaGamesHistory(self):
        import history

        history.Panel(self.screen, width=self.width, height=self.height)

    def openSettings(self):
        import settings

        settings.Panel(self.screen, width=self.width, height=self.height)
