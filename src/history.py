import pygame
import pygame_menu
import pygame_menu.events
import pygame_menu.themes

import methods


class Panel:
    def __init__(self, screen, width=800, height=550):
        self.screen = screen
        self.width, self.height = width, height
        self.max_visible_rows = 12

        mytheme = pygame_menu.themes.THEME_DARK.copy()
        mytheme.widget_selection_effect = None
        mytheme.title_bar_style = pygame_menu.widgets.MENUBAR_STYLE_NONE
        mytheme.title_font_size = 1

        self.menu = pygame_menu.Menu("История", width, height, theme=mytheme, center_content=False)
        self.menu.add.banner(methods.load_image("return_button"), self.Return).scale(3, 1).set_margin(-455, 0)

        self.headers = ["№", "Дата", "Время", "Уровни", "Статус"]
        self.col_widths = [70, 190, 170, 170, 170]
        self.row_height = 44
        self.table_x = (self.width - sum(self.col_widths)) // 2
        self.table_y = 160

        self.header_font = pygame.font.SysFont("Arial", 38, bold=True)
        self.cell_font = pygame.font.SysFont("Arial", 34)

        self.rows = self._build_rows()
        self._loop()

    def _loop(self):
        self.menu.enable()
        while self.menu.is_enabled():
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.menu.disable()
                    pygame.event.post(event)
                    break

            self.menu.update(events)
            if not self.menu.is_enabled():
                break

            self.menu.draw(self.screen)
            self._draw_table()
            pygame.display.flip()

    def _build_rows(self):
        rows = methods.loadHistory()
        if len(rows) > self.max_visible_rows:
            rows = rows[-self.max_visible_rows:]

        prepared = []
        for i, row in enumerate(rows, start=1):
            normalized = self.normalize_row(row)
            if normalized is None:
                continue
            date, duration, step, status = normalized
            prepared.append([str(i), date, duration, step, status])
        return prepared

    def _draw_table(self):
        visible_rows = self.rows if self.rows else [["-", "Нет данных", "-", "-", "-"]]

        total_rows = 1 + len(visible_rows)
        total_width = sum(self.col_widths)
        total_height = total_rows * self.row_height
        x = self.table_x
        y = self.table_y

        pygame.draw.rect(self.screen, (40, 40, 44), (x, y, total_width, self.row_height))
        pygame.draw.rect(self.screen, (220, 220, 220), (x, y, total_width, total_height), width=2)

        running_x = x
        for width in self.col_widths[:-1]:
            running_x += width
            pygame.draw.line(self.screen, (220, 220, 220), (running_x, y), (running_x, y + total_height), width=2)

        for row_i in range(1, total_rows):
            line_y = y + row_i * self.row_height
            pygame.draw.line(self.screen, (220, 220, 220), (x, line_y), (x + total_width, line_y), width=2)

        self._draw_row(self.headers, y, self.header_font, (185, 185, 185))

        for idx, row_data in enumerate(visible_rows):
            row_y = y + (idx + 1) * self.row_height
            self._draw_row(row_data, row_y, self.cell_font, (230, 230, 230))

    def _draw_row(self, values, row_y, font, color):
        col_x = self.table_x
        for col_i, text in enumerate(values):
            col_w = self.col_widths[col_i]
            rendered = font.render(str(text), True, color)
            text_x = col_x + (col_w - rendered.get_width()) // 2
            text_y = row_y + (self.row_height - rendered.get_height()) // 2
            self.screen.blit(rendered, (text_x, text_y))
            col_x += col_w

    @staticmethod
    def normalize_row(row):
        if not isinstance(row, (list, tuple)) or len(row) < 2:
            return None

        values = [str(value).replace("\n", " ").strip() for value in row if str(value).strip()]
        if len(values) < 2:
            return None

        date = values[0]
        duration = values[1]
        status = "-"
        step = "-"

        if len(values) >= 4:
            step = values[2]
            status = values[3]
        elif len(values) == 3:
            third = values[2]
            if "Победа" in third:
                step = third.replace("Победа", "").strip(" -–—>") or "-"
                status = "Победа"
            elif "Поражение" in third:
                step = third.replace("Поражение", "").strip(" -–—>") or "-"
                status = "Поражение"
            else:
                step = third

        return (
            Panel.short(date, 12),
            Panel.short(duration, 12),
            Panel.short(step, 14),
            Panel.short(status, 12),
        )

    @staticmethod
    def short(text, limit):
        return text if len(text) <= limit else f"{text[:limit - 1]}…"

    def Return(self):
        self.menu.disable()
