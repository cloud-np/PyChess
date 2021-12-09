"""Includes the class for each Pawn."""
from chess.pieces.piece import Piece


class Bishop(Piece):
    """Has specific functions tied to a Bishop obj.

    Parameters
    ----------
    Piece : Piece
        The base class we inherit from.
    """

    def __init__(self, piece_code: int, coords: tuple):
        """Init the King.

        Parameters
        ----------
        color : int
            The color of the created piece.
        symbol : str
            The symbol that is shown when printing the piece.
        coords : tuple
            The coordinates of the piece.
        """
        super().__init__(piece_code, coords)

    def get_moves(self):
        """Override the get_moves from Piece class."""
        return 0
