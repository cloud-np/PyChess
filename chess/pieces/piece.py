"""Includes the base class for each Piece."""
from chess.move import MoveDirection, Move
from typing import Tuple, Set, Literal


class Piece:
    """Base class that holds info about the piece."""

    EMPTY = 0x0     # 0
    KING = 0x1      # 1
    PAWN = 0x2      # 2
    KNIGHT = 0x3    # 3
    BISHOP = 0x4    # 4
    ROOK = 0x5      # 5
    QUEEN = 0x6     # 6

    A_PAWN = 0x10                # 16
    B_PAWN = 0x20                # 32
    C_PAWN = 0x30                # 48
    D_PAWN = 0x40                # 64
    E_PAWN = 0x50                # 80
    F_PAWN = 0x60                # 96
    G_PAWN = 0x70                # 112
    H_PAWN = 0x80                # 128
    LEFT_PIECE = 0x90            # 144
    RIGHT_PIECE = 0xA0           # 160

    WHITE = 0x100      # 256
    BLACK = 0x200      # 512
    INVALID = 0x1000   # 4096

    TYPE_MASK = 0xF           # 7
    UNIQUE_PIECE_MASK = 0xF0  # 240
    COLOR_MASK = 0xF00        # 3840
    ERROR_MASK = 0xF000       # 61440

    @staticmethod
    def get_the_specific_piece(piece_code: int) -> int:
        """Return which specific piece is this."""
        return piece_code & Piece.UNIQUE_PIECE_MASK

    @staticmethod
    def get_enemy_color(our_piece_code: int) -> int:
        """Given a piece code return the enemy color."""
        return Piece.WHITE if Piece.get_color(our_piece_code) == Piece.BLACK else Piece.BLACK

    @staticmethod
    def get_enemy_possible_coords(enemy_pieces, board_state):
        """Get all the enemy moves."""
        enemy_possible_coords = set()
        for piece_code, enemy_list in enemy_pieces.items():
            for en in enemy_list:
                if piece_code == Piece.PAWN:
                    enemy_possible_coords = enemy_possible_coords | en.get_attack_possible_coords(board_state)
                else:
                    enemy_possible_coords = enemy_possible_coords | en.get_possible_coords(board_state)
        return enemy_possible_coords

    def add_moves_in_direction(self, board_state, coords_set: Set[Tuple[int]], direction: MoveDirection) -> None:
        """Found the all moves based of the 'direction' a direction.

        Given a direction it will generate all the moves until it hits either:
        1. An invalid block.
        2. An ally Piece.
        3. An enemy Piece (which he will inclide his square).

        Parameters
        ----------
        board_state : BoardStateList
            A 2d custom matrix that holds information about all the pieces on board.
        coords_set : set[tuple[int]]
            The set of the valid coords based on the criteria we added above.

        direction : MoveDirection
            The direction of which we want to generate moves to.
        """
        direction_func = Move.get_direction_func(direction)
        for i in range(1, self.range_limit):
            coords: Tuple[int, int] = direction_func(self.coords, i)
            piece_code = board_state[coords]
            color = Piece.get_color(piece_code)
            if piece_code == Piece.EMPTY:
                coords_set.add(coords)
            elif piece_code == Piece.INVALID or color == self.color:
                break
            elif color != self.color:
                coords_set.add(coords)
                break

    @staticmethod
    def get_type(piece_code: int) -> int:
        """Filter the piece_code and find the piece type.

        Parameters
        ----------
        piece_code : uint8
            A binary way to represent our pieces

        Returns
        -------
        int
            This will return only the type part of the binary num.
        """
        return piece_code & Piece.TYPE_MASK

    @staticmethod
    def get_symbol(piece_code: int) -> str:
        """Return the correct unicode symbol."""
        ptype = Piece.get_type(piece_code)
        color = Piece.get_color(piece_code)
        if ptype == Piece.PAWN:
            return '♙' if color == Piece.WHITE else '♟︎'
        elif ptype == Piece.BISHOP:
            return '♗' if color == Piece.WHITE else '♝︎'
        elif ptype == Piece.KNIGHT:
            return '♘' if color == Piece.WHITE else '♞︎'
        elif ptype == Piece.ROOK:
            return '♖' if color == Piece.WHITE else '♜︎'
        elif ptype == Piece.QUEEN:
            return '♕' if color == Piece.WHITE else '♛︎'
        elif ptype == Piece.KING:
            return '♔' if color == Piece.WHITE else '♚︎'
        elif ptype == Piece.EMPTY:
            return ' '
        else:
            raise Exception('Not a valid piece_code to get a symbol!')

    @staticmethod
    def get_color(piece_code: int) -> int:
        """Filter the piece_code and find the piece color.

        Parameters
        ----------
        piece_code : uint8
            A binary way to represent our pieces

        Returns
        -------
        int
            This will return only the color part of the binary num.
        """
        return piece_code & Piece.COLOR_MASK

    def set_coords(self, coords: tuple):
        """Setter for coords."""
        self.coords = coords

    def get_moves(self):
        """Stay for the other classes to implement.

        Raises
        ------
        Exception
            Incase the inheriting class did not implement this function this will raise.
        """
        raise Exception("Not implemented yet for this type of piece!")

    @staticmethod
    def get_img_for_piece(piece_code, imgs_path: str) -> str:
        """Find the correct img for a piece.

        Parameters
        ----------
        imgs_path : str
            The path to the images folder.

        Returns
        -------
        str
            The path of the piece img.
        """
        if piece_code == Piece.EMPTY:
            return ''
        path = f"{imgs_path}/"
        color = Piece.get_color(piece_code)
        ptype = Piece.get_type(piece_code)

        if color == Piece.WHITE:
            path += 'w'
        elif color == Piece.BLACK:
            path += 'b'

        if ptype == Piece.KING:
            path += 'k'
        elif ptype == Piece.PAWN:
            path += 'p'
        elif ptype == Piece.KNIGHT:
            path += 'n'
        elif ptype == Piece.BISHOP:
            path += 'b'
        elif ptype == Piece.ROOK:
            path += 'r'
        elif ptype == Piece.QUEEN:
            path += 'q'

        return f"{path}.png"
