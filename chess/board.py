"""board module contains all the classes and methods which are needed for a chessboard to be functional."""
import numpy as np
from chess.piece import Piece


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
        self.state = self.get_state_from_fen(fen)

    def get_state_from_fen(self, fen):
        state = np.zeros((self.size), dtype="int")
        pos = 0
        for ch in fen:
            # Skip that many tiles.
            if ch in "12345678":
                pos += int(ch) - 1  # -1 because we count from 0
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

            if piece_code < 0:
                raise ValueError(f"Incorrect piece_code value: {piece_code}")
            else:
                # Initialize the piece.
                state[pos] = piece_code
                pos += 1

        return state

    # def show_white_pieces_pos():
    #     for
    # def __str__(self):
