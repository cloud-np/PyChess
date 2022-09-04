"""Includes the base class for each Piece."""
import numpy as np
from typing import Tuple, Set, Optional, List, Dict, Callable, Literal


class CastleSide:
    """Represents a side of a castle."""

    WK_SIDE_L = 0
    WK_SIDE_R = 1
    BK_SIDE_L = 2
    BK_SIDE_R = 3

    @staticmethod
    def get_side(end_coords) -> Optional[int]:
        """Return the side of the castle.

        We use .get() to avoid KeyErrors.
        """
        return {
            (7, 6): CastleSide.WK_SIDE_R,
            (7, 2): CastleSide.WK_SIDE_L,
            (0, 6): CastleSide.BK_SIDE_R,
            (0, 2): CastleSide.BK_SIDE_L,
        }.get(end_coords)

    @staticmethod
    def get_rook_posistions(castling_side: int) -> tuple:
        """Return the positions of the rooks involved in a castling.

        Based on the castling side we return the positions of the rook before and after the castling.
        """
        if castling_side == CastleSide.WK_SIDE_R:
            return (7, 5), (7, 7)
        elif castling_side == CastleSide.WK_SIDE_L:
            return (7, 3), (7, 0)
        elif castling_side == CastleSide.BK_SIDE_R:
            return (0, 5), (0, 7)
        elif castling_side == CastleSide.BK_SIDE_L:
            return (0, 3), (0, 0)
        else:
            raise ValueError("Invalid castling side.")


class Piece:
    """Base class that holds info about the piece."""

    EMPTY = 0x0  # 0
    KING = 0x1  # 1
    PAWN = 0x2  # 2
    KNIGHT = 0x3  # 3
    BISHOP = 0x4  # 4
    ROOK = 0x5  # 5
    QUEEN = 0x6  # 6

    A_PAWN = 0x10  # 16
    B_PAWN = 0x20  # 32
    C_PAWN = 0x30  # 48
    D_PAWN = 0x40  # 64
    E_PAWN = 0x50  # 80
    F_PAWN = 0x60  # 96
    G_PAWN = 0x70  # 112
    H_PAWN = 0x80  # 128
    LEFT_PIECE = 0x90  # 144
    RIGHT_PIECE = 0xA0  # 160

    WHITE = 0x100  # 256
    BLACK = 0x200  # 512
    INVALID = 0x300  # 4096

    TYPE_MASK = 0xF  # 7
    # ANTI_TYPE_MASK = 0xFF0
    UNIQUE_PIECE_MASK = 0xF0  # 240
    COLOR_MASK = 0xF00  # 3840

    WK_R_CASTLE = [(7, 5), (7, 6)]
    BK_R_CASTLE = [(0, 5), (0, 6)]
    WK_L_CASTLE = [(7, 3), (7, 2), (7, 1)]
    BK_L_CASTLE = [(0, 3), (0, 2), (0, 1)]

    WHITE_KING = WHITE | KING
    BLACK_KING = BLACK | KING

    @staticmethod
    def get_the_specific_piece(piece: np.uint32) -> int:
        """Return which specific piece is this."""
        return piece & Piece.UNIQUE_PIECE_MASK

    @staticmethod
    def get_enemy_color(our_piece: np.uint32) -> int:
        """Given a piece code return the enemy color."""
        return Piece.WHITE if Piece.get_color(our_piece) == Piece.BLACK else Piece.BLACK

    @staticmethod
    def get_castle_coords(piece: np.uint32, side: int) -> Optional[List[Tuple[int, int]]]:
        if Piece.get_type(piece) == Piece.KING:
            return {
                Piece.WHITE | Piece.RIGHT_PIECE: [(7, 5), (7, 6)],
                Piece.WHITE | Piece.LEFT_PIECE: [(7, 3), (7, 2), (7, 1)],
                Piece.BLACK | Piece.RIGHT_PIECE: [(0, 5), (0, 6)],
                Piece.BLACK | Piece.LEFT_PIECE: [(0, 3), (0, 2), (0, 1)],
            }[Piece.get_color(piece) | side]
        return None

    @staticmethod
    def get_type(piece: np.uint32) -> np.uint32:
        """Filter the piece and find the piece type.

        Parameters
        ----------
        piece : uint8
            A binary way to represent our pieces

        Returns
        -------
        int
            This will return only the type part of the binary num.
        """
        return piece & Piece.TYPE_MASK

    @staticmethod
    def get_symbol(piece: np.uint32) -> str:
        """Return the correct unicode symbol."""
        ptype = Piece.get_type(piece)
        color = Piece.get_color(piece)
        if ptype == Piece.PAWN:
            return "♙" if color == Piece.WHITE else "♟︎"
        elif ptype == Piece.BISHOP:
            return "♗" if color == Piece.WHITE else "♝︎"
        elif ptype == Piece.KNIGHT:
            return "♘" if color == Piece.WHITE else "♞︎"
        elif ptype == Piece.ROOK:
            return "♖" if color == Piece.WHITE else "♜︎"
        elif ptype == Piece.QUEEN:
            return "♕" if color == Piece.WHITE else "♛︎"
        elif ptype == Piece.KING:
            return "♔" if color == Piece.WHITE else "♚︎"
        elif ptype == Piece.EMPTY:
            return " "
        else:
            raise Exception("Not a valid piece to get a symbol!")

    @staticmethod
    def get_color(piece: np.uint32) -> Literal[256, 512]:
        """Filter the piece and find the piece color.

        Parameters
        ----------
        piece : uint8
            A binary way to represent our pieces

        Returns
        -------
        int
            This will return only the color part of the binary num.
        """
        return piece & Piece.COLOR_MASK

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
    def get_img_for_piece(piece, imgs_path: str) -> str:
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
        if piece == Piece.EMPTY:
            return ""
        path = f"{imgs_path}/"
        color = Piece.get_color(piece)
        ptype = Piece.get_type(piece)

        if color == Piece.WHITE:
            path += "w"
        elif color == Piece.BLACK:
            path += "b"

        if ptype == Piece.KING:
            path += "k"
        elif ptype == Piece.PAWN:
            path += "p"
        elif ptype == Piece.KNIGHT:
            path += "n"
        elif ptype == Piece.BISHOP:
            path += "b"
        elif ptype == Piece.ROOK:
            path += "r"
        elif ptype == Piece.QUEEN:
            path += "q"

        return f"{path}.png"
