import pygame_menu
import pygame_menu.events
import pygame_menu.themes
import pygame_menu.font

import methods

class Panel:
    def __init__(self, screen, width=800, height=550):
        self.screen = screen
        self.width, self.height = width, height
        mytheme = pygame_menu.themes.THEME_DARK.copy()
        mytheme.widget_selection_effect = None
        mytheme.title_bar_style = pygame_menu.widgets.MENUBAR_STYLE_NONE
        mytheme.title_font_size = 1

        self.menu = pygame_menu.Menu('История', width, height, theme=mytheme, center_content=False)

        self.menu.add.banner(methods.load_image("return_button"), self.Return).scale(3, 1).set_margin(-455, 0)
        
        # self.menu.add.banner(methods.load_image("return_button"), self.Return).scale(3, 1).set_margin(-455, 0)
        self.table = self.menu.add.table('', border_color='white').set_alignment("align-center").update_font(
            style={"size": 14, "name": pygame_menu.font.FONT_OPEN_SANS}
        )

        self.table.default_cell_padding = (6, 8)
        self.renderData()
        self.table.set_max_width(self.width - 80)
        self.table.set_max_height(self.height - 140)
        self.menu.mainloop(screen)

    def renderData(self):
        self.table.clear()
        # заполняем таблицу
        self.table.add_row(['№', 'Дата', 'Продолжительность', 'Ступень', 'Статус'],
                           cell_border_color='white',
                           cell_align=pygame_menu.locals.ALIGN_CENTER)
        for i, row in enumerate(methods.loadHistory(), start=1):
            date, duration, step, status = self.normalize_row(row)
            self.table.add_row(
                [str(i), date, duration, step, status],
                cell_border_color='white',
                cell_align=pygame_menu.locals.ALIGN_CENTER
            )

    @staticmethod
    def normalize_row(row):
        if not isinstance(row, (list, tuple)):
            return '-', '-', '-', str(row)
        values = [str(value) for value in row[:4]]
        while len(values) < 4:
            values.append('-')
        return values[0], values[1], values[2], values[3]
        
    def Return(self):
        self.menu.disable()
