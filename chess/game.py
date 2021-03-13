"""uuid: A unique undentifier."""
from uuid import uuid4

from chess.piece import Piece
from chess.board import Board
from datetime import datetime
from chess.frontend.visuals import GameVisuals


# STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
STARTING_FEN = "rnbqkbnr/ppppp1pp/8/8/4P3/8/PPPP1PPP/RNBQKBNR"
BOARD_SIZE = 64


class Game:
    """Basically the main controller for game visuals and game logic."""

    def __init__(self, debug=False, player1="PC", player2="PC"):
        """Construct."""
        self.id: uuid4 = uuid4()
        self.time_created = datetime.now()
        self.debug = debug
        self.is_white_turn = True
        self.board: Board = Board(STARTING_FEN, BOARD_SIZE)
        self.visuals = GameVisuals(self, BOARD_SIZE, self.board.state)


    def __str__(self) -> str:
        """Represent the current game and its info."""
        return f"Created: " \
               f"{self.time_created.strftime('%d/%m/%Y %H:%M:%S')} {self.id}"

    def start(self):
        """Run basic setup functions."""
        self.visuals.main_loop()


    def is_piece_pickable(self, piece_code):
        """Determine if you can pick a piece.

        Parameters
        ----------
        piece_code : uint8
            A binary way to represent our pieces

        Returns
        -------
        bool
            If the piece is on the same colour as the player 
            who is turn to play then the pick is pickable.
        """
        if Piece.get_type(piece_code) == Piece.EMPTY:
            return False
        elif not Piece.is_our_teams_turn(piece_code, self.is_white_turn):
            return False
        return True




