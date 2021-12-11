"""Includes the base class for each Piece."""
from chess.move import MoveDirection, Move
from typing import Tuple, Set


class Piece:
    """Base class that holds info about the piece."""

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

    def __init__(self, piece_code: int, coords: tuple):
        """Init the piece.

        Parameters
        ----------
        color : int
            The color of the created piece.
        ptype : int
            The type of the piece.
        symbol : str
            The symbol that is shown when printing the piece.
        coords : tuple
            The coordinates of the piece.
        """
        self.piece_code: int = piece_code
        self.color: int = Piece.get_colour(piece_code)
        self.is_white = self.color == Piece.WHITE
        self.ptype: int = Piece.get_type(piece_code)
        self.symbol: int = Piece.get_symbol(piece_code)
        self.coords: tuple = coords

    def __eq__(self, other: 'Piece'):
        """Overload the == when it is applied on two Piece classes to check if they are equal based on their coords and piececode."""
        if not isinstance(other, Piece):
            return False
        return self.__key() == other.__key()

    def __key(self):
        return tuple(self.piece_code, *self.coords)

    def add_moves_in_direction(self, board_state, moves: Set[Tuple[int]], direction: MoveDirection) -> None:
        """Found the all moves based of the 'direction' a direction.

        Given a direction it will generate all the moves until it hits either:
        1. An invalid block.
        2. An ally Piece.
        3. An enemy Piece (which he will inclide his square).

        Parameters
        ----------
        board_state : BoardStateList
            A 2d custom matrix that holds information about all the pieces on board.
        moves : set[tuple[int]]
            The set of the valid moves based on the criteria we added above.

        direction : MoveDirection
            The direction of which we want to generate moves to.
        """
        direction_func = Move.get_direction_func(direction)
        for i in range(1, self.range_limit):
            move: tuple[int] = direction_func(self.coords, i)
            piece = board_state[move]
            if piece == Piece.EMPTY:
                moves.add(move)
            elif piece == Piece.INVALID:
                break
            elif isinstance(piece, Piece):
                if piece.color != self.color:
                    moves.add(piece.coords)
                break

    # def is_piece_and_same_color(self, o_piece) -> tuple[bool]:
    #     """Check if the given arg is an instance of Piece and then if it has the same color."""
    #     if isinstance(o_piece, Piece):
    #         if o_piece.color != self.color:
    #             return True, True
    #         return True, False
    #     return False, False

    def __hash__(self):
        """Make the obj hashable so it can be used in Sets etc."""
        return hash(self.__key())

    def __str__(self):
        """Show the piece and the coords that is on."""
        return f" {self.symbol}  coords: [{self.coords[0]}, {self.coords[1]}]"

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
        color = Piece.get_colour(piece_code)
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
        path = f"{imgs_path}/"
        color = Piece.get_colour(piece_code)
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
