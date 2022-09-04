"""Includes the class for each Pawn."""
from chess.pieces.piece import Piece
from chess.moves.move import MoveDirection


class Queen(Piece):
    """Has specific functions tied to a Queen obj.

    Parameters
    ----------
    Piece : Piece
        The base class we inherit from.
    """

    def __init__(self, piece: np.uint32, coords: tuple):
        """Init the Queen.

        Parameters
        ----------
        piece : int
            A binary way to represent our pieces.
        coords : tuple
            The coordinates of the piece.
        """
        self.range_limit = 8
        super().__init__(piece, coords)

    def get_possible_coords(self, state):
        """Override the get_moves from Piece class."""
        moves = set()
        for md in [MoveDirection.UP, MoveDirection.DOWN, MoveDirection.LEFT, MoveDirection.RIGHT, MoveDirection.UP_LEFT,
                   MoveDirection.UP_RIGHT, MoveDirection.DOWN_LEFT, MoveDirection.DOWN_RIGHT]:
            self.add_moves_in_direction(state, moves, md)
        return moves
