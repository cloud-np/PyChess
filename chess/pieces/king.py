"""Includes the class for each Pawn."""
from chess.pieces.piece import Piece
from chess.moves.move import MoveDirection
import numpy as np


class King(Piece):
    """Has specific functions tied to a King obj.

    Parameters
    ----------
    Piece : Piece
        The base class we inherit from.
    """

    WK_R_CASTLE = [(7, 5), (7, 6)]
    BK_R_CASTLE = [(0, 5), (0, 6)]
    WK_L_CASTLE = [(7, 3), (7, 2), (7, 1)]
    BK_L_CASTLE = [(0, 3), (0, 2), (0, 1)]

    def __init__(self, piece: np.uint32, coords: tuple):
        """Init the King.

        Parameters
        ----------
        piece : int
            A binary way to represent our pieces.
        coords : tuple
            The coordinates of the piece.
        """
        self.range_limit = 2
        piece_colour = Piece.get_color(piece)
        self.r_castle = {'is_valid': True, 'coords_list': King.WK_R_CASTLE if piece_colour == Piece.WHITE else King.BK_R_CASTLE}
        self.l_castle = {'is_valid': True, 'coords_list': King.WK_L_CASTLE if piece_colour == Piece.WHITE else King.BK_L_CASTLE}
        super().__init__(piece, coords)

    def get_castling_coords(self, board):
        """Try adding the roke moves if they are valid."""
        possible_castle_coords = set()
        if self.times_moved > 0:
            return possible_castle_coords
        if self.r_castle['is_valid'] and not board.are_coords_under_attack(self.r_castle['coords_list'], self.enemy_color) and board.are_coords_empty(self.r_castle['coords_list']):
            possible_castle_coords.add((7, 6) if self.color == Piece.WHITE else (0, 6))

        if self.l_castle['is_valid'] and not board.are_coords_under_attack(self.l_castle['coords_list'], self.enemy_color) and board.are_coords_empty(self.l_castle['coords_list']):
            possible_castle_coords.add((7, 2) if self.color == Piece.WHITE else (0, 2))
        return possible_castle_coords

    def in_check(self, enemies_pieces, state):
        """Check if the king is in check."""
        # Check if the king is in check from the rest of the pieces
        enemy_possible_coords = set()
        for piece, enemy_list in enemies_pieces.items():
            if piece == Piece.PAWN | self.enemy_color:
                continue

            # NOTE: Keep track of the attacking direction of the enemy piece.
            #       THERE MAY BE 2 DIRECTIONS OF ATTACKING.
            for en in enemy_list:
                enemy_possible_coords = en.get_possible_coords(state)
                if self.coords in enemy_possible_coords:
                    return True

        # Check if the king is in check from pawns
        enemy_pawns = enemies_pieces[Piece.PAWN | self.enemy_color]
        for en_pawn in enemy_pawns:
            enemy_possible_coords = enemy_possible_coords | en_pawn.get_attack_possible_coords(state)
            if self.coords in enemy_possible_coords:
                return True

        return False

    def get_possible_coords(self, state):
        """Override the get_moves from Piece class."""
        moves = set()
        for md in [MoveDirection.UP, MoveDirection.DOWN, MoveDirection.LEFT, MoveDirection.RIGHT, MoveDirection.UP_LEFT,
                   MoveDirection.UP_RIGHT, MoveDirection.DOWN_LEFT, MoveDirection.DOWN_RIGHT]:
            self.add_moves_in_direction(state, moves, md)
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
