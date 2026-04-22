import pygame_menu
import methods


class Menu:
    def __init__(self, screen, startFunc, disablePauseFunc, width=800, height=550):
        self.screen = screen
        self.startFunc = startFunc
        self.disablePauseFunc = disablePauseFunc
        self.width, self.height = width, height
        # Обьект темы
        Theme = pygame_menu.Theme(background_color=methods.load_image("fone"),
                                  title_bar_style=pygame_menu.widgets.MENUBAR_STYLE_NONE, title_font_size=1)

        # Обьект меню
        self.menu = pygame_menu.Menu('Меню паузы', width, height, theme=Theme, center_content=False)
        self.menu.add.frame_v(50, 70)
        self.menu.add.label("Пауза").update_font(style={"name": methods.load_font("PressStart2P-Regular"),
                                                        "size": 70, "color": (124, 255, 12)})
        self.menu.add.frame_v(50, 140)
        self.menu.add.banner(methods.load_image("continue_button"), self.Continue).scale(9, 1.3, False)
        self.menu.add.banner(methods.load_image("exit_button"), self.Return).scale(9, 1.3, False)
        self.menu.add.banner(methods.load_image("settings_button"), self.openSettings).scale(9, 1.3, False)


    def Continue(self):
        # отлючаем меню и продолжаем
        self.disablePauseFunc()
        self.menu.disable()

    def Return(self):
        import menu

        mainMenu = menu.Menu(self.screen, self.startFunc, width=self.width, height=self.height)
        mainMenu.menu.enable()
        mainMenu.menu.mainloop(self.screen)

        self.menu.disable()

    def openSettings(self):
        # настройки
        import settings

        settings.Panel(self.screen, width=self.width, height=self.height)