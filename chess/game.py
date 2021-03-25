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

    def __init__(self, debug=False, player1="PC", player2="PC", no_visuals=False):
        """Construct."""
        self.id: uuid4 = uuid4()
        self.time_created = datetime.now()
        self.debug = debug
        self.is_white_turn = True
        self.board: Board = Board(STARTING_FEN, BOARD_SIZE)
        # self.moves_history:
        if not no_visuals:
            self.visuals = GameVisuals(self, BOARD_SIZE, self.board.state)
            self.visuals.main_loop()

    def __str__(self) -> str:
        """Represent the current game and its info."""
        return f"Created: " \
               f"{self.time_created.strftime('%d/%m/%Y %H:%M:%S')} {self.id}"

    def is_move_valid(self, start_tile, end_tile):
        """Return whether or not a move is valid.

        We take for granted that the given input is correct and the
        starting tile does have the correct piece code.

        Parameters
        ----------
        start_tile : int
            Starting tile of the piece.
        end_tile : int
            Ending tile of the piece.
        piece_code : uint8
            A binary way to represnt our piece.

        Returns
        -------
        bool
            Returns whether or not a move is valid.
        """
        piece_code = self.board.state[start_tile]
        get_piece_moves = Piece.find_moveset(piece_code)
        if end_tile not in get_piece_moves(start_tile):
            return False
        print(f"start-tile: {start_tile} end-tile: {end_tile}")
        print(f"moves: {get_piece_moves(start_tile)}")

        # move_direction = Move.find_move_direction(start_t, end_t)
        return True

    def register_move(self, old_index: int, new_index: int):
        self.board.state[new_index] = self.board.state[old_index]
        self.board.state[old_index] = Piece.EMPTY
        self.is_white_turn = not self.is_white_turn

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
        if not Piece.is_our_teams_turn(piece_code, self.is_white_turn):
            return False
        return True
