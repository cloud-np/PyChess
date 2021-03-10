"""uuid: A unique undentifier."""
from uuid import uuid4
from chess.board import Board
from datetime import datetime


class Game:
    """This will holds all the info about the game and the players."""

    def __init__(self):
        """Construct."""
        self.id: uuid4 = uuid4()
        self.time_created = datetime.now()
        self.board: Board = Board()

    def __str__(self) -> str:
        """Represent the current game and its info."""
        return f"Created: " \
               f"{self.time_created.strftime('%d/%m/%Y %H:%M:%S')} {self.id}"
