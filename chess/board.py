"""board module contains all the classes and methods which are needed for a chessboard to be functional."""
import numpy as np
from typing import Callable, Any
# import numpy.typing as npt
from typing import Dict, List
from chess.pieces.piece import Piece
from chess.pieces.bishop import Bishop
from chess.pieces.queen import Queen
from chess.pieces.rook import Rook
from chess.pieces.king import King
from chess.pieces.knight import Knight
from chess.pieces.pawn import Pawn

BOARD_OFFSET = 21


class BoardStateList(list):
    """This class helps with keeping the indexes in bound."""

    def __init__(self, *args, **kwargs):
        """Init."""
        super(BoardStateList, self).__init__(args[0])

    def __setitem__(self, indexes, o):
        """Made to handle tuples are indexes."""
        self[indexes[0]][indexes[1]] = o

    def __getitem__(self, indexes):
        """Handle out of bounds board indexes."""
        if type(indexes) is int:
            return super().__getitem__(indexes)
        for i in indexes:
            if not 0 <= i <= 7:
                return Piece.INVALID
        return super().__getitem__(indexes[0]).__getitem__(indexes[1])


class Board:
    """The way we represent our Board is a Piece centric way.

    Description:
    Meaing a tile on the board has some properties and holds
    info about the piece that either occupies it there or not.
    """

    def __init__(self, fen: str):
        """Construct all the necessary attributes for the board object.

        Parameters
        ----------
        fen : str
            A way to represent the board state.
        """
        self.fen: str = fen
        self.state: BoardStateList = self.setup_board_state()
        self.get_state_from_fen(fen)  # This assign does nothing here its just for readability.

        # Get White Lists
        self.w_pieces = self.organize_pieces(is_whites=True)
        self.w_king, self.w_pawn, self.w_bishop, self.w_knight, self.w_rook, self.w_queen = self.w_pieces.values()

        # Get Black Lists
        self.b_pieces = self.organize_pieces(is_whites=False)
        self.b_king, self.b_pawn, self.b_bishop, self.b_knight, self.b_rook, self.b_queen = self.b_pieces.values()
        print(self)

    def get_piece_obj(self, coords: tuple, piece_code: int):
        """Get the piece obj.

        Find the piece obj that corrisponds to
        coords and the piece code that was given.

        Parameters
        ----------
        coords : tuple
            The coords of the piece obj.
        piece_code : int
            The piece code of the piece.

        Returns
        -------
        Piece
            The piece that was found.

        Raises
        ------
        Exception
            [description]
        """
        if piece_code == Piece.EMPTY:
            return None

        color = Piece.get_colour(piece_code)
        if color == Piece.WHITE:
            pieces = [piece for piece in self.w_pieces[piece_code] if piece.coords == coords and piece.piece_code == piece_code]
        else:
            pieces = [piece for piece in self.b_pieces[piece_code] if piece.coords == coords and piece.piece_code == piece_code]

        if len(pieces) > 1 or not pieces:
            raise Exception("Found the same piece obj twice!")
        print(pieces)
        return pieces[0]

    def organize_pieces(self, is_whites: bool) -> Dict[int, List[int]]:
        """Given a team color it will return that team's pieces.

        Parameters
        ----------
        is_whites : bool
            Whether or not white pieces were asked to be returned.

        Returns
        -------
        Dict[int, List[int]]
            A map of the existing (white or black) pieces
            separated in lists based on their type.
        """
        color = Piece.WHITE if is_whites else Piece.BLACK
        pieces: Dict[int, List[int]] = {Piece.KING | color: list(),
                                        Piece.PAWN | color: list(),
                                        Piece.BISHOP | color: list(),
                                        Piece.KNIGHT | color: list(),
                                        Piece.ROOK | color: list(),
                                        Piece.QUEEN | color: list()}

        for i in range(8):
            for j in range(8):
                piece = self.state[i, j]
                if isinstance(piece, Piece) and piece.color == color:
                    pieces[piece.piece_code].append(piece)
        return pieces

    @staticmethod
    def make_piece(piece_code: int, coords: tuple) -> Any:
        """Create a piece object based on the given piece code.

        Parameters
        ----------
        pc : int
            Piece code that describes the piece type and color.
        """
        Constructor = Board.piece_classes(piece_code)
        return Constructor(piece_code, coords)

    @staticmethod
    def piece_classes(piece_code: int) -> Callable:
        """Map in a dictionary all the functions for the pieces.

        Returns
        -------
        dict
            Return all the functions for each piece.
        """
        ptype = Piece.get_type(piece_code)
        return {Piece.KING: King,
                Piece.PAWN: Pawn,
                Piece.BISHOP: Bishop,
                Piece.KNIGHT: Knight,
                Piece.ROOK: Rook,
                Piece.QUEEN: Queen}[ptype]

    def setup_board_state(self) -> np.ndarray:
        """Do the setup for the state of the board."""
        return BoardStateList([[Piece.EMPTY for i in range(8)] for j in range(8)])

    def get_state_from_fen(self, fen: str) -> BoardStateList:
        """Given a fen it will return the board state.

        Parameters
        ----------
        fen : str
            A way to represent a chess board state.

        Returns
        -------
        BoardStateList
            A custom object which is the same as a list with
            the exception that is made to check if the indexes
            are in bound of the board.

        Raises
        ------
        ValueError
            In case there is a wrong symbol in the fen.
        """
        # np.full((120), 32, dtype="uint8")
        # Adding the error bits should be done when creating the board obj.
        # The pos could start from 21 and stop at 98
        pos = 0
        for ch in fen:
            if pos > 63:
                raise ValueError(f"Exited board boundries: {pos}")

            # Skip that many tiles.
            if ch in "12345678":
                pos += int(ch)
                continue

            # Find the color of the piece.
            piece_code = 0b0
            piece_code |= Piece.WHITE if ch.isupper() else Piece.BLACK
            # Find the type of the piece.
            chl = ch.lower()
            if chl == 'k':
                piece_code |= Piece.KING
            elif chl == 'p':
                piece_code |= Piece.PAWN
            elif chl == 'n':
                piece_code |= Piece.KNIGHT
            elif chl == 'b':
                piece_code |= Piece.BISHOP
            elif chl == 'r':
                piece_code |= Piece.ROOK
            elif chl == 'q':
                piece_code |= Piece.QUEEN
            elif chl == '/':
                continue
            else:
                raise ValueError(f"Unkown symbol in fen: {chl}")

            # Occupy the pos.
            row = pos // 8
            col = pos - row * 8

            self.state[row, col] = Board.make_piece(piece_code, (row, col))
            pos += 1

        return self.state

    # FIXME Needs refactoring because of the new board representation.
    def get_tile_from_piece(self, piece_code: int, row: int = -1, col: str = '') -> int:
        colour = Piece.get_colour(piece_code)

        _col = None
        if row != -1:
            pass
            # inv_row = (8 - row) * 8
        elif col != '':
            _col = Board.get_number_for_col(col)

        pieces = self.w_pieces if colour == Piece.WHITE else self.b_pieces

        for index in pieces[piece_code]:
            # Des ama to index einai ths idias sthlhs h shras
            # me to row/col pou exeis
            c = index % 8
            r = index - c
            if c == _col or r != -1:
                return index
        return -1

    # FIXME Needs refactoring because of the new board representation.
    # def find_tile_from_piece(self, piece_code: int, row: int = -1, col: str = ''):
    #     colour, type = Piece.get_colour_and_type(piece_code)

    #     if row != -1:
    #         inv_row = (8 - row) * 8
    #         for i, index in enumerate(range(inv_row, inv_row + 8)):
    #             pc = self.state[Board.normalize_index(index)]
    #             if (Piece.get_colour_and_type(pc)) == (colour, type):
    #                 return inv_row + i
    #     elif col != '':
    #         offset = Board.get_number_for_col(col)
    #         for i, pc in enumerate(self.state[::8 + offset]):
    #             if (Piece.get_colour_and_type(pc)) == (colour, type):
    #                 return (i * 8) + offset

    #     for i, pc in enumerate(self.state):
    #         if (Piece.get_colour_and_type(pc)) == (colour, type):
    #             return i

    #     return -1

    # FIXME Needs refactoring because of the new board representation.
    @staticmethod
    def find_tile_from_str(row: str, col: str) -> int:
        """Find the tile given the row and col names."""
        _col: int = Board.get_number_for_col(col)
        _row: int = (8 - int(row))
        return (_row * 8) + _col

    @staticmethod
    def get_number_for_col(col: str) -> int:
        """Get the corrisponding number based on the given col name."""
        if col == 'a':
            return 0
        elif col == 'b':
            return 1
        elif col == 'c':
            return 2
        elif col == 'd':
            return 3
        elif col == 'e':
            return 4
        elif col == 'f':
            return 5
        elif col == 'g':
            return 6
        elif col == 'h':
            return 7
        else:
            raise ValueError(f"Wrong value for collumn: {col}")

    def __str__(self):
        """Print the board state."""
        print('\n      0     1     2     3     4     5     6     7')
        # x = 0
        # print(x, end='   ')
        for row in range(8):
            print()
            print(row, end='   ')
            for col in range(8):
                piece = self.state[row, col]
                print(f"[ {' ' if not isinstance(piece, Piece) else piece.symbol} ]", end=' ')
        return ' '
