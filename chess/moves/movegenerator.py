import numpy as np
from .move import Move
from chess.moves.piecesmoves import PiecesMoves
from typing import Literal, Tuple, List, Set, Callable, Dict, Optional
from chess.pieces.piece import Piece
from chess.board import Board, BoardUtils

class MoveGenerator:

    def __init__(self, board: Board) -> None:
        self.board = board
    
    def get_all_moves(self) -> List[Tuple[np.uint32, Tuple[int, int]]]:
        ...

    def is_king_in_check(self, enemies, king_coords) -> bool:
        """Check if the king is in check."""
        for _, enemy_list in enemies.items():
            for e, ecrd in enemy_list.items():
                if king_coords in self.get_possible_coords((e, ecrd)):
                    return True
        return False

    def are_coords_under_attack(self, coords_list: List[Tuple[int, int]], color: Literal[256, 512]) -> bool:
        """Check if any of the given coords are being attacked.

        Parameters
        ----------
        coords_list : List[Tuple[int, int]]
            A list of coords to check if they are being attacked.
        enemy_color : int
            The color of the enemy pieces.
        enemies_pieces : List[Piece]
            The enemy pieces.

        Returns
        -------
        bool
            Returns true if any of the coords are being attacked.
        """
        # Check if the king is in check from the rest of the pieces
        enemy_moves = self.get_enemy_possible_coords(color)
        return any(tuple(coords) in enemy_moves for coords in coords_list)

    def get_enemy_possible_coords(self, color: Literal[256, 512]):
        """Get all the enemy moves."""
        enemy_possible_coords = set()
        for _, enemy_list in self.board.get_enemies(color).items():
            for e, ecrd in enemy_list.items():
                enemy_possible_coords = (
                    enemy_possible_coords | self.get_possible_coords((e, ecrd))
                )
        return enemy_possible_coords

    def get_possible_coords(self, piece_info: Tuple[np.uint32, Tuple[int, int]]) -> Set[Tuple[int, int]]:
        """Return all the possible coords for a piece.

        Returns all the possible coords given a piece and a state.

        Parameters
        ----------
            piece_info : Tuple[int, Tuple[int, int]]
                It containes the moving piece's piece and the coordinates of the piece.
        """
        ptype: np.uint32 = Piece.get_type(piece_info[0])
        piece_func: Callable = {
            Piece.KING: PiecesMoves.king_moves,
            Piece.PAWN: PiecesMoves.pawn_moves,
            Piece.KNIGHT: PiecesMoves.knight_moves,
            Piece.BISHOP: PiecesMoves.bishop_moves,
            Piece.ROOK: PiecesMoves.rook_moves,
            Piece.QUEEN: PiecesMoves.queen_moves,
        }[ptype]
        if ptype == Piece.PAWN:
            return piece_func(self.board.state, piece_info, self.board.en_passant)
        else:
            return piece_func(self.board.state, piece_info)