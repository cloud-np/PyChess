"""A module for tools related to board utils."""
from chess.pieces.piece import Piece
from typing import Literal


class BoardUtils:
    """A collection of static methods for board related operations."""

    @staticmethod
    def swap_colors(color: int) -> Literal[Piece.WHITE, Piece.BLACK]:
        """Swap the colors."""
        return Piece.WHITE if color == Piece.BLACK else Piece.BLACK

    # FIXME Needs refactoring because of the new board representation.
    @staticmethod
    def find_tile_from_str(row: str, col: str) -> int:
        """Find the tile given the row and col names."""
        _col: int = BoardUtils.get_number_for_col(col)
        _row: int = 8 - int(row)
        return (_row * 8) + _col

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
