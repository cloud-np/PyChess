"""Includes the class for each Pawn."""
from chess.pieces.piece import Piece
from chess.move import MoveDirection


class King(Piece):
    """Has specific functions tied to a King obj.

    Parameters
    ----------
    Piece : Piece
        The base class we inherit from.
    """

    def __init__(self, piece_code: int, coords: tuple):
        """Init the King.

        Parameters
        ----------
        piece_code : int
            A binary way to represent our pieces.
        coords : tuple
            The coordinates of the piece.
        """
        self.range_limit = 2
        self.enemy_color = Piece.BLACK if Piece.get_colour(piece_code) == Piece.WHITE else Piece.WHITE
        super().__init__(piece_code, coords)

    def in_check(self, enemies_pieces, board_state):
        """Check if the king is in check."""

        # Check if the king is in check from the rest of the pieces
        enemy_moves = set()
        for piece_code, enemy_list in enemies_pieces.items():
            if piece_code == Piece.PAWN | self.enemy_color:
                continue
            for en in enemy_list:
                enemy_moves = enemy_moves | en.get_moves(board_state)

            if self.coords in enemy_moves:
                return True

        # Check if the king is in check from pawns
        enemy_pawns = enemies_pieces[Piece.PAWN | self.enemy_color]
        for en_pawn in enemy_pawns:
            enemy_moves = enemy_moves | en_pawn.get_attack_moves(board_state)
            if self.coords in enemy_moves:
                return True

        return False

    def get_moves(self, board_state):
        """Override the get_moves from Piece class."""
        moves = set()
        for md in [MoveDirection.UP, MoveDirection.DOWN, MoveDirection.LEFT, MoveDirection.RIGHT, MoveDirection.UP_LEFT,
                   MoveDirection.UP_RIGHT, MoveDirection.DOWN_LEFT, MoveDirection.DOWN_RIGHT]:
            self.add_moves_in_direction(board_state, moves, md)
        return moves

    # def in_checkmate(self):
    #     """Check if the king is in checkmate."""
    #     return self.in_check

    # def in_stalemate(self):
    #     """Check if the king is in stalemate."""
    #     return self.in_check

    # def in_draw(self):
    #     """Check if the king is in draw."""
    #     return self.in_check

    # def in_threefold_repetition(self):
    #     """Check if the king is in threefold repetition."""
    #     return self.in_check

    # def insufficient_material(self):
    #     """Check if the king is in insufficient material."""
    #     return self.in_check

    # def in_fifty_move_rule(self):
    #     """Check if the king is in fifty move rule."""
    #     return self.in_check
