"""Anything related to a move how it was executed."""
from typing import Callable, Set, Tuple
from chess.board import BoardUtils
import numpy as np
import re

# from chess.board import Board


def WRONG_INPUT(u_input, msg="Wrong move input:"):
    """Just a helper function to more readable maybe value errors."""
    return ValueError(f"{msg} {u_input}")


PIECE_SYMBOLS = "rnbqk"
TILE_NUMBERS = "12345678"
TILE_NAMES = "abcdefgh"

""" We should hardcode this values so we can evaluate
    faster which moves are in-bounds or not. """
INVALID_TILES: Set[int] = {
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18,
    20, 30, 40, 60, 70, 80, 90, 19, 29, 39, 49, 59, 69, 79, 89, 99, 100,
    101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114,
    115, 116, 117, 118, 119,
}


class MoveDirection:
    """An enum class that helps showing the direction of a move."""

    # Horizontal directions
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3

    # Diagonal directions
    UP_LEFT = 4
    UP_RIGHT = 5
    DOWN_LEFT = 6
    DOWN_RIGHT = 7


class Move:
    """To preserve memory during search, moves are stored as 16 bit numbers.
    The format is as follows:
        bit 0-5: from square (0 to 63)
        bit 6-11: to square (0 to 63)
        bit 12-15: flag
    """
    NORMAL = 0
    EN_PASSANT_CAPTURE = 1
    CASTLE = 2
    PROMOTE_QUEEN = 3
    PROMOTE_BISHOP = 4
    PROMOTE_ROOK = 5
    PROMOTE_KNIGHT = 6
    PAWN_TWO_STEP = 7

    START_COORDS_MASK = 0b0000000000111111
    SECOND_COORDS_MASK = 0b0000111111000000
    FLAG_MASK = 0b1111000000000000


    def __init__(
        self,
        move_value: int,
        moving_piece: np.uint32,
        start_coords: Tuple[int, int],
        end_coords: Tuple[int, int],
        castle_side,
        old_fen: str,
        curr_fen: str,
    ):
        """Components to indentify a move."""
        self.move_value: int = move_value
        self.moving_piece: np.uint32 = moving_piece
        self.start_coords: Tuple[int, int] = start_coords
        self.end_coords: Tuple[int, int] = end_coords
        self.castle_side = castle_side
        self.old_fen: str = old_fen
        self.curr_fen: str = curr_fen 
    
    @staticmethod
    def get_start_coords(move_value: int) -> Tuple[int, int]:
        return BoardUtils.get_coords_from_index(move_value & Move.START_COORDS_MASK)

    @staticmethod
    def get_end_coords(move_value: int) -> Tuple[int, int]:
        return BoardUtils.get_coords_from_index((move_value >> 5) & Move.SECOND_COORDS_MASK)

    @staticmethod
    def get_flag(move_value: int) -> int:
        return (move_value >> 11) & Move.FLAG_MASK

    @staticmethod
    def get_direction_func(direction: int) -> Callable:
        """Return the function that corrisponds to the move direction."""
        return {
            MoveDirection.UP: Move.up,
            MoveDirection.DOWN: Move.down,
            MoveDirection.LEFT: Move.left,
            MoveDirection.RIGHT: Move.right,
            MoveDirection.UP_LEFT: Move.up_left,
            MoveDirection.UP_RIGHT: Move.up_right,
            MoveDirection.DOWN_LEFT: Move.down_left,
            MoveDirection.DOWN_RIGHT: Move.down_right,
        }[direction]

    # Horizontal directions ###############
    @staticmethod
    def up(coords, i) -> Tuple[int, int]:
        """Return a move that has a direction upwards."""
        return coords[0] - i, coords[1]

    @staticmethod
    def down(coords, i) -> Tuple[int, int]:
        """Return a move that has a direction downwards."""
        return coords[0] + i, coords[1]

    @staticmethod
    def right(coords, i) -> Tuple[int, int]:
        """Return a move that has a direction right."""
        return coords[0], coords[1] + i

    @staticmethod
    def left(coords, i) -> Tuple[int, int]:
        """Return a move that has a direction left."""
        return coords[0], coords[1] - i

    # Diagonal directions ###############
    @staticmethod
    def up_left(coords, i) -> Tuple[int, int]:
        """Return a move that has a direction upwards."""
        return coords[0] - i, coords[1] - i

    @staticmethod
    def up_right(coords, i) -> Tuple[int, int]:
        """Return a move that has a direction upwards."""
        return coords[0] - i, coords[1] + i

    @staticmethod
    def down_left(coords, i) -> Tuple[int, int]:
        """Return a move that has a direction upwards."""
        return coords[0] + i, coords[1] - i

    @staticmethod
    def down_right(coords, i) -> Tuple[int, int]:
        """Return a move that has a direction upwards."""
        return coords[0] + i, coords[1] + i

    # TODO: This is outdated.
    # @staticmethod
    # def find_move_direction(start: int, end: int):
    #     diff = end - start

    #     if (diff % 7) == 0:
    #         steps = diff // 7
    #         # UpRight - DownLeft
    #         return -7 if steps < 0 else 7
    #     elif (diff % 8) == 0:
    #         steps = diff // 8
    #         if steps == 0:
    #             # Left - Right
    #             return -1 if diff < 0 else 1
    #         else:
    #             # Up - Down
    #             return -8 if steps < 0 else 8
    #     elif (diff % 9) == 0:
    #         steps = diff // 9
    #         # UpLeft - DownRight
    #         return -9 if steps < 0 else 9


class MoveDecoder:
    """Decodes a move string to a move object."""

    # def __init__(self, input_str: str):
    #     """Components to indentify a move.

    #     Parameters
    #     ----------
    #     input_str : str
    #         The inputed move string.
    #     """
    #     self.input_str = input_str
    #     self.coords = self.__parse_coords()

    @staticmethod
    def parse_coords(input_str) -> Tuple[Tuple[int, int], Tuple[int, int]] | Tuple[None, None]:
        """Parse the coords of the move from the input string.

        Parameters
        ----------
        input_str : str
            The input string of the user.

        Returns
        -------
        Tuple[Tuple[int, int], Tuple[int, int]] | Tuple[None, None]:
            The coords of the move or None if the input string is invalid.
        """
        if re.search("[a-h][1-8]{1}", input_str):
            # We have a valid move.
            start_tile = MoveDecoder.get_tile_coords(input_str[:2])
            end_tile = MoveDecoder.get_tile_coords(input_str[2:])
            return start_tile, end_tile
        return None, None

    @staticmethod
    def get_tile_coords(tile: str):
        """Get the tile coordinates from a tile string."""
        # We parse the coords in the way our array is set up.
        x = 8 - int(tile[1])
        y = ord(tile[0]) - ord("a")
        return x, y

    @staticmethod
    def encode_to_str(coords: Tuple[int, int]) -> str:
        """Encode the coords to a string."""
        return chr(ord("a") + coords[1]) + str(8 - coords[0])

    # def __str__(self):
    #     return (
    #         f"start_tile: {self.start_tile}\n"
    #         f"end_tile: {self.end_tile}\n"
    #         f"piece: {self.piece}\n"
    #         f"move_code: {self.move_code}\n"
    #     )

    @staticmethod
    def is_symbol_turn(move_str: str, is_white_turn: bool):
        """Given the first symbol show if the given piece is correct.

        Parameters
        ----------
        move_str : str
            The user input
        is_white_turn : bool
            Shows which teams turn is to play.

        Returns
        -------
        bool
            Return if the first symbol input is correct.

        Raises
        ------
        WRONG_INPUT
            If its wrong character or its not this teams turn to play.
        """
        if (move_str[0] not in TILE_NAMES) and (
            (move_str[0].isupper() and not is_white_turn)
            or (move_str[0].islower() and is_white_turn)
        ):
            raise WRONG_INPUT(move_str, msg="Wrong piece team entered.")
        return True

    @staticmethod
    def check_symbol_for_action(move_code: int, ch: str):
        if ch == "x":
            return Move.add_action(move_code, MoveTypes.TAKES), True
        elif ch == "+":
            return Move.add_action(move_code, MoveTypes.CHECK), True
        elif ch == "#":
            return Move.add_action(move_code, MoveTypes.CHECKMATE), True
        return move_code, False

    @staticmethod
    def remove_off_bounds_tiles(moves: Set[int]):
        """Filter the invalid tiles.

        Parameters
        ----------
        moves : Set[int]
            A set of moves that the piece could go in theory.

        Returns
        -------
          Set[int]
            The new filtered set without the out of bounds tiles.
        """
        return moves - INVALID_TILES

    @staticmethod
    def add_action(move_code: int, move_action: int) -> int:
        """Check if move action has been repeated.

        Parameters
        ----------
        move_code : int
            A binary way to represent our moves.
        move_action : int
            A binary way to show the type of the move action.
        """
        if (move_code & MoveTypes.MOVE_MASK) == move_action:
            move_code = MoveTypes.VALUE_ERROR
        else:
            move_code |= move_action
        return move_code
