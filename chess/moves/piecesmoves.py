import numpy as np
from .move import Move, MoveDirection
from typing import Tuple, Set, Callable, Dict, Optional
from chess.pieces.piece import Piece
from chess.board import BoardUtils

class PiecesMoves:

    @staticmethod
    def knight_moves(state, piece_info):
        """Knight moves."""
        # We could get 'fancy' and use permutation but it generates 4 more cases
        # which we do not need and it would take couple ifs to get rid of them.
        pcoords = piece_info[1]
        possible_coords = [
            (pcoords[0] - 1, pcoords[1] - 2),
            (pcoords[0] - 2, pcoords[1] - 1),
            (pcoords[0] + 1, pcoords[1] - 2),
            (pcoords[0] + 2, pcoords[1] - 1),
            (pcoords[0] + 1, pcoords[1] + 2),
            (pcoords[0] + 2, pcoords[1] + 1),
            (pcoords[0] - 1, pcoords[1] + 2),
            (pcoords[0] - 2, pcoords[1] + 1),
        ]

        return {
            crd
            for crd in possible_coords
            if BoardUtils.is_in_bound(crd)
            and (
                state[crd] == Piece.EMPTY
                or Piece.get_color(state[crd]) == Piece.get_enemy_color(piece_info[0])
            )
        }

    @staticmethod
    def queen_moves(state, piece_info):
        """Override the get_moves from Piece class."""
        moves = set()
        for md in [
            MoveDirection.UP,
            MoveDirection.DOWN,
            MoveDirection.LEFT,
            MoveDirection.RIGHT,
            MoveDirection.UP_LEFT,
            MoveDirection.UP_RIGHT,
            MoveDirection.DOWN_LEFT,
            MoveDirection.DOWN_RIGHT,
        ]:
            PiecesMoves.add_moves_in_direction(state, 8, piece_info, moves, md)
        return moves

    @staticmethod
    def rook_moves(state, piece_info):
        """Override the get_moves from Piece class."""
        moves = set()
        for md in [
            MoveDirection.UP,
            MoveDirection.DOWN,
            MoveDirection.LEFT,
            MoveDirection.RIGHT,
        ]:
            PiecesMoves.add_moves_in_direction(state, 8, piece_info, moves, md)
        return moves

    @staticmethod
    def bishop_moves(state, piece_info):
        """Override the get_moves from Piece class."""
        moves = set()
        for md in [
            MoveDirection.UP_LEFT,
            MoveDirection.UP_RIGHT,
            MoveDirection.DOWN_LEFT,
            MoveDirection.DOWN_RIGHT,
        ]:
            PiecesMoves.add_moves_in_direction(state, 8, piece_info, moves, md)
        return moves

    @staticmethod
    def king_moves(state, piece_info):
        """Override the get_moves from Piece class."""
        moves = set()
        for md in [
            MoveDirection.UP,
            MoveDirection.DOWN,
            MoveDirection.LEFT,
            MoveDirection.RIGHT,
            MoveDirection.UP_LEFT,
            MoveDirection.UP_RIGHT,
            MoveDirection.DOWN_LEFT,
            MoveDirection.DOWN_RIGHT,
        ]:
            PiecesMoves.add_moves_in_direction(state, 2, piece_info, moves, md)
        return moves

    @staticmethod
    def pawn_attack_moves(state, piece_info: Dict[int, Tuple[int, int]], en_passant: Optional[Tuple[int, int]]) -> Set[Tuple[int, int]]:
        """Get the attackable coords for the pawn."""
        moves: Set[Tuple[int, int]] = set()
        pcolor: int = Piece.get_color(piece_info[0])
        coords: Tuple[int, int] = piece_info[1]

        if pcolor == Piece.WHITE:
            l_coords = coords[0] - 1, coords[1] - 1
            r_coords = coords[0] - 1, coords[1] + 1
        else:
            l_coords = coords[0] + 1, coords[1] - 1
            r_coords = coords[0] + 1, coords[1] + 1

        # We check for the enemy color to avoid to check for Piece.INVALID
        # for example [5, 8] checks for != Piece.EMPTY and has diff color vs our pcolor
        # Left enemy
        if BoardUtils.is_in_bound(l_coords):
            left_enemy = state[l_coords]
            if (
                left_enemy != Piece.EMPTY
                and Piece.get_enemy_color(left_enemy) == pcolor
            ):
                moves.add(l_coords)
            elif en_passant is not None and en_passant == l_coords:
                moves.add(l_coords)
        # Right enemy
        if BoardUtils.is_in_bound(r_coords):
            right_enemy = state[r_coords]
            if (
                right_enemy != Piece.EMPTY
                and Piece.get_enemy_color(right_enemy) == pcolor
            ):
                moves.add(r_coords)
            elif en_passant is not None and en_passant == r_coords:
                moves.add(r_coords)

        return moves

    @staticmethod
    def pawn_moves(state, piece_info, en_passant: Tuple[int, int]):
        """Override the get_moves from Piece class."""
        moves = set()
        piece, piece_coords = piece_info
        if Piece.get_color(piece) == Piece.WHITE:
            if piece_coords[0] >= 1:
                coords_to_go = piece_coords[0] - 1, piece_coords[1]
                piece = state[coords_to_go]
                if piece == Piece.EMPTY:
                    moves.add(coords_to_go)
            if piece_coords[0] == 6:
                coords_to_go = piece_coords[0] - 2, piece_coords[1]
                piece = state[piece_coords[0] - 1, piece_coords[1]]
                piece2 = state[coords_to_go]
                if piece == Piece.EMPTY and piece2 == Piece.EMPTY:
                    moves.add(coords_to_go)
        else:
            if piece_coords[0] <= 6:
                coords_to_go = piece_coords[0] + 1, piece_coords[1]
                piece = state[coords_to_go]
                if piece == Piece.EMPTY:
                    moves.add(coords_to_go)
            if piece_coords[0] == 1:
                coords_to_go = piece_coords[0] + 2, piece_coords[1]
                piece = state[piece_coords[0] + 1, piece_coords[1]]
                piece2 = state[coords_to_go]
                if piece == Piece.EMPTY and piece2 == Piece.EMPTY:
                    moves.add(coords_to_go)
        # moves = [m for m in moves if 0 < m[0] < 7]

        # for i in indexes:
        #     if not 0 <= i <= 7:
        #         return Piece.INVALID
        moves |= PiecesMoves.pawn_attack_moves(state, piece_info, en_passant)
        return moves

    @staticmethod
    def add_moves_in_direction(
        state,
        range_limit: int,
        piece_info: Tuple[int, Tuple[int, int]],
        coords_set: Set[Tuple[int, int]],
        direction: int,
    ) -> None:
        """Found the all moves based of the 'direction' a direction.

        Given a direction it will generate all the moves until it hits either:
        1. An invalid block.
        2. An ally Piece.
        3. An enemy Piece (which he will inclide his square).

        Parameters
        ----------
        state : BoardStateList
            A 2d custom matrix that holds information about all the pieces on board.
        coords_set : Set[Tuple[int, int]]
            The set of the valid coords based on the criteria we added above.

        direction : MoveDirection
            The direction of which we want to generate moves to.
        """
        direction_func: Callable = Move.get_direction_func(direction)
        curr_pcolor = Piece.get_color(piece_info[0])
        for i in range(1, range_limit):
            coords: Tuple[int, int] = direction_func(piece_info[1], i)
            if not BoardUtils.is_in_bound(coords):
                break
            dir_pc = state[coords]
            dir_pcolor = Piece.get_color(dir_pc)
            if dir_pc == Piece.EMPTY:
                coords_set.add(coords)
            elif dir_pcolor == curr_pcolor:
                break
            else:
                coords_set.add(coords)
                break