"""Includes the class for each Pawn."""
from chess.pieces.piece import Piece
from chess.move import MoveDirection


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
        self.range_limit = 8
        super().__init__(piece_code, coords)

    # def get_moves(self):
    #     """Override the get_moves from Piece class."""
    #     return 0

    def get_moves(self, board_state):
        """Get all possible moves for the Bishop.

        Parameters
        ----------
        board : Board
            The board that the piece is on.

        Returns
        -------
        set
            A set of all possible moves for the piece.
        """
        moves = set()
        # Get all possible moves for the Bishop.
        for md in [MoveDirection.UP_LEFT, MoveDirection.UP_RIGHT, MoveDirection.DOWN_LEFT, MoveDirection.DOWN_RIGHT]:
            self.add_moves_in_direction(board_state, moves, md)
        return moves
