"""Includes the class for each Pawn."""
from chess.pieces.piece import Piece
from chess.move import MoveDirection


class RookCorner:
    """An enum for the rook corners."""

    BOTTOM_LEFT = 0
    BOTTOM_RIGHT = 1
    TOP_LEFT = 2
    TOP_RIGHT = 3


class Rook(Piece):
    """Has specific functions tied to a Rook obj.

    Parameters
    ----------
    Piece : Piece
        The base class we inherit from.
    """

    def __init__(self, piece_code: int, coords: tuple):
        """Init the Rook.

        Parameters
        ----------
        piece_code : int
            A binary way to represent our pieces.
        coords : tuple
            The coordinates of the piece.
        """
        self.range_limit = 8
        self.rook_corner = Rook.__get_rooks_corner(coords)
        super().__init__(piece_code, coords)

    @staticmethod
    def __get_rooks_corner(coords):
        return {
            (7, 7): RookCorner.BOTTOM_RIGHT,
            (7, 0): RookCorner.BOTTOM_LEFT,
            (0, 7): RookCorner.TOP_RIGHT,
            (0, 0): RookCorner.TOP_LEFT,
        }[coords]

    def get_possible_coords(self, board_state):
        """Override the get_moves from Piece class."""
        moves = set()
        for md in [MoveDirection.UP, MoveDirection.DOWN, MoveDirection.LEFT, MoveDirection.RIGHT]:
            self.add_moves_in_direction(board_state, moves, md)
        return moves
