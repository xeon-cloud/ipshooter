import pygame
import pygame_menu
import pygame_menu.events
import pygame_menu.themes

running = True


class End_screen:
    def __init__(self, screen, status, money_earned, startFunc, width=800, height=550):
        self.startFunc = startFunc
        import methods

        status_values = {"victory": {"color_for_backround": (165, 207, 76),
                              "color_for_font": (255, 255, 255)},
                  "defeat": {"color_for_backround": (82, 0, 0),
                              "color_for_font": (71, 59, 59)}
                  }

        mytheme = pygame_menu.Theme(background_color=(status_values[status]["color_for_backround"]),
                                    title_bar_style=pygame_menu.widgets.MENUBAR_STYLE_NONE, title_font_size=1)
        mytheme.widget_selection_effect = None

        self.screen = screen
        self.width, self.height = width, height

        self.menu = pygame_menu.Menu('', width, height, theme=mytheme)
        self.menu.add.label(f'{status.capitalize()}!').update_font(style={"size": 80, "name": methods.load_font("PressStart2P-Regular"), "color": status_values[status]["color_for_font"]})
        self.menu.add.label(f'{methods.getData()["user"]["lvl_of_difficulty"] - 1} lvl completed!').update_font(style={"size": 20, "name": methods.load_font("PressStart2P-Regular"), "color": (40, 40, 40)})
        self.menu.add.label(f'{money_earned}$ earned!').update_font(
            style={"size": 36, "name": methods.load_font("PressStart2P-Regular"), "color": (66, 181, 0)})

        self.menu.add.frame_v(width=60, height=160)

        self.menu.add.banner(methods.load_image("continue_button"), self.Continue).scale(9, 1.3, False)
        self.menu.add.banner(methods.load_image("exit_button"), self.Return).scale(9, 1.3, False)

        self.menu.mainloop(screen)

    def Continue(self):
        pygame.mixer.music.stop()

        self.menu.disable()

        self.startFunc()

    def Return(self):
        import menu

        mainMenu = menu.Menu(self.screen, self.startFunc, width=self.width, height=self.height)
        mainMenu.menu.enable()
        mainMenu.menu.mainloop(self.screen)

        self.menu.disable()