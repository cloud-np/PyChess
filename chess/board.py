"""board module contains all the classes and methods which are needed for a chessboard to be functional."""
import numpy as np
from typing import Any

# import numpy.typing as npt
from typing import Dict, List, Literal, Union, Tuple
from chess.pieces.piece import Piece
from chess.pieces.bishop import Bishop
from chess.pieces.queen import Queen
from chess.pieces.rook import Rook, RookCorner
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


class Fen:
    @staticmethod
    def create_fen(
        board_state: BoardStateList,
        colour_to_move: Literal[Piece.WHITE, Piece.BLACK],
        caslting: Union[Dict[List[bool], List[bool]], str] = "-",
        enpassan: Union[List[int], str] = "-",
        halfmove_clock: int = 0,
        fullmove_number: int = 1,
    ) -> str:
        """Given the board state it produces the fen string."""
        board_state_f: str = Fen.__get_board_state_fen(board_state)
        # Remove the symbol '/'
        # fen = fen[:-1] + " " + self.get_castling_fen() + " " + self.get_en_passant_fen() + " " + str(self.half_move_clock) + " " + str(self.full_move_number)
        colour_f: str = " w " if colour_to_move == Piece.WHITE else " b "
        cast_f: str = Fen.__get_castling_fen(caslting) if caslting != "-" else "-"
        return board_state_f + colour_f + cast_f

    @staticmethod
    def __get_castling_fen(castling_rights: Dict[List[bool], List[bool]]) -> str:
        castling_fen: str = ""
        # Get white and black castling sides
        ws, bs = castling_rights.values()
        castling_fen += 'K' if ws[1] else ""
        castling_fen += 'Q' if ws[0] else ""
        castling_fen += 'k' if bs[1] else ""
        castling_fen += 'q' if bs[0] else ""
        return castling_fen if castling_fen != "" else "-"

    @staticmethod
    def __get_board_state_fen(board_state: BoardStateList) -> str:
        fen: str = ""
        pos: int = 0
        for row in board_state:
            for piece_code in row:
                ptype = Piece.get_type(piece_code)
                colour = Piece.get_colour(piece_code)
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
    def create_state_and_pieces(
        state: BoardStateList, board_state_fen: str
    ) -> Tuple[BoardStateList, List[Piece]]:
        pieces: list = []
        pos: int = 0
        # Parse the pieces and the tiles.
        for ch in board_state_fen:
            # Needs a regex to check if the fen is valid
            if pos > 63:
                raise ValueError(f"Exited board boundries: {pos}")
            if ch in "12345678":
                pos += int(ch)
                continue
            piece_code = 0
            piece_code |= Piece.WHITE if ch.isupper() else Piece.BLACK
            chl = ch.lower()
            if chl == "k":
                piece_code |= Piece.KING
            elif chl == "p":
                piece_code |= Piece.PAWN
            elif chl == "n":
                piece_code |= Piece.KNIGHT
            elif chl == "b":
                piece_code |= Piece.BISHOP
            elif chl == "r":
                piece_code |= Piece.ROOK
            elif chl == "q":
                piece_code |= Piece.QUEEN
            elif chl == "/":
                continue
            elif chl == " ":
                break
            # TODO Should check with a regex.
            else:
                raise ValueError(f"Unkown symbol in fen: {chl}")
            row = pos // 8
            col = pos - row * 8
            pieces.append(Board.make_piece(piece_code, (row, col)))
            state[row, col] = piece_code
            pos += 1

        return state, pieces

    @staticmethod
    def create_castling_info(castling_fen: str):
        # Parse castling positions
        castling: Dict[List[bool], List[bool]] = {
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
    def translate_to_state(state: BoardStateList, fen: str):
        """Based on the given fen

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
        colour_pos: int = 0

        try:
            (
                board_state_fen,
                colour_to_move_fen,
                castling_fen,
                halfmove_fen,
                fullmove_fen,
            ) = fen.split()
        except ValueError:
            raise ValueError("Wrong fen format") from None

        state, pieces = Fen.create_state_and_pieces(state, board_state_fen)
        colour_to_move: Literal[Piece.WHITE, Piece.BLACK] = (
            Piece.WHITE if colour_to_move_fen == "w" else Piece.BLACK
        )
        castling: Dict[List[bool], List[bool]] = Fen.create_castling_info(castling_fen)

        # Parse enpassan positions
        # halfmove_pos: int = 0
        # for i, ch in enumerate(fen[enpassan_pos + 1:]):
        #     if ch == '-':
        #         halfmove_pos = i
        #         break
        #     elif ch in 'abcdefgh':
        #         print('h')

        return state, pieces, colour_to_move, castling


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
        self.starting_fen: str = fen
        self.state: BoardStateList = self.setup_board_state()

        # This assign does nothing here its just for readability.
        (
            self.state,
            pieces,
            self.colour_to_move,
            self.castling_rights,
        ) = Fen.translate_to_state(self.state, fen)

        # Get White Lists
        self.w_pieces = self.organize_pieces(pieces, is_whites=True)

        # Get Black Lists
        self.b_pieces = self.organize_pieces(pieces, is_whites=False)

        self.all_pieces = {Piece.WHITE: self.w_pieces, Piece.BLACK: self.b_pieces}

        # Kings
        self.kings = {
            Piece.WHITE: self.w_pieces[Piece.KING | Piece.WHITE][0],
            Piece.BLACK: self.b_pieces[Piece.KING | Piece.BLACK][0],
        }

        self.dead_pieces: List[Piece] = []
        # print(self)
        self.correct_format_print()

    @staticmethod
    def swap_colours(colour: int) -> Literal[Piece.WHITE, Piece.BLACK]:
        return Piece.WHITE if colour == Piece.BLACK else Piece.BLACK

    def try_updating_castling(self, moving_piece):
        """Remove castling privileges depending the moving piece."""

        # Only for the first time the King is moving.
        if moving_piece.times_moved == 0 and isinstance(moving_piece, King):
            moving_piece.r_castle["is_valid"] = False
            moving_piece.l_castle["is_valid"] = False
            self.castling_rights[moving_piece.color] = [False, False]

        if isinstance(moving_piece, Rook):
            # Check if the rook moved was in the Right half of the board.
            if moving_piece.rook_corner in (
                RookCorner.BOTTOM_RIGHT,
                RookCorner.TOP_RIGHT,
            ):
                self.kings[moving_piece.color].r_castle["is_valid"] = False
                self.castling_rights[moving_piece.color][1] = False

            # Check if the rook moved was in the Left half of the board.
            if moving_piece.rook_corner in (
                RookCorner.BOTTOM_LEFT,
                RookCorner.TOP_LEFT,
            ):
                self.kings[moving_piece.color].l_castle["is_valid"] = False
                self.castling_rights[moving_piece.color][0] = False

    def transform_pawn_to(self, moving_pawn: Piece, piece_code: int) -> None:
        """Transform to a desired Piece.

        Transform to a desired Piece and removed the original Pawn from the list.

        Parameters
        ----------
        piece_code : int
            Piece code that describes the piece type and color.

        Raises
        ------
        Exception
            [description]
        """

        # if piece_code

        # Create the Piece that the pawn will transform too
        PieceConstructor = Board.piece_classes(piece_code)
        transformed_piece = PieceConstructor(piece_code, moving_pawn.coords)
        transformed_piece.times_moved = moving_pawn.times_moved

        # Update Pieces
        if moving_pawn.color == Piece.WHITE:
            self.w_pieces[moving_pawn.piece_code].remove(moving_pawn)
            self.w_pieces[transformed_piece.piece_code].append(transformed_piece)
        else:
            self.b_pieces[moving_pawn.piece_code].remove(moving_pawn)
            self.b_pieces[transformed_piece.piece_code].append(transformed_piece)

    def kill_piece(self, dead_piece: Piece):
        self.dead_pieces.append(dead_piece)
        dead_piece.is_dead = True

        # Remove the dead piece from the piece lists
        if dead_piece.color == Piece.WHITE:
            self.w_pieces[dead_piece.piece_code].remove(dead_piece)
        else:
            self.b_pieces[dead_piece.piece_code].remove(dead_piece)

    def simulated_board_state(self):
        """Given a board state it will return a 'simulated' board state.

        This will allows us to affect the board state without actually changing it.
        """
        # Slower but more compact
        return BoardStateList([[self.state[j, i] for i in range(8)] for j in range(8)])

    def get_piece(self, coords: tuple) -> Piece:
        """Given a coords it will return the piece that is there."""
        piece_code = self.state[coords]
        return self.get_piece_obj(coords, piece_code)

    def get_piece_obj(self, coords: tuple, piece_code: int):
        # sourcery skip: raise-specific-error
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
        """
        if piece_code == Piece.EMPTY:
            return None

        color = Piece.get_colour(piece_code)
        if color == Piece.WHITE:
            pieces = [
                piece
                for piece in self.w_pieces[piece_code]
                if piece.coords == coords and piece.piece_code == piece_code
            ]
        else:
            pieces = [
                piece
                for piece in self.b_pieces[piece_code]
                if piece.coords == coords and piece.piece_code == piece_code
            ]

        if len(pieces) > 1 or not pieces:
            raise Exception("Found the same piece obj twice!")
        return pieces[0]

    def organize_pieces(
        self, all_pieces: List[Piece], is_whites: bool
    ) -> Dict[int, List[int]]:
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
        pieces: Dict[int, List[int]] = {
            Piece.KING | color: [],
            Piece.PAWN | color: [],
            Piece.BISHOP | color: [],
            Piece.KNIGHT | color: [],
            Piece.ROOK | color: [],
            Piece.QUEEN | color: [],
        }

        for piece in all_pieces:
            if isinstance(piece, Piece) and piece.color == color:
                pieces[piece.piece_code].append(piece)
        return pieces

    @staticmethod
    def make_piece(piece_code: int, coords: tuple) -> Any:
        """Create a piece object based on the given piece code.

        Parameters
        ----------
        piece_code : int
            Piece code that describes the piece type and color.
        """
        PieceConstructor = Board.piece_classes(piece_code)
        return PieceConstructor(piece_code, coords)

    @staticmethod
    def piece_classes(piece_code: int) -> dict:
        """Map in a dictionary all the functions for the pieces.

        Returns
        -------
        dict
            Return all the functions for each piece.
        """
        ptype = Piece.get_type(piece_code)
        return {
            Piece.KING: King,
            Piece.PAWN: Pawn,
            Piece.BISHOP: Bishop,
            Piece.KNIGHT: Knight,
            Piece.ROOK: Rook,
            Piece.QUEEN: Queen,
        }[ptype]

    def setup_board_state(self) -> np.ndarray:
        """Do the setup for the state of the board."""
        return BoardStateList([[Piece.EMPTY for _ in range(8)] for _ in range(8)])

    def are_coords_under_attack(self, coords_list, enemy_color):
        """Check if any of the given coords are being attacked.

        Parameters
        ----------
        coords_list : List[Tuple[int, int]]
            A list of coords to check if they are being attacked.
        enemy_color : int
            The color of the enemy pieces.
        enemies_pieces : List[Piece]
            The enemy pieces.

        Returns
        -------
        bool
            Returns true if any of the coords are being attacked.
        """
        # Check if the king is in check from the rest of the pieces
        enemy_moves = Piece.get_enemy_possible_coords(
            self.all_pieces[enemy_color], self.state
        )
        return any(tuple(coords) in enemy_moves for coords in coords_list)

    def are_coords_empty(self, coords_list):
        """Check if ALL the given coords are empty."""
        return all(self.state[coords] == Piece.EMPTY for coords in coords_list)

    # FIXME Needs refactoring because of the new board representation.
    def get_tile_from_piece(self, piece_code: int, row: int = -1, col: str = "") -> int:
        colour = Piece.get_colour(piece_code)

        _col = None
        if row != -1:
            pass
            # inv_row = (8 - row) * 8
        elif col != "":
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
    @staticmethod
    def find_tile_from_str(row: str, col: str) -> int:
        """Find the tile given the row and col names."""
        _col: int = Board.get_number_for_col(col)
        _row: int = 8 - int(row)
        return (_row * 8) + _col

    @staticmethod
    def get_number_for_col(col: str) -> int:
        """Get the corrisponding number based on the given col name."""
        if col == "a":
            return 0
        elif col == "b":
            return 1
        elif col == "c":
            return 2
        elif col == "d":
            return 3
        elif col == "e":
            return 4
        elif col == "f":
            return 5
        elif col == "g":
            return 6
        elif col == "h":
            return 7
        else:
            raise ValueError(f"Wrong value for collumn: {col}")

    def __str__(self):
        """Print the board state."""
        print("\n      0     1     2     3     4     5     6     7")
        for row in range(8):
            print(f"\n{row}", end="   ")
            for col in range(8):
                piece_code = self.state[row, col]
                print(f"[ {Piece.get_symbol(piece_code)} ]", end=" ")
        print(f"\n{Fen.create_fen(self.state, self.colour_to_move, self.castling_rights)}")
        return " "

    def correct_format_print(self):
        """Print the board state in correct format."""
        for row in range(8, 0, -1):
            print(f"\n{row}", end="   ")
            for col in range(8, 0, -1):
                piece_code = self.state[8 - row, 8 - col]
                print(f"[ {Piece.get_symbol(piece_code)} ]", end=" ")
        print("\n\n      a     b     c     d     e     f     g     h\n\n")
        print(f"{Fen.create_fen(self.state, self.colour_to_move, self.castling_rights)}\n\n")
        return " "
