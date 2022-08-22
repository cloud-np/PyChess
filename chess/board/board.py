"""Board module contains all the classes and methods which are needed for a chessboard to be functional."""
from typing import Dict, List, Tuple, Literal, Union, Optional
from .board_utils import BoardUtils
from .fen import Fen
from chess.pieces.rook import RookCorner
from chess.pieces.piece import Piece

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
        self.last_piece_moved: Optional[Piece] = None

        self.color_to_move: Literal[Piece.WHITE, Piece.BLACK]
        self.castle_rights: Dict[Tuple[int, int], Tuple[int, int]]
        self.en_passant_coords: Union[Tuple[int, int], str]
        # This assign does nothing here its just for readability.
        (
            pcs_and_coords,
            self.color_to_move,
            self.castle_rights,
            self.en_passant_coords,
        ) = Fen.translate_to_state(fen)

        self.state, pieces = self.setup_board_state_and_pieces(pcs_and_coords)

        # Get White Lists
        w_pieces = Board.organize_pieces(pieces, is_whites=True)
        # Get Black Lists
        b_pieces = Board.organize_pieces(pieces, is_whites=False)
        self.all_pieces = {Piece.WHITE: w_pieces, Piece.BLACK: b_pieces}

        # Kings
        # self.kings = {
        #     Piece.WHITE: w_pieces[Piece.KING | Piece.WHITE][0],
        #     Piece.BLACK: b_pieces[Piece.KING | Piece.BLACK][0],
        # }

        self.dead_pieces: List[int] = []
        self.correct_format_print()

    @staticmethod
    def try_update_castle_rights(castle_rights, moving_piece: int) -> None:
        """Remove castling privileges depending the moving piece."""
        # Only for the first time the King is moving.
        pcolor = Piece.get_color(moving_piece)
        ptype = Piece.get_type(moving_piece)
        if ptype == Piece.KING:
            castle_rights[pcolor] = [False, False]

        if Piece.get_type(moving_piece) == Piece.ROOK:
            # Check if the rook moved was in the Right half of the board.
            if Piece.get_the_specific_piece(moving_piece) == Piece.RIGHT_PIECE:
                castle_rights[pcolor][1] = False

            # Check if the rook moved was in the Left half of the board.
            if Piece.get_the_specific_piece(moving_piece) == Piece.LEFT_PIECE:
                castle_rights[pcolor][0] = False

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

    @staticmethod
    def simulate_board_state(board_state: BoardStateList) -> BoardStateList:
        """Given a board state it will return a 'simulated' board state.

        This will allows us to affect the board state without actually changing it.
        """
        # Slower but more compact
        return BoardStateList([[baord_state[j, i] for i in range(8)] for j in range(8)])

    @staticmethod
    def get_piece(board_state, coords: Tuple[int, int]) -> int:
        """Given a coords it will return the piece that is there."""
        return board_state[coords]

    @staticmethod
    def update_piece_board_lists(piece_code: int,):
        ...

    @staticmethod
    def get_all_color_pieces(all_pieces, color: Literal[Piece.WHITE, Piece.BLACK]) -> List[Tuple[int, Tuple[int, int]]]:
        return all_pieces[Piece.get_color(color)]

    @staticmethod
    def get_piece_coords(all_pieces, piece_code: int) -> Optional[Tuple[int, int]]:
        """Given a piece_code find the coords of the piece.

        Find the piece obj that corrisponds to
        coords and the piece code that was given.
        """
        if piece_code == Piece.EMPTY:
            return None

        pcolor = Piece.get_color(piece_code)
        ptype = Piece.get_type(piece_code)
        pieces_list = Board.get_all_color_pieces(all_pieces, pcolor)
        for p_info in pieces_list[pcolor | ptype]:
            if piece_code == p_info[0]:
                return p_info[1]

    @staticmethod
    def organize_pieces(all_pieces: List[Piece], is_whites: bool) -> Dict[int, List[int]]:
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
        color_given = Piece.WHITE if is_whites else Piece.BLACK
        pieces: Dict[int, List[int]] = {
            Piece.KING | color_given: [],
            Piece.PAWN | color_given: [],
            Piece.BISHOP | color_given: [],
            Piece.KNIGHT | color_given: [],
            Piece.ROOK | color_given: [],
            Piece.QUEEN | color_given: [],
        }

        for pc, coords in all_pieces:
            color = Piece.get_color(pc)
            ptype = Piece.get_type(pc)
            if color == color_given:
                pieces[ptype | color].append((pc, coords))
        return pieces

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
            Piece.KING: Piece.king_moves,
            Piece.PAWN: Piece.pawn_moves,
            Piece.BISHOP: Piece.bishop_moves,
            Piece.KNIGHT: Piece.knight_moves,
            Piece.ROOK: Piece.rook_moves,
            Piece.QUEEN: Piece.queen_moves,
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
            pieces.append((pc, coords))
        return state, pieces

    @staticmethod
    def are_coords_under_attack(board_state: BoardStateList, coords_list: List[Tuple[int, int]], enemy_pieces) -> bool:
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
        enemy_moves = Piece.get_enemy_possible_coords(enemy_pieces, board_state)
        return any(tuple(coords) in enemy_moves for coords in coords_list)

    @staticmethod
    def are_coords_empty(board_state: BoardStateList, coords_list: List[Tuple[int, int]]) -> bool:
        """Check if ALL the given coords are empty."""
        return all(board_state[coords] == Piece.EMPTY for coords in coords_list)

    # FIXME Needs refactoring because of the new board representation.
    def get_tile_from_piece(self, piece_code: int, row: int = -1, col: str = "") -> int:
        color = Piece.get_color(piece_code)

        _col = None
        if row != -1:
            pass
            # inv_row = (8 - row) * 8
        elif col != "":
            _col = BoardUtils.get_number_for_col(col)

        pieces = self.w_pieces if color == Piece.WHITE else self.b_pieces

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
        self.fen = Fen.create_fen(self.state, self.color_to_move, self.castle_rights, self.en_passant_coords)
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
