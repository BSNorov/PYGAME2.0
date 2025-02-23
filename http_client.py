import threading
import logging

import requests

from models import User, Game, Player, Move, Rating


def run_in_thread(func):
    def wrapper(*args, **kwargs):
        result_container = {"result": None}
        thread = threading.Thread(target=lambda: result_container.update(result=func(*args, **kwargs)))
        thread.start()
        return result_container["result"]
    return wrapper


class HttpClient:
    def __init__(self):
        self.host = "https://tictac.redko.us"

    def get_user(self, user_id: str) -> User | None:
        try:
            response = requests.get(f"{self.host}/get_user?user_id={user_id}", timeout=5)
            response.raise_for_status()
            data = response.json()
            if data["status"] != 200:
                logging.error(f"Ошибка сервера при get_user: {data}")
                return None
            return User(**data["body"]["user"])
        except requests.exceptions.RequestException as e:
            logging.error(f"Ошибка соединения с сервером: {e}")
            return None

    def get_active_game_by_user_id(self, user_id: str) -> tuple[Game, list[Player], list[Move]] | None:
        try:
            response = requests.get(f"{self.host}/get_active_game_by_user_id?user_id={user_id}").json()
            if response["status"] != 200:
                return None

            game = Game(**response["body"]["game"])
            players = [Player(**user) for user in response["body"]["users"]]
            moves = [Move(**move) for move in response["body"]["moves"]]

            return game, players, moves
        except:
            return None

    def join_game(self, user_id: str) -> tuple[Game, list[Player]] | None:
        try:
            response = requests.get(f"{self.host}/join_game?user_id={user_id}").json()
            if response["status"] != 200:
                return None

            game = Game(**response["body"]["game"])
            users = [Player(**user) for user in response["body"]["users"]]

            return game, users
        except:
            return None

    def get_game_info(self, game_id: int) -> tuple[Game, list[Player], list[Move]] | None:
        try:
            response = requests.get(f"{self.host}/get_game_info?game_id={game_id}", timeout=5)
            response.raise_for_status()
            data = response.json()
            if data["status"] != 200:
                logging.error(f"Ошибка сервера: {data}")
                return None

            game = Game(**data["body"]["game"])
            players = [Player(**user) for user in data["body"]["users"]]
            moves = [Move(**move) for move in data["body"]["moves"]]

            return game, players, moves
        except requests.exceptions.RequestException as e:
            logging.error(f"Ошибка соединения: {e}")
            return None

    @run_in_thread
    def make_move(self, user_id: str, game_id: int, row: int, col: int, sign: str) -> Move | None:
        try:
            url = f"{self.host}/make_move?user_id={user_id}&game_id={game_id}&row={row}&col={col}&sign={sign}"
            response = requests.get(url).json()
            if response["status"] != 200:
                return None

            return Move(**response["body"]["move"])
        except:
            return None

    def get_rating(self) -> list[Rating] | None:
        try:
            response = requests.get(f"{self.host}/get_rating").json()
            if response["status"] != 200:
                return None

            return [Rating(**rating) for rating in response["body"]["rating"]]
        except:
            return None

    def leave_game(self, user_id: str, game_id: str) -> bool:
        try:
            response = requests.get(f"{self.host}/leave_game?user_id={user_id}&game_id={game_id}").json()

            return response["status"] == 200
        except:
            return False
