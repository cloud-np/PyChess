"""Module for FEN notation."""
import numpy as np
from typing import Dict, List, Literal, Optional, Tuple
from .board_utils import BoardUtils
from chess.pieces.piece import Piece


class Fen:
    """A class for representing a fen string."""

    @staticmethod
    def create_fen(
        state,
        color_to_move: Literal[256, 512],
        caslting_rights: Optional[Dict[int, List[bool]]] = None,
        en_passant: Optional[Tuple[int, int]] = None,
        half_move_clock: int = 0,
        fullmove_number: int = 1,
    ) -> str:
        """Given the board state it produces the fen string."""
        state_f: str = Fen.__get_state_fen(state)
        # Remove the symbol '/'
        # fen = fen[:-1] + " " + self.get_castling_fen() + " " + self.get_en_passant_fen() + " " + str(self.half_move_clock) + " " + str(self.full_move_number)
        colour_f: str = " w " if color_to_move == Piece.WHITE else " b "
        cast_f: str = Fen.__get_castling_fen(caslting_rights) if caslting_rights is not None else "-"
        en_passant_fen: str = Fen.__get_en_passant_fen(en_passant)
        return f"{state_f}{colour_f}{cast_f} {en_passant_fen} {half_move_clock} {fullmove_number}"

    @staticmethod
    def __get_en_passant_fen(en_passant: Optional[Tuple[int, int]]) -> str:
        """Get the en passant fen."""
        return "-" if en_passant is None else BoardUtils.get_col_for_number(en_passant[1]) + str(8 - en_passant[0])

    @staticmethod
    def get_color_to_move(fen: str) -> Literal[256, 512]:
        """Get the en passant fen."""
        _, colour_to_move_fen, rest_of_fen = fen.split()
        return Piece.WHITE if colour_to_move_fen == "w" else Piece.BLACK

    @staticmethod
    def __get_castling_fen(castle_rights: Optional[Dict[int, List[bool]]]) -> str:
        if castle_rights is None:
            raise Exception("Castling rights not found")

        ws, bs = castle_rights.values()
        castle_fen: str = "" + ("K" if ws[1] else "")
        castle_fen += "Q" if ws[0] else ""
        castle_fen += "k" if bs[1] else ""
        castle_fen += "q" if bs[0] else ""
        return castle_fen if castle_fen != "" else "-"

    @staticmethod
    def __get_state_fen(state) -> str:
        fen: str = ""
        pos: int = 0
        for row in state:
            for piece in row:
                ptype = Piece.get_type(piece)
                colour = Piece.get_color(piece)
                if ptype == Piece.EMPTY:
                    pos += 1
                elif pos > 0:
                    fen += str(pos)
                    pos = 0

                if ptype == Piece.PAWN:
                    fen += "P" if colour == Piece.WHITE else "p"
                elif ptype == Piece.BISHOP:
                    fen += "B" if colour == Piece.WHITE else "b"
                elif ptype == Piece.KNIGHT:
                    fen += "N" if colour == Piece.WHITE else "n"
                elif ptype == Piece.ROOK:
                    fen += "R" if colour == Piece.WHITE else "r"
                elif ptype == Piece.KING:
                    fen += "K" if colour == Piece.WHITE else "k"
                elif ptype == Piece.QUEEN:
                    fen += "Q" if colour == Piece.WHITE else "q"

            if pos > 0:
                fen += str(pos)
                pos = 0
            fen += "/"
        return fen[:-1]

    @staticmethod
    def make_state_and_pieces(state_fen: str):
        pieces = []
        pos: int = 0
        pawns_count: int = 0
        knights_count: int = 0
        bishops_count: int = 0
        rooks_count: int = 0

        piece_pos = {0: Piece.LEFT_PIECE, 1: Piece.RIGHT_PIECE}
        # Parse the pieces and the tiles
        for ch in state_fen:
            # Needs a regex to check if the fen is valid
            if pos > 63:
                raise ValueError(f"Exited board boundries: {pos}")
            if ch in "12345678":
                pos += int(ch)
                continue
            piece = 0
            piece |= Piece.WHITE if ch.isupper() else Piece.BLACK
            chl = ch.lower()
            if chl == "k":
                piece |= Piece.KING
            elif chl == "p":
                piece |= Piece.PAWN
                piece |= {0: Piece.A_PAWN, 1: Piece.B_PAWN, 2: Piece.C_PAWN, 3: Piece.D_PAWN,
                               4: Piece.E_PAWN, 5: Piece.F_PAWN, 6: Piece.G_PAWN, 7: Piece.H_PAWN}[pawns_count]
                pawns_count += 1
                if pawns_count == 8:
                    pawns_count = 0
            elif chl == "n":
                piece |= Piece.KNIGHT
                piece |= piece_pos[knights_count]
                knights_count += 1
                if knights_count == 2:
                    knights_count = 0
            elif chl == "b":
                piece |= Piece.BISHOP
                piece |= piece_pos[bishops_count]
                bishops_count += 1
                if bishops_count == 2:
                    bishops_count = 0
            elif chl == "r":
                piece |= Piece.ROOK
                piece |= piece_pos[rooks_count]
                rooks_count += 1
                if rooks_count == 2:
                    rooks_count = 0
            elif chl == "q":
                piece |= Piece.QUEEN
            elif chl == "/":
                continue
            elif chl == " ":
                break
            # TODO Should check with a regex.
            else:
                raise ValueError(f"Unkown symbol in fen: {chl}")
            row = pos // 8
            col = pos - row * 8
            pieces.append((piece, (row, col)))
            pos += 1
        return pieces

    @staticmethod
    def create_castling_info(castling_fen: str) -> Dict[int, List[bool]]:
        # Parse castling positions
        castling = {
            Piece.WHITE: [False, False],
            Piece.BLACK: [False, False],
        }
        for ch in castling_fen:
            if ch == "-":
                break
            elif ch == "K":
                # King side == Right side
                castling[Piece.WHITE][1] = True
            elif ch == "Q":
                # Queen side == Left side
                castling[Piece.WHITE][0] = True
            elif ch == "k":
                castling[Piece.BLACK][0] = True
            elif ch == "q":
                castling[Piece.BLACK][1] = True
        return castling

    @staticmethod
    def create_en_passant_coords(en_passant_fen: str) -> Optional[Tuple[int, int]]:
        """Create the en passant coords based on the given en_passant_fen.

        For example if en_passant_fen is "e3" then the en passant coords are [4, 3].

        Parameters
        ----------
        en_passant_fen : str
            Representation of the en passant coords.

        Returns
        -------
        Optional[Tuple[int, int]]
            Either None because there is no en passant or the en passant coords.
        """
        if en_passant_fen == "-":
            return None
        return BoardUtils.get_number_for_col(en_passant_fen[0]), int(en_passant_fen[1])

    @staticmethod
    def translate_to_state(fen: str):
        """Based on the given fen.

        Parameters
        ----------
        fen : str
            A way to represent a chess board state.

        Returns
        -------
        pieces : List[Piece]
            The pieces on the board.

        Raises
        ------
        ValueError
            In case there is a wrong symbol in the fen.
        """
        try:
            (
                state_fen,
                colour_to_move_fen,
                castling_fen,
                en_passant_fen,
                halfmove_fen,
                fullmove_fen,
            ) = fen.split()
        except ValueError:
            raise ValueError("Wrong fen format") from None

        pieces: List[Tuple[np.uint32, Tuple[int, int]]] = Fen.make_state_and_pieces(state_fen)
        colour_to_move = (
            Piece.WHITE if colour_to_move_fen == "w" else Piece.BLACK
        )
        castling = Fen.create_castling_info(castling_fen)
        en_passant: Optional[Tuple[int, int]] = Fen.create_en_passant_coords(en_passant_fen)

        return pieces, colour_to_move, castling, en_passant, int(halfmove_fen), int(fullmove_fen)
