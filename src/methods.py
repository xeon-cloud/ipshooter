import json
import os
import pygame_menu

def load_image(path, use_path=False): #Загружает картинки
    if use_path:
        image_path = path
    else:
        image_path = os.path.join('menu_images', f'{path}.png')
    image = pygame_menu.BaseImage(image_path=image_path) #Выберает по пути
    return image #Возвращает картинку


def load_font(name): #Загружает шрифты
    font_path = os.path.join("Fonts", f'{name}.ttf')
    return font_path


def getData() -> dict: #Возвращает дату игрока
    with open('base.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def dump(data): #Сохраняет дату игрока
    with open('base.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def getCoins() -> int: #Возвращает текущее кол монет
    return getData()['user']['coins']


def getLvl() -> int: #Возврщает текущий лвл
    return getData()['user']['lvl']

def getLvlDiff() -> int: #Возврщает текущий лвл сложности
    return getData()['user']['lvl_of_difficulty']


def updateCoins(newValue: int): #Присваивает значение монетам игрока
    data = getData()
    data['user']['coins'] = newValue
    dump(data)

def stat_exist(stats): #Проверяет наличие передаваемой статистики
    return getData()["stats"][stats] if getData().get("stats") else 0


def up_lvl(): #Повышает статистики
    data = getData()
    if data["user"]["coins"] >= data["stats"]["Lvl costs"]:
        data["user"]["lvl"] += 1
        data["user"]["coins"] -= data["stats"]["Lvl costs"]
        data["user"]["coins"] = int(data["user"]["coins"])

        # статистика: можно через цикл повышать на процент от нынешней статы
        data["stats"]["Lvl costs"] *= 1.7
        if data["stats"]["Damage"] > 1:
            data["stats"]["Damage"] *= 1.1
        else:
            data["stats"]["Damage"] = 2
        data["stats"]["FireRate"] *= 0.95
        data["stats"]["Cooldown"] *= 0.95

        data["stats"]["Lvl costs"] = round(data["stats"]["Lvl costs"])
        data["stats"]["Damage"] = int(data["stats"]["Damage"])
        data["stats"]["FireRate"] = round(data["stats"]["FireRate"], 2)
        data["stats"]["Cooldown"] = round(data["stats"]["Cooldown"], 2)
        ship_lvl = min(data["user"]["lvl"], 20)
        data["user"]["spaceship"] = f'Ships/ship_lvl_{ship_lvl}.png'
    else:
        print("Нет денег")

    dump(data)


def up_lvl_of_difficulty(): #Повышает уровень сложности
    data = getData()
    data["user"]["lvl_of_difficulty"] += 1
    dump(data)

def getSpaceship(): #Возвращает текущий корабль
    return getData()['user']['spaceship']

def getIndexShip(): #Возвращает индекс корабля для анимаций и коректирования пуль
    r = ''
    for i in getData()['user']['spaceship']:
        if i.isdigit():
            r += i
    return int(r)


def getStatsElem(key: str): #Аналог Stat_exist
    return getData()["stats"][key]

def getBulletCount(): #Возвращает количетсво выпускаемых пуль
    count = 0
    for i in getData()["user"]["bullets_count"]:
        spisok = i.split(", ")
        if str(getLvl()) in spisok:
            count = getData()["user"]["bullets_count"][i]
    if count == 0:
        count = 7
    return count


def loadHistory(): #Возвращает историю игр
    return getData()['history']

def addNoteHistory(date, duration, status): # 1 - win, 2 - loose. Записывает игру
    data = getData()
    data['history'].append([date, duration, f'{getLvlDiff()} -> {getLvlDiff() + 1}', 'Победа' if status == 1 else 'Поражение'])
    dump(data)


def load_ship_image(): #Загружает картинку корабля
    global image_path
    ship_filename = getData()['user']['spaceship']
    ship_filepath = os.path.join("Ships", ship_filename)

    if os.path.exists(ship_filepath):
        image_path = ship_filepath
    else:
        image_path = "Ships/ship_lvl_9.png"

    return image_path
