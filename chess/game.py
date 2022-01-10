"""uuid: A unique undentifier."""
from uuid import uuid4
from uuid import UUID

from chess.board import Board
from datetime import datetime
from chess.pieces.piece import Piece
from chess.frontend.visuals import GameVisuals


# STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
STARTING_FEN = "rnbqkbnr/ppppp1pp/8/8/4P3/8/PPPP1PPP/RNBQKBNR"
# BOARD_SIZE = 64
# VISUAL_BOARD_SIZE = 64


class Game:
    """Basically the main controller for game visuals and game logic."""

    def __init__(self, debug: bool = False, player1: str = "PC", player2: str = "PC", visuals: bool = True):
        """Construct."""
        self.id: UUID = uuid4()
        self.time_created = datetime.now()
        self.debug: bool = debug
        self.is_white_turn: bool = True
        self.board: Board = Board(STARTING_FEN)
        # self.moves_history:
        if visuals:
            self.visuals: GameVisuals = GameVisuals(self, self.board.state)
            self.visuals.main_loop()

    def __str__(self) -> str:
        """Represent the current game and its info."""
        return (
            f"Created: " f"{self.time_created.strftime('%d/%m/%Y %H:%M:%S')} {self.id}"
        )

    def is_player_move_valid(self, start_coords: int, end_coords: int) -> bool:
        """Return whether or not the player move is valid.

        We take for granted that the given input is correct and the
        starting tile does have the correct piece code.

        Parameters
        ----------
        start_tile : int
            Starting coords of the piece.
        end_tile : int
            Ending coords of the piece.

        Returns
        -------
        bool
            Returns whether or not a move is valid.
        """
        piece = self.board.state[start_coords]
        moves = piece.get_moves(self.board.state)
        # For each simulated move, if the king is in check, then the move is invalid.

        # sim_state = self.board.simulated_board_state()
        # sim_state[end_coords] = sim_state[start_coords]
        # for move in moves:
        #     sim_state = self.board.simulated_board_state()
        #     sim_state_copy = sim_state.copy()
        print(self.board.w_king[0].in_check(self.board.b_pieces, self.board.state))
        # moves = Piece.get_moveset(start_tile, piece_code)

        # possible_moves = Move.remove_off_bounds_tiles(moves)

        print(f"{piece.symbol}: {start_coords} --> {end_coords}")
        print(f"moves: {moves}")
        return end_coords in moves

    def register_move(self, old_coords: tuple, new_coords: tuple):
        """Register the a move.

        Find the Piece objs on the given coords and change their attr accordantly.


        Parameters
        ----------
        old_coords : tuple
            The old coords of the piece.
        new_coords : tuple
            The new coords of the piece.
        """
        # Update pieces.
        moving_piece = self.board.state[old_coords]
        moving_piece.set_coords(new_coords)
        taken_piece = self.board.state[new_coords]
        if isinstance(taken_piece, Piece):
            del taken_piece

        # Update board state.
        self.board.state[new_coords] = self.board.state[old_coords]
        self.board.state[old_coords] = Piece.EMPTY
        self.is_white_turn = not self.is_white_turn
        print(self.board)

    def is_piece_pickable(self, piece) -> bool:
        """Determine if you can pick a piece.

        If the piece is on the same colour as the player
        who is turn to play then the pick is pickable.
        """
        # return isinstance(piece, Piece) and piece.is_white == self.is_white_turn
        return True
