"""Board module contains all the classes and methods which are needed for a chessboard to be functional."""
import numpy as np
from typing import Dict, List, Tuple, Literal, Union, Optional

from .board_utils import BoardUtils
from .fen import Fen
from chess.pieces.piece import Piece

BOARD_OFFSET = 21


# class BoardStateList(list):
#     """This class helps with keeping the indexes in bound."""

#     def __init__(self, *args, **kwargs):
#         """Init."""
#         super(BoardStateList, self).__init__(args[0])

#     def __setitem__(self, indexes, o) -> None:
#         """Made to handle tuples as indexes."""
#         self[indexes[0]][indexes[1]] = o

#     def __getitem__(self, indexes):
#         """Handle out of bounds board indexes."""
#         if type(indexes) is int:
#             return super().__getitem__(indexes)
#         for i in indexes:
#             if not 0 <= i <= 7:
#                 return Piece.INVALID
#         return super().__getitem__(indexes[0]).__getitem__(indexes[1])




class Board:
    """The way we represent our Board is a Piece centric way.

    Description:
    Meaing a tile on the board has some properties and holds
    info about the piece that either occupies it there or not.
    """
    # Castling
    # 4 bits
    WL_CASTLE = 0x1
    WR_CASTLE = 0x2
    BL_CASTLE = 0x3
    BR_CASTLE = 0x4

    CASTLE_MASK = 0xF
    EN_PASSANT_MASK = 0xFF
    FIFITY_MOVE_MASK = 0xFF

    # Captured Piece
    # 12 bits

    # En passant
    # It shows the square (1-64) 
    # 8 bits

    # Fifty move clock
    # 8 bits

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
        self.color_to_move: Literal[256, 512]
        # This assign does nothing here its just for readability.
        (
            pcs_and_coords,
            self.color_to_move,
            self.castle_rights,
            self.en_passant,
            self.half_move_clock,
            self.full_move
        ) = Fen.translate_to_state(fen)

        self.state, self.all_pieces = Board.setup_state_and_pieces(pcs_and_coords)

        # Get White Lists
        # w_pieces = Board.organize_pieces(pieces, is_whites=True)
        # # Get Black Lists
        # b_pieces = Board.organize_pieces(pieces, is_whites=False)

        self.dead_pieces: List[int] = []
        self.correct_format_print()

    def try_update_castle_rights(self, moving_piece: np.uint32) -> None:
        """Remove castling privileges depending the moving piece."""
        # Only for the first time the King is moving.
        pcolor = Piece.get_color(moving_piece)
        ptype = Piece.get_type(moving_piece)
        if ptype == Piece.KING:
            self.castle_rights[pcolor] = [False, False]

        if Piece.get_type(moving_piece) == Piece.ROOK:
            # Check if the rook moved was in the Right half of the board.
            if Piece.get_the_specific_piece(moving_piece) == Piece.RIGHT_PIECE:
                self.castle_rights[pcolor][1] = False

            # Check if the rook moved was in the Left half of the board.
            if Piece.get_the_specific_piece(moving_piece) == Piece.LEFT_PIECE:
                self.castle_rights[pcolor][0] = False

    @staticmethod
    def is_promoting(piece: np.uint32, end_coords: Tuple[int, int]) -> bool:
        """Detect if the Pawn is promoting based on each position and color.
        Assumes that is used only for Pawns."""
        ptype = Piece.get_type(piece)
        if ptype != Piece.PAWN:
            return False

        pcolor = Piece.get_color(piece)
        return end_coords[0] == {Piece.WHITE: 0, Piece.BLACK: 7}[pcolor]

    @staticmethod
    def promote_to(state, piece, prom_type) -> None:
        """Promote to a desired Piece.

        Promote to a desired Piece and update the all_pieces dictionary and state list.

        Parameters
        ----------
        piece : int
            Piece code that describes the piece type and color.
        """
        # Create the Piece that the pawn will transform too
        pcolor = Piece.get_color(piece)
        ptype = Piece.get_type(piece)
        all_piece_coords = np.where(state == ptype)
        piece_coords = (all_piece_coords[0][0], all_piece_coords[1][0])

        # Add it to the new piece list
        # But we keep track of which pawn it is in case we need to find it again.
        new_piece = Piece.get_the_specific_piece(piece) | prom_type | pcolor
        state[piece_coords] = new_piece

    @staticmethod
    def simulate_state(state: np.ndarray) -> np.ndarray:
        """Given a board state it will return a 'simulated' board state.

        This will allows us to affect the board state without actually changing it.
        """
        # Slower but more compact
        return np.copy(state)

    @staticmethod
    def get_piece(state: np.ndarray, coords: Tuple[int, int]) -> int:
        """Given a coords it will return the piece that is there."""
        return state[coords]

    @staticmethod
    def update_piece_board_lists(piece: np.uint32,):
        ...
    
    def get_king_coords(self, color: Literal[256, 512]):
        # kpos = np.where(state == color | Piece.KING)
        # return (kpos[1][0], kpos[1][0])
        return self.all_pieces[color][Piece.KING][Piece.KING | color]

    @staticmethod
    def find_king(state, color: Literal[256, 512]):
        return np.where(state == color | Piece.KING) 

    def get_enemies(self, color) -> Dict[np.uint32, Tuple[np.uint32, Tuple[int, int]]]:
        # ecolor = Piece.get_enemy_color(color)
        # enemies = []
        # for i, row in enumerate(state):
        #     enemies.extend((e, (i, j)) for j, e in enumerate(row) if Piece.get_color(e) == ecolor)
        # return enemies
        return self.all_pieces[Piece.get_enemy_color(color)]

    # @staticmethod
    # def get_piece_coords(state, piece: np.uint32) -> Optional[Tuple[int, int]]:
    #     """Given a piece find the coords of the piece.

    #     Find the piece obj that corrisponds to
    #     coords and the piece code that was given.
    #     """
    #     if piece == Piece.EMPTY:
    #         return None
    #     pcolor = Piece.get_color(piece)
    #     ptype = Piece.get_type(piece)
    #     return [p for p in Board.get_enemies(state, pcolor)][0]

    # @staticmethod
    # def set_coordsl_to_piece(coords: Tuple[int, int], piece: np.uint32) -> None:
    #     """Set the coords to a piece."""
    #     all_pieces[Piece.get_color(piece)][Piece.get_type(piece)][piece] = coords

    @staticmethod
    def setup_state_and_pieces(pc_and_coords: List[Tuple[np.uint32, Tuple[int, int]]]) -> Tuple[np.ndarray, dict]:
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
        # state = BoardStateList([[Piece.EMPTY for _ in range(8)] for _ in range(8)])
        state: np.ndarray = np.zeros((8, 8), dtype=np.uint32)
        all_pieces = { Piece.WHITE: { 
                Piece.PAWN: {}, Piece.KING: {},
                Piece.BISHOP: {}, Piece.ROOK: {},
                Piece.KNIGHT: {}, Piece.QUEEN: {}
            }, 
            Piece.BLACK: {
                Piece.PAWN: {}, Piece.KING: {},
                Piece.BISHOP: {}, Piece.ROOK: {},
                Piece.KNIGHT: {}, Piece.QUEEN: {} }}

        for pc, coords in pc_and_coords:
            state[coords] = pc
            pcolor = Piece.get_color(pc)
            ptype = Piece.get_type(pc)
            all_pieces[pcolor][ptype][pc] = coords
        return state, all_pieces

    def are_coords_empty(self, coords_list: List[Tuple[int, int]]) -> bool:
        """Check if ALL the given coords are empty."""
        return all(self.state[coords] == Piece.EMPTY for coords in coords_list)

    def get_fen(self) -> str:
        """Get the fen for the board."""
        self.fen = Fen.create_fen(self.state, self.color_to_move, self.castle_rights, self.en_passant, self.half_move_clock, self.full_move)
        return self.fen

    def __str__(self):
        """Print the board state."""
        print("\n      0     1     2     3     4     5     6     7")
        for row in range(8):
            print(f"\n{row}", end="   ")
            for col in range(8):
                piece = self.state[row, col]
                print(f"[ {Piece.get_symbol(piece)} ]", end=" ")
        print(f"\n{self.get_fen()}")
        return " "

    def correct_format_print(self):
        """Print the board state in correct format."""
        for row in range(8, 0, -1):
            print(f"\n{row}", end="   ")
            for col in range(8, 0, -1):
                piece = self.state[8 - row, 8 - col]
                print(f"[ {Piece.get_symbol(piece)} ]", end=" ")
        print("\n\n      a     b     c     d     e     f     g     h\n\n")
        print(f"{self.get_fen()}\n\n")
        return " "
