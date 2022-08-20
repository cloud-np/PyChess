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

    def get_attack_possible_coords(self, board_state, coords_set=None):
        """Get the attackable coords for the pawn."""
        if coords_set is None:
            coords_set = set()

        if self.color == Piece.WHITE:
            l_coords = self.coords[0] - 1, self.coords[1] - 1
            r_coords = self.coords[0] - 1, self.coords[1] + 1
        else:
            l_coords = self.coords[0] + 1, self.coords[1] - 1
            r_coords = self.coords[0] + 1, self.coords[1] + 1

        # Left enemy
        left_enemy = board_state[l_coords]
        if (
            left_enemy != Piece.EMPTY and Piece.get_colour(left_enemy) == self.enemy_color
        ):
            coords_set.add(l_coords)

        # Right enemy
        right_enemy = board_state[r_coords]
        if (
            right_enemy != Piece.EMPTY and Piece.get_colour(right_enemy) == self.enemy_color
        ):
            coords_set.add(r_coords)

        return coords_set

    def is_transforming(self) -> bool:
        """Detect if the Pawn is transforming based on each position and color."""
        return self.coords[0] == {Piece.WHITE: 0, Piece.BLACK: 7}[self.color]

    def get_transform_possible_coords(self, board_state):
        ...

    # TODO: Maybe we can write this a bit more cleanly?
    def get_possible_coords(self, board_state):
        """Override the get_moves from Piece class."""
        coords_set = set()
        if self.color == Piece.WHITE:
            if self.coords[0] >= 1:
                piece_code = board_state[self.coords[0] - 1, self.coords[1]]
                if piece_code == Piece.EMPTY:
                    coords_set.add((self.coords[0] - 1, self.coords[1]))
            if self.coords[0] == 6:
                piece_code = board_state[self.coords[0] - 1, self.coords[1]]
                piece_code2 = board_state[self.coords[0] - 2, self.coords[1]]
                if piece_code == Piece.EMPTY and piece_code2 == Piece.EMPTY:
                    coords_set.add((self.coords[0] - 2, self.coords[1]))
        else:
            if self.coords[0] <= 6:
                piece_code = board_state[self.coords[0] + 1, self.coords[1]]
                if piece_code == Piece.EMPTY:
                    coords_set.add((self.coords[0] + 1, self.coords[1]))
            if self.coords[0] == 1:
                piece_code = board_state[self.coords[0] + 1, self.coords[1]]
                piece_code2 = board_state[self.coords[0] + 2, self.coords[1]]
                if piece_code == Piece.EMPTY and piece_code2 == Piece.EMPTY:
                    coords_set.add((self.coords[0] + 2, self.coords[1]))

        self.get_attack_possible_coords(board_state, coords_set)
        return coords_set
