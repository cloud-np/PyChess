"""Includes the class for each Pawn."""
from chess.pieces.piece import Piece


class Knight(Piece):
    """Has specific functions tied to a Knight obj.

    Parameters
    ----------
    Piece : Piece
        The base class we inherit from.
    """

    def __init__(self, piece_code: int, coords: tuple):
        """Init the Knight.

        Parameters
        ----------
        piece_code : int
            A binary way to represent our pieces.
        coords : tuple
            The coordinates of the piece.
        """
        super().__init__(piece_code, coords)

    def get_moves(self):
        """Override the get_moves from Piece class."""
        return 0
