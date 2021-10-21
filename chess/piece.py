"""Holds everything related to a piece."""
from typing import Dict, Set, Any


class Piece:
    """Info about the piece type moves-set."""

    EMPTY = 0
    KING = 1
    PAWN = 2
    KNIGHT = 3
    BISHOP = 5
    ROOK = 6
    QUEEN = 7

    WHITE = 8
    BLACK = 16
    INVALID = 32

    TYPE_MASK = 0b000111
    COLOUR_MASK = 0b011000
    ERROR_MASK = 0b100000

    @staticmethod
    def move_sets() -> Dict[int, Any]:
        """Map in a dictionary all the functions for the pieces.

        Returns
        -------
        dict
            Return all the functions for each piece.
        """
        return {Piece.KING: Piece.king_moveset,
                Piece.PAWN: Piece.pawn_moveset,
                Piece.BISHOP: Piece.bishop_moveset,
                Piece.KNIGHT: Piece.knight_moveset,
                Piece.ROOK: Piece.rook_moveset,
                Piece.QUEEN: Piece.queen_moveset,
                Piece.PAWN: Piece.pawn_moveset}

    # def __init__(self, piece_code):
    #     if piece_code <= 0:
    #         raise ValueError(f"Invalid piece_code: {piece_code}")

    #     self.piece_code = piece_code
    #     self.moveset = self.__find_correct_moveset()

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
    def get_colour(piece_code: int) -> int:
        """Filter the piece_code and find the piece colour.

        Parameters
        ----------
        piece_code : uint8
            A binary way to represent our pieces

        Returns
        -------
        int
            This will return only the colour part of the binary num.
        """
        return piece_code & Piece.COLOUR_MASK

    @staticmethod
    def get_colour_and_type(piece_code: int):
        """Get both the colour and the type of the piece.

        Parameters
        ----------
        piece_code : uint8
            A binary way to represent our pieces.

        Returns
        -------
        tuple
            A tuple with both the colour and the type of the piece.
        """
        return (Piece.get_colour(piece_code), Piece.get_type(piece_code))

    @staticmethod
    def get_img_for_piece(piece_code: int, imgs_path: str) -> str:
        """Find the correct img for a piece.

        Parameters
        ----------
        piece_code : uint8
            A way we represent our pieces.
        imgs_path : str
            The path to the images folder.

        Returns
        -------
        str
            The path of the piece img.
        """
        path = f"{imgs_path}/"

        colour, p_type = Piece.get_colour_and_type(piece_code)

        if colour == Piece.WHITE:
            path += 'w'
        elif colour == Piece.BLACK:
            path += 'b'

        if p_type == Piece.KING:
            path += 'k'
        elif p_type == Piece.PAWN:
            path += 'p'
        elif p_type == Piece.KNIGHT:
            path += 'n'
        elif p_type == Piece.BISHOP:
            path += 'b'
        elif p_type == Piece.ROOK:
            path += 'r'
        elif p_type == Piece.QUEEN:
            path += 'q'

        return f"{path}.png"

    @staticmethod
    def is_our_teams_turn(piece_code: int, is_white_turn: bool) -> bool:
        """Return true if given a piece its his team turn.

        Parameters
        ----------
        piece_code : uint8
            A binary way to represent our pieces.
        is_white_turn : bool
            Whether or not is white turns to play.

        Returns
        -------
        bool
            Show if its the given's piece team turn to play.
        """
        piece_colour = Piece.get_colour(piece_code)
        if piece_colour == Piece.WHITE and is_white_turn:
            return True
        elif piece_colour == Piece.BLACK and not is_white_turn:
            return True
        return False

    @staticmethod
    def is_white(piece_code: int):
        """Find if the piece is white or not."""
        return True if Piece.get_colour(piece_code) == Piece.WHITE else False

    @staticmethod
    def find_piece_from_symbol(symbol: str) -> int:
        """Find the piece from a given symbol.

        Parameters
        ----------
        symbol : str
            The given symbol.

        Returns
        -------
        int
            The corrisponding piece code.

        Raises
        ------
        ValueError
            In case the given symbol is invalid.
        """
        if symbol == 'k':
            return Piece.KING
        elif symbol == 'p':
            return Piece.PAWN
        elif symbol == 'n':
            return Piece.KNIGHT
        elif symbol == 'b':
            return Piece.BISHOP
        elif symbol == 'r':
            return Piece.ROOK
        elif symbol == 'q':
            return Piece.QUEEN
        else:
            raise ValueError(f"Wrong symbol input to find a piece: {symbol}")

    @staticmethod
    def find_symbol_for_piece(piece_code: int) -> str:
        """Find the correct symbol for a piece.

        Parameters
        ----------
        piece_code : uint8
            A binary way to represent our pieces

        Returns
        -------
        str
            The corresponding symbol for the piece.
        """
        symbol = ''
        colour, p_type = Piece.get_colour_and_type(piece_code)

        if p_type == Piece.EMPTY:
            return ' '
        if p_type == Piece.KING:
            symbol = 'k'
        elif p_type == Piece.PAWN:
            symbol = 'p'
        elif p_type == Piece.KNIGHT:
            symbol = 'n'
        elif p_type == Piece.BISHOP:
            symbol = 'b'
        elif p_type == Piece.ROOK:
            symbol = 'r'
        elif p_type == Piece.QUEEN:
            symbol = 'q'

        if colour == Piece.WHITE:
            return symbol.upper()
        else:
            return symbol

    @staticmethod
    def get_moveset(start_tile, piece_code: int) -> Set[int]:
        """Find the correct moveset for a piece.

        Parameters
        ----------
        piece_code : uint8
            A binary way to represent our pieces
        start_tile : int
            The starting tile of the piece

        Returns
        -------
        Set[int]
            Returns all the possible tiles
            that the specified piece can land.
        """
        p_type = Piece.get_type(piece_code)
        if p_type == Piece.KING:
            return Piece.king_moveset(start_tile)
        elif p_type == Piece.PAWN:
            return Piece.pawn_moveset(start_tile, piece_code)
        elif p_type == Piece.KNIGHT:
            return Piece.knight_moveset(start_tile)
        elif p_type == Piece.BISHOP:
            return Piece.bishop_moveset(start_tile, piece_code)
        elif p_type == Piece.ROOK:
            return Piece.rook_moveset(start_tile, piece_code)
        elif p_type == Piece.QUEEN:
            return Piece.queen_moveset(start_tile, piece_code)

    @staticmethod
    def queen_moveset(pos: int):
        """Generate queen moves based on the position."""
        pass

    @staticmethod
    def rook_moveset(pos: int):
        """Generate rook moves based on the position."""
        # return {pos - 1, pos + 1, }
        pass

    @staticmethod
    def bishop_moveset(pos: int):
        """Generate bishop moves based on the position."""
        pass

    @staticmethod
    def knight_moveset(pos: int) -> Set[int]:
        """Generate knight moves based on the position."""
        return {pos - 8, pos + 8, pos - 12, pos + 12, pos - 19, pos + 19, pos - 21, pos + 21}

    @staticmethod
    def pawn_moveset(pos: int, piece_code: int) -> Set[int]:
        """Generate pawn moves based on the position."""
        if Piece.is_white(piece_code):
            moves = {pos - 10, pos - 11, pos - 12}
            if 80 <= pos < 90:
                moves.add(pos - 20)
        else:
            moves = {pos + 10, pos + 11, pos + 12}
            if 30 <= pos < 40:
                moves.add(pos + 20)
        return moves

    @staticmethod
    def king_moveset(pos: int) -> Set[int]:
        """Generate king moves based on the position."""
        return {pos - 1, pos + 1, pos - 11, pos + 11, pos - 10, pos + 10, pos - 9, pos + 9}
