"""A module for tools related to board utils."""
from chess.pieces.piece import Piece
from typing import Literal, Optional, Tuple
import chess.board as board 


class BoardUtils:
    """A collection of static methods for board related operations."""

    @staticmethod
    def is_in_bound(coord: Tuple[int, int]) -> bool:
        return all(0 <= ax <= 7 for ax in coord)

    @staticmethod
    def swap_colors(color: int) -> Literal[256, 512]:
        """Swap the colors."""
        return Piece.WHITE if color == Piece.BLACK else Piece.BLACK

    # FIXME Needs refactoring because of the new board representation.
    # @staticmethod
    # def find_tile_from_str(row: str, col: str) -> int:
    #     """Find the tile given the row and col names."""
    #     _col: int = BoardUtils.get_number_for_col(col)
    #     _row: int = 8 - int(row)
    #     return (_row * 8) + _col
    
    @staticmethod
    def get_coords_from_index(index: int) -> Tuple[int, int]:
        """Find the tile given the row and col names."""
        _row, _col = divmod(index, 8)
        return _row, _col

    @staticmethod
    def get_index_from_coords(index: Tuple[int, int]) -> int:
        """Find the tile given the row and col names."""
        return (index[0] * 8) + index[1]
    
    # @staticmethod
    # def get_color_to_move(last_piece_moved: Optional[int], fen: str) -> int:
    #     if not last_piece_moved:
    #         return board.Fen.get_color_to_move(fen)
    #     return Piece.WHITE if Piece.get_color(last_piece_moved) == Piece.BLACK else Piece.BLACK

    @staticmethod
    def get_col_for_number(number: int) -> str:
        """Get the corrisponding number based on the given col name."""
        return chr(ord('a') + number)

    @staticmethod
    def get_number_for_col(col: str) -> int:
        """Get the corrisponding number based on the given col name."""
        # 97 because ord('a') == 97
        num_col = ord(col) - 97
        if not 0 <= num_col < 8:
            raise ValueError(f"Wrong value for collumn: {col}")
        return num_col
