import pygame_menu
import pygame_menu.events
import pygame_menu.themes

import methods


class Panel:

    def __init__(self, screen, width=800, height=550):
        self.screen = screen
        self.width, self.height = width, height
        default_scale = [(0.25, 0.25)]
        #Обьект темы
        mytheme = pygame_menu.Theme(background_color=(92, 62, 44),
                                     title_bar_style=pygame_menu.widgets.MENUBAR_STYLE_NONE, title_font_size=2)
        mytheme.widget_selection_effect = None
        # Обьект меню
        self.menu = pygame_menu.Menu('Прокачка', width, height, theme=mytheme, center_content=False)
        self.menu.add.frame_v(50, 70)

        self.menu.add.banner(methods.load_image("return_button"), self.Return).scale(3, 1).set_margin(-470, -45)
        #уровень

        self.lvlLabel = self.menu.add.label(f'Уровень: {methods.getLvl()}').update_font(style={"size": 24, "name": methods.load_font("PressStart2P-Regular"),
                                                                                               "color": (255, 255, 255)}).set_margin(0, -47)
        self.coinsLabel = self.menu.add.label(f'Баланс: {int(methods.getCoins())}$').set_alignment("align-right").update_font(style={"size": 20, "name": methods.load_font("PressStart2P-Regular"),
                                                                                                                                     "color": (0, 255, 34)})
        self.menu.add.frame_v(60, 150)

        self.menu.add.label("Статистика").set_alignment("align-left").update_font(style={"size": 24, "name": methods.load_font("PressStart2P-Regular"),
                                                                                               "color": (255, 255, 255)}).set_margin(15, 0)

        self.statsBackround = self.menu.add.image(methods.load_image("stats_backround")).set_alignment(
            "align-left").set_margin(-5, -400).scale(2.8, 2.2, False).scale(*default_scale[0])

        self.Ship = self.menu.add.image((methods.load_image(methods.getSpaceship(), True) if methods.getLvl() <= 20 else "Ships/ship_lvl_20.png")).set_alignment(
            "align-center").set_margin(0, -250).scale(1, 1, False)
        #текст

        self.standartPos = [(70, 15), (15, -40)]


        #Урон
        self.damageImage = self.menu.add.image(methods.load_image("damage_icon")).set_margin(*self.standartPos[1]).set_alignment("align-left").scale(0.9, 0.9).scale(*default_scale[0])
        self.damageLabel = self.menu.add.label(f'Damage: {methods.stat_exist("Damage")}').set_alignment(
            "align-left").update_font(style={"size": 12, "name": methods.load_font("PressStart2P-Regular"), "color": (255, 112, 3)}).set_margin(*self.standartPos[0])

        #Скоростельность
        self.firerateImage = self.menu.add.image(methods.load_image("firerate_icon")).set_margin(*self.standartPos[1]).set_alignment("align-left").scale(0.8, 0.8).scale(*default_scale[0])
        self.fireRateLabel = self.menu.add.label(f'Fire rate: {methods.stat_exist("FireRate")}').set_alignment(
            "align-left").update_font(style={"size": 12, "name": methods.load_font("PressStart2P-Regular"), "color": (153, 255, 0)}).set_margin(*self.standartPos[0])

        #Куладун
        self.cooldownImage = self.menu.add.image(methods.load_image("cooldown_icon")).set_margin(*self.standartPos[1]).set_alignment("align-left").scale(0.8, 0.8).scale(*default_scale[0])
        self.cooldownLabel = self.menu.add.label(f'Cooldown: {methods.stat_exist("Cooldown")}').set_alignment(
            "align-left").update_font(style={"size": 12, "name": methods.load_font("PressStart2P-Regular"), "color": (0, 159, 184)}).set_margin(*self.standartPos[0])

        # Хп
        self.healthImage = self.menu.add.image(methods.load_image("health_icon")).set_margin(*self.standartPos[1]).set_alignment("align-left").scale(0.8, 0.8).scale(*default_scale[0])
        self.healthLabel = self.menu.add.label(f'Health: {methods.stat_exist("Health")}').set_alignment(
            "align-left").update_font(style={"size": 12, "name": methods.load_font("PressStart2P-Regular"), "color": (184, 9, 0)}).set_margin(*self.standartPos[0])

        # Количетсво пуль
        self.bulletsImage = self.menu.add.image(methods.load_image("bullets_icon")).set_margin(
            *self.standartPos[1]).set_alignment("align-left").scale(0.8, 0.8).scale(*default_scale[0])
        self.bulletsLabel = self.menu.add.label(f'Bullets count: {methods.getBulletCount()}').set_alignment(
            "align-left").update_font(
            style={"size": 12, "name": methods.load_font("PressStart2P-Regular"), "color": (255, 255, 230)}).set_margin(
            *self.standartPos[0])

        self.menu.add.frame_h(50, 50).set_alignment("align-left")
        self.menu.add.vertical_margin(15)
        #Цена
        self.costImage = self.menu.add.image(methods.load_image("money_icon")).set_margin(-50, -35).set_alignment("align-center").scale(0.3, 0.3).scale(*default_scale[0])
        self.costLabel = self.menu.add.label(f'{methods.stat_exist("Lvl costs")}$').set_alignment(
            "align-center").update_font(style={"size": 20, "name": methods.load_font("PressStart2P-Regular"),
                                                                                               "color": (255, 255, 255)}).set_margin(45, 0)

        #кнопки
        self.menu.add.frame_h(50, 10).set_alignment("align-left")

        self.upgradeButton = self.menu.add.banner(methods.load_image("buy_button_active") if methods.getData()["user"]["coins"] >= methods.getData()["stats"]["Lvl costs"] \
                                                  else methods.load_image("buy_button_unactive"), self.render).set_alignment("align-center").scale(*default_scale[0])

        self.upgradeButton.set_title('Улучшить').update_font(style={"size": 24, "name": methods.load_font("PressStart2P-Regular")}).scale(1.2, 1.6)
        self.menu.mainloop(screen)


    def render(self):
        methods.up_lvl()

        #Обновляет показатели

        self.lvlLabel.set_title(f"Уровень: {methods.getLvl()}")
        self.coinsLabel.set_title(f"Баланс: {methods.getCoins()}$")

        self.damageLabel.set_title(f'Damage: {methods.stat_exist("Damage")}')
        self.fireRateLabel.set_title(f'Fire rate: {methods.stat_exist("FireRate")}')
        self.cooldownLabel.set_title(f'Cooldown: {methods.stat_exist("Cooldown")}')
        self.healthLabel.set_title(f'Health: {methods.stat_exist("Health")}')
        self.costLabel.set_title(f'{methods.stat_exist("Lvl costs")}$')
        self.bulletsLabel.set_title(f'Bullets count: {methods.getBulletCount()}')

        self.Ship.set_image((methods.load_image(methods.getSpaceship(), True) if methods.getLvl() <= 20 else methods.load_image("Ships/ship_lvl_20.png", True)))

        self.upgradeButton.set_background_color(methods.load_image("buy_button_active") if methods.getData()["user"]["coins"] >= methods.getData()["stats"]["Lvl costs"] \
                                                else methods.load_image("buy_button_unactive"))

    def Return(self):
        #Возвращает в меню

        self.menu.disable()