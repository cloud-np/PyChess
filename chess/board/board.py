"""Board module contains all the classes and methods which are needed for a chessboard to be functional."""
from typing import Dict, List, Tuple, Literal, Union, Optional
from .board_utils import BoardUtils
from .fen import Fen
from chess.pieces.piece import Piece

BOARD_OFFSET = 21


class BoardStateList(list):
    """This class helps with keeping the indexes in bound."""

    def __init__(self, *args, **kwargs):
        """Init."""
        super(BoardStateList, self).__init__(args[0])

    def __setitem__(self, indexes, o) -> None:
        """Made to handle tuples as indexes."""
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

        self.castle_rights: Dict[int, List[bool]]
        self.en_passant: Optional[Tuple[int, int]]
        # This assign does nothing here its just for readability.
        (
            pcs_and_coords,
            self.color_to_move,
            self.castle_rights,
            self.en_passant,
            self.half_move_clock,
            self.full_move
        ) = Fen.translate_to_state(fen)

        self.state, self.all_pieces = Board.setup_board_state_and_pieces(pcs_and_coords)

        # Get White Lists
        # w_pieces = Board.organize_pieces(pieces, is_whites=True)
        # # Get Black Lists
        # b_pieces = Board.organize_pieces(pieces, is_whites=False)
        # self.all_pieces = {Piece.WHITE: w_pieces, Piece.BLACK: b_pieces}

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

    @staticmethod
    def is_promoting(piece_code: int, end_coords: Tuple[int, int]) -> bool:
        """Detect if the Pawn is promoting based on each position and color.
        Assumes that is used only for Pawns."""
        ptype = Piece.get_type(piece_code)
        if ptype != Piece.PAWN:
            return False

        pcolor = Piece.get_color(piece_code)
        return end_coords[0] == {Piece.WHITE: 0, Piece.BLACK: 7}[pcolor]

    @staticmethod
    def promote_to(state, all_pieces, piece_code, prom_type) -> None:
        """Promote to a desired Piece.

        Promote to a desired Piece and update the all_pieces dictionary and state list.

        Parameters
        ----------
        piece_code : int
            Piece code that describes the piece type and color.
        """
        # Create the Piece that the pawn will transform too
        pcolor = Piece.get_color(piece_code)
        ptype = Piece.get_type(piece_code)
        piece_coords = all_pieces[pcolor][ptype][piece_code]
        # Remove the pawn from the pawn list
        all_pieces[pcolor][ptype].pop(piece_code)

        # Add it to the new piece list
        # But we keep track of which pawn it is in case we need to find it again.
        new_piece_code = Piece.get_the_specific_piece(piece_code) | prom_type | pcolor
        all_pieces[pcolor][prom_type][new_piece_code] = piece_coords
        state[piece_coords] = new_piece_code

    @staticmethod
    def simulate_board_state(board_state: BoardStateList) -> BoardStateList:
        """Given a board state it will return a 'simulated' board state.

        This will allows us to affect the board state without actually changing it.
        """
        # Slower but more compact
        return BoardStateList([[board_state[j, i] for i in range(8)] for j in range(8)])

    @staticmethod
    def get_piece(board_state, coords: Tuple[int, int]) -> int:
        """Given a coords it will return the piece that is there."""
        return board_state[coords]

    @staticmethod
    def update_piece_board_lists(piece_code: int,):
        ...

    @staticmethod
    def get_all_color_pieces(all_pieces, color) -> List[Tuple[int, Tuple[int, int]]]:
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
    def set_coordsl_to_piece(all_pieces, coords: Tuple[int, int], piece_code: int) -> None:
        """Set the coords to a piece."""
        all_pieces[Piece.get_color(piece_code)][Piece.get_type(piece_code)][piece_code] = coords

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

    @staticmethod
    def setup_board_state_and_pieces(pc_and_coords: Tuple[int, Tuple[int, int]]) -> Tuple[BoardStateList, List[Piece]]:
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
        all_pieces = {
            Piece.WHITE: {
                Piece.KING: {}, Piece.PAWN: {}, Piece.BISHOP: {},
                Piece.KNIGHT: {}, Piece.ROOK: {}, Piece.QUEEN: {}
            },
            Piece.BLACK: {
                Piece.KING: {}, Piece.PAWN: {}, Piece.BISHOP: {},
                Piece.KNIGHT: {}, Piece.ROOK: {}, Piece.QUEEN: {}
            }
        }

        for pc, coords in pc_and_coords:
            state[coords] = pc
            pcolor = Piece.get_color(pc)
            ptype = Piece.get_type(pc)
            all_pieces[pcolor][ptype][pc] = coords
        return state, all_pieces

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
        self.fen = Fen.create_fen(self.state, self.color_to_move, self.castle_rights, self.en_passant)
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
