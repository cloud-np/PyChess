"""board module contains all the classes and methods which are needed for a chessboard to be functional."""
import numpy as np
from chess.piece import Piece

BOARD_OFFSET = 21


class Board:
    """The way we represent our Board is a Piece centric way.

    Description:
    Meaing a tile on the board has some properties and holds
    info about the piece that either occupies it there or not.
    """

    def __init__(self, fen, size):
        """Construct all the necessary attributes for the board object.

        Parameters
        ----------
        fen : str
            A way to represent the board state.
        """
        self.fen: str = fen
        self.size = size
        self.setup_board_state()
        self.state = self.get_state_from_fen(fen)  # This assign does nothing here its just for readability.
        self.w_pieces = self.get_pieces(whites=True)
        self.w_king, self.w_pawn, self.w_bishop, self.w_knight, self.w_rook, self.w_queen = self.w_pieces.values()
        self.b_pieces = self.get_pieces(whites=False)
        self.pieces_movesets = Piece.move_sets()
        self.b_king, self.b_pawn, self.b_bishop, self.b_knight, self.b_rook, self.b_queen = self.b_pieces.values()
        print(self)

    @staticmethod
    def normalize_index(index):
        """Calculate the normilized version of the index e.g: 0 -> 21, 16 -> 41."""
        row = index // 8
        return (index + 21) + (row * 2)

    def get_pieces(self, whites):
        colour = Piece.WHITE if whites else Piece.BLACK
        pieces = {Piece.KING | colour: list(),
                  Piece.PAWN | colour: list(),
                  Piece.BISHOP | colour: list(),
                  Piece.KNIGHT | colour: list(),
                  Piece.ROOK | colour: list(),
                  Piece.QUEEN | colour: list()}

        for i, pc in enumerate(self.state):
            if pc != Piece.EMPTY and Piece.get_colour(pc) == colour:
                pieces[pc].append(i)
        return pieces

    def setup_board_state(self):
        """Do the setup by making boundries (0-21 98-120) in the board and the board itself."""
        self.state = np.zeros((self.size), dtype="uint8")
        for i in range(0, 21):
            self.state[i] |= Piece.INVALID
        for i in range(98, len(self.state)):
            self.state[i] |= Piece.INVALID
        return self.state

    def get_state_from_fen(self, fen):
        """Given a fen it will return the board state.

        Parameters
        ----------
        fen : str
            A way to represent a chess board state.

        Returns
        -------
        numpy.array(dtype="uint8")
            A numpy array of unsigned 8 bit ints.

        Raises
        ------
        ValueError
            In case there is a wrong symbol in the fen.
        """
        # np.full((120), 32, dtype="uint8")
        # Adding the error bits should be done when creating the board obj.
        # The pos could start from 21 and stop at 98
        pos = 21
        for ch in fen:
            if pos > 98:
                raise ValueError(f"Exited board boundries: {pos}")
            # Skip the invalid positions.
            elif (pos + 1) % 10 == 0:
                pos += 2
                continue
            # Skip that many tiles.
            if ch in "12345678":
                pos += int(ch)
                continue

            # Find the color of the piece.
            piece_code = 0b0
            if ch.isupper():
                piece_code |= Piece.WHITE
            else:
                piece_code |= Piece.BLACK

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
            self.state[pos] = piece_code
            pos += 1

        return self.state

    # FIXME Needs refactoring because of the new board representation.
    def get_tile_from_piece(self, piece_code, row: int = -1, col: str = ''):
        colour = Piece.get_colour(piece_code)

        if row != -1:
            pass
            # inv_row = (8 - row) * 8
        elif col != '':
            col = Board.get_number_for_col(col)

        pieces = self.w_pieces if colour == Piece.WHITE else self.b_pieces

        for index in pieces[piece_code]:
            # Des ama to index einai ths idias sthlhs h shras
            # me to row/col pou exeis
            c = index % 8
            r = index - c
            if c == col:
                return index
            elif r != -1:
                return index

    # FIXME Needs refactoring because of the new board representation.
    def find_tile_from_piece(self, piece_code, row: int = -1, col: str = ''):
        colour, type = Piece.get_colour_and_type(piece_code)

        if row != -1:
            inv_row = (8 - row) * 8
            for i, index in enumerate(range(inv_row, inv_row + 8)):
                pc = self.state[Board.normalize_index(index)]
                if (Piece.get_colour_and_type(pc)) == (colour, type):
                    return inv_row + i
        elif col != '':
            offset = Board.get_number_for_col(col)
            for i, pc in enumerate(self.state[::8 + offset]):
                if (Piece.get_colour_and_type(pc)) == (colour, type):
                    return (i * 8) + offset

        for i, pc in enumerate(self.state):
            if (Piece.get_colour_and_type(pc)) == (colour, type):
                return i

        return -1

    # FIXME Needs refactoring because of the new board representation.
    @staticmethod
    def find_tile_from_str(row: str, col: str):
        col = Board.get_number_for_col(col)
        row = (8 - int(row))
        return (row * 8) + col

    @staticmethod
    def get_number_for_col(col):
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

    # FIXME Needs refactoring because of the new board representation.
    def __str__(self):
        """Print the board state."""
        x = 0
        print('\t\t\t\t     BOARD')
        print('      0     1     2     3     4     5     6     7')
        print(x, end='   ')
        i = 0
        for index in range(21, 99):
            if i % 8 == 0 and i != 0:
                x += 1
                print()
                print(x, end='   ')
                i = 0
            elif index % 10 != 0:
                print(f'[ {Piece.find_symbol_for_piece(self.state[index])} ]', end=' ')
                i += 1
        return ' '
