"""Includes the class for each Pawn."""
from chess.pieces.piece import Piece


class Pawn(Piece):
    """Has specific functions tied to a Pawn obj.

    Parameters
    ----------
    Piece : Piece
        The base class we inherit from.
    """

    def __init__(self, piece_code: int, coords: tuple):
        """Init the pawn.

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
        moves = set()
        if self.color == Piece.WHITE:
            if self.coords[0] >= 1:
                moves.add((self.coords[0] - 1, self.coords[1]))
            if self.coords[0] == 6:
                moves.add((self.coords[0] - 2, self.coords[1]))
        else:
            if self.coords[0] <= 6:
                moves.add((self.coords[0] + 1, self.coords[1]))
            if self.coords[0] == 1:
                moves.add((self.coords[0] + 2, self.coords[1]))
        return moves
