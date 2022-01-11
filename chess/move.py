from typing import Set, Tuple
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
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
    16, 17, 18, 20, 30, 40, 60, 70, 80, 90, 19, 29, 39, 49,
    59, 69, 79, 89, 99, 100, 101, 102, 103, 104, 105, 106,
    107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119}


class MoveTypes:
    """A binary way to represent moves and move actions."""

    NORMAL = 0
    TAKES = 1
    CHECK = 2
    CASTLE_SHORT = 3
    CASTLE_LONG = 5
    CHECKMATE = 6
    EN_PASSAT = 7

    ILLEGAL = 8
    VALUE_ERROR = 16

    MOVE_MASK = 0b00111
    ERROR_MASK = 0b11000


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
    """Holds info about the move made."""

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
    def parse_coords(input_str) -> Tuple[int, int]:
        if re.search("[a-h][1-8]{1}", input_str):
            # We have a valid move.
            start_tile = Move.get_tile_coords(input_str[:2])
            end_tile = Move.get_tile_coords(input_str[2:])
            return start_tile, end_tile
        return Exception("Invalid move input.")

    @staticmethod
    def get_tile_coords(tile_str):
        """Get the tile coordinates from a tile string."""
        # We parse the coords in the way our array is set up.
        x = 8 - int(tile_str[1])
        y = ord(tile_str[0]) - ord('a')
        return x, y

    def __str__(self):
        return (
            f"start_tile: {self.start_tile}\n"
            f"end_tile: {self.end_tile}\n"
            f"piece_code: {self.piece_code}\n"
            f"move_code: {self.move_code}\n"
        )

    # TODO write this a bit cleaner.
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
        if (move_str[0] not in TILE_NAMES) and ((move_str[0].isupper() and not is_white_turn) or (move_str[0].islower() and is_white_turn)):
            raise WRONG_INPUT(move_str, msg="Wrong piece team entered.")
        return True

    # TODO A regex way should be way more readable but this works for now.

    # @staticmethod
    # def decode_to_move(move_str: str, board, is_white_turn: bool) -> 'Move':
    #     # Because of the case for e.g: "exf4"
    #     # we can't be sure if the piece is black or not
    #     piece_code = Piece.EMPTY
    #     move_code = MoveTypes.NORMAL
    #     start_tile = -1
    #     end_tile = -1

    #     # Find colour
    #     if Move.is_symbol_turn(move_str, is_white_turn) is True:
    #         piece_code |= Piece.WHITE if is_white_turn else Piece.BLACK

    #     # Find piece type
    #     if move_str[0].lower() in PIECE_SYMBOLS:
    #         piece_code |= Piece.find_piece_from_symbol(move_str[0].lower())
    #     else:
    #         piece_code |= Piece.PAWN

    #     if move_str[1] in TILE_NAMES:
    #         start_tile = board.get_tile_from_piece(piece_code, col=move_str[1])

    #     for i, ch in enumerate(move_str[1:]):
    #         move_code, is_action = Move.check_symbol_for_action(move_code, ch)
    #         if is_action is False:
    #             if ch in TILE_NUMBERS:
    #                 if start_tile == -1:
    #                     start_tile = board.find_tile_from_str(row=ch, col=move_str[i])
    #                 end_tile = board.find_tile_from_str(row=ch, col=move_str[i])
    #             # We can have a piece symbol only in the very first pos.
    #             elif ch not in (TILE_NUMBERS + TILE_NAMES):
    #                 raise WRONG_INPUT(move_str)

    #     return Move(piece_code, start_tile, end_tile, move_code, move_str)

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

    # Horizontal directions ###############
    @staticmethod
    def up(coords, i) -> Tuple[int]:
        """Return a move that has a direction upwards."""
        return coords[0] - i, coords[1]

    @staticmethod
    def down(coords, i) -> Tuple[int]:
        """Return a move that has a direction downwards."""
        return coords[0] + i, coords[1]

    @staticmethod
    def right(coords, i) -> Tuple[int]:
        """Return a move that has a direction right."""
        return coords[0], coords[1] + i

    @staticmethod
    def left(coords, i) -> Tuple[int]:
        """Return a move that has a direction left."""
        return coords[0], coords[1] - i

    # Diagonal directions ###############
    @staticmethod
    def up_left(coords, i) -> Tuple[int]:
        """Return a move that has a direction upwards."""
        return coords[0] - i, coords[1] - i

    @staticmethod
    def up_right(coords, i) -> Tuple[int]:
        """Return a move that has a direction upwards."""
        return coords[0] - i, coords[1] + i

    @staticmethod
    def down_left(coords, i) -> Tuple[int]:
        """Return a move that has a direction upwards."""
        return coords[0] + i, coords[1] - i

    @staticmethod
    def down_right(coords, i) -> Tuple[int]:
        """Return a move that has a direction upwards."""
        return coords[0] + i, coords[1] + i

    @staticmethod
    def get_direction_func(direction: MoveDirection):
        """Return the function that corrisponds to the move direction."""
        return {
            MoveDirection.UP: Move.up,
            MoveDirection.DOWN: Move.down,
            MoveDirection.LEFT: Move.left,
            MoveDirection.RIGHT: Move.right,
            MoveDirection.UP_LEFT: Move.up_left,
            MoveDirection.UP_RIGHT: Move.up_right,
            MoveDirection.DOWN_LEFT: Move.down_left,
            MoveDirection.DOWN_RIGHT: Move.down_right
        }[direction]

    # TODO check if this function works correctly.
    # Also make a direction enum or something.
    @staticmethod
    def find_move_direction(start: int, end: int):
        diff = end - start

        if (diff % 7) == 0:
            steps = diff // 7
            # UpRight - DownLeft
            return -7 if steps < 0 else 7
        elif (diff % 8) == 0:
            steps = diff // 8
            if steps == 0:
                # Left - Right
                return -1 if diff < 0 else 1
            else:
                # Up - Down
                return -8 if steps < 0 else 8
        elif (diff % 9) == 0:
            steps = diff // 9
            # UpLeft - DownRight
            return -9 if steps < 0 else 9

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

    # TODO Work in progress. (No real reason to make this yet)

    def encode_to_str(self) -> str:
        move_str = ""

        # if self.

        return move_str
