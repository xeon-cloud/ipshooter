import os

from game import GameSession


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)


_session: GameSession | None = None


def get_session() -> GameSession:
    global _session
    if _session is None:
        _session = GameSession()
    return _session


def startNewGame() -> None:
    get_session().start_new_game()


def start_new_game() -> None:
    startNewGame()


def run() -> None:
    get_session().run()


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print('game finished')