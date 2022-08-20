"""Board module contains all the classes and methods which are needed for a chessboard to be functional."""
from typing import Dict, List, Tuple, Literal, Union, Any
from .board_utils import BoardUtils
from .fen import Fen
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

        self.colour_to_move: Literal[Piece.WHITE, Piece.BLACK]
        self.castling_rights: Dict[Tuple[int, int], Tuple[int, int]]
        self.en_passant_coords: Union[Tuple[int, int], str]
        # This assign does nothing here its just for readability.
        (
            pcs_and_coords,
            self.colour_to_move,
            self.castling_rights,
            self.en_passant_coords,
        ) = Fen.translate_to_state(fen)

        self.state, pieces = self.setup_board_state_and_pieces(pcs_and_coords)

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
        self.correct_format_print()

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
        """Remove a piece from the board."""
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

    def setup_board_state_and_pieces(self, pc_and_coords: Tuple[int, Tuple[int, int]]) -> Tuple[BoardStateList, List[Piece]]:
        """Do the setup for the state of the board.

        Returns
        -------
        Tuple[BoardStateList, List[Piece]]
            A tuple where the first elements is:
            A custom object which is the same as a list with
            the exception that is made to check if the indexes
            are in bound of the board.

            And the second one is:
            A list with all the Pieces objects that were created.
        """
        state = BoardStateList([[Piece.EMPTY for _ in range(8)] for _ in range(8)])
        pieces: List[Piece] = []
        for pc, coords in pc_and_coords:
            state[coords] = pc
            pieces.append(Board.make_piece(pc, coords))
        return state, pieces

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
            _col = BoardUtils.get_number_for_col(col)

        pieces = self.w_pieces if colour == Piece.WHITE else self.b_pieces

        for index in pieces[piece_code]:
            # Des ama to index einai ths idias sthlhs h shras
            # me to row/col pou exeis
            c = index % 8
            r = index - c
            if c == _col or r != -1:
                return index
        return -1

    def get_fen(self) -> str:
        """Get the fen for the board."""
        self.fen = Fen.create_fen(self.state, self.colour_to_move, self.castling_rights, self.en_passant_coords)
        return self.fen

    def __str__(self):
        """Print the board state."""
        print("\n      0     1     2     3     4     5     6     7")
        for row in range(8):
            print(f"\n{row}", end="   ")
            for col in range(8):
                piece_code = self.state[row, col]
                print(f"[ {Piece.get_symbol(piece_code)} ]", end=" ")
        print(f"\n{self.get_fen()}")
        return " "

    def correct_format_print(self):
        """Print the board state in correct format."""
        for row in range(8, 0, -1):
            print(f"\n{row}", end="   ")
            for col in range(8, 0, -1):
                piece_code = self.state[8 - row, 8 - col]
                print(f"[ {Piece.get_symbol(piece_code)} ]", end=" ")
        print("\n\n      a     b     c     d     e     f     g     h\n\n")
        print(f"{self.get_fen()}\n\n")
        return " "
