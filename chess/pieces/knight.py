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

    def get_possible_coords(self, board_state):  # sourcery skip: merge-duplicate-blocks
        """Override the get_moves from Piece class."""
        # We could be 'fancy' and use permutation but it generates 4 more cases
        # which we do not need and it would take couple ifs to get rid of them.
        possible_coords = [(self.coords[0] - 1, self.coords[1] - 2),
                           (self.coords[0] - 2, self.coords[1] - 1),
                           (self.coords[0] + 1, self.coords[1] - 2),
                           (self.coords[0] + 2, self.coords[1] - 1),

                           (self.coords[0] + 1, self.coords[1] + 2),
                           (self.coords[0] + 2, self.coords[1] + 1),
                           (self.coords[0] - 1, self.coords[1] + 2),
                           (self.coords[0] - 2, self.coords[1] + 1)]
        coords_set = set()
        for coords in possible_coords:
            piece_code = board_state[coords]
            # if piece_code == Piece.INVALID:
            #     pass
            if piece_code == Piece.EMPTY:
                coords_set.add(coords)
            elif Piece.get_color(piece_code) == self.enemy_color:
                coords_set.add(coords)
        return coords_set
