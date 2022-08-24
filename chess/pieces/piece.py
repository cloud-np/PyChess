"""Includes the base class for each Piece."""
from chess.move import MoveDirection, Move
from typing import Tuple, Set, Optional, List, Dict, Callable, Literal


class CastleSide:
    """Represents a side of a castle."""

    WK_SIDE_L = 0
    WK_SIDE_R = 1
    BK_SIDE_L = 2
    BK_SIDE_R = 3

    @staticmethod
    def get_side(end_coords) -> Optional[int]:
        """Return the side of the castle.

        We use .get() to avoid KeyErrors.
        """
        return {
            (7, 6): CastleSide.WK_SIDE_R,
            (7, 2): CastleSide.WK_SIDE_L,
            (0, 6): CastleSide.BK_SIDE_R,
            (0, 2): CastleSide.BK_SIDE_L
        }.get(end_coords)

    @staticmethod
    def get_rook_posistions(castling_side: int) -> tuple:
        """Return the positions of the rooks involved in a castling.

        Based on the castling side we return the positions of the rook before and after the castling.
        """
        if castling_side == CastleSide.WK_SIDE_R:
            return (7, 5), (7, 7)
        elif castling_side == CastleSide.WK_SIDE_L:
            return (7, 3), (7, 0)
        elif castling_side == CastleSide.BK_SIDE_R:
            return (0, 5), (0, 7)
        elif castling_side == CastleSide.BK_SIDE_L:
            return (0, 3), (0, 0)
        else:
            raise ValueError("Invalid castling side.")


class Piece:
    """Base class that holds info about the piece."""

    EMPTY = 0x0  # 0
    KING = 0x1  # 1
    PAWN = 0x2  # 2
    KNIGHT = 0x3  # 3
    BISHOP = 0x4  # 4
    ROOK = 0x5  # 5
    QUEEN = 0x6  # 6

    A_PAWN = 0x10  # 16
    B_PAWN = 0x20  # 32
    C_PAWN = 0x30  # 48
    D_PAWN = 0x40  # 64
    E_PAWN = 0x50  # 80
    F_PAWN = 0x60  # 96
    G_PAWN = 0x70  # 112
    H_PAWN = 0x80  # 128
    LEFT_PIECE = 0x90  # 144
    RIGHT_PIECE = 0xA0  # 160

    WHITE = 0x100  # 256
    BLACK = 0x200  # 512
    INVALID = 0x300  # 4096

    TYPE_MASK = 0xF  # 7
    # ANTI_TYPE_MASK = 0xFF0
    UNIQUE_PIECE_MASK = 0xF0  # 240
    COLOR_MASK = 0xF00  # 3840

    WK_R_CASTLE = [(7, 5), (7, 6)]
    BK_R_CASTLE = [(0, 5), (0, 6)]
    WK_L_CASTLE = [(7, 3), (7, 2), (7, 1)]
    BK_L_CASTLE = [(0, 3), (0, 2), (0, 1)]

    WHITE_KING = WHITE | KING
    BLACK_KING = BLACK | KING

    @staticmethod
    def get_the_specific_piece(piece_code: int) -> int:
        """Return which specific piece is this."""
        return piece_code & Piece.UNIQUE_PIECE_MASK

    @staticmethod
    def get_enemy_color(our_piece_code: int) -> int:
        """Given a piece code return the enemy color."""
        return (
            Piece.WHITE
            if Piece.get_color(our_piece_code) == Piece.BLACK
            else Piece.BLACK
        )

    @staticmethod
    def is_king_in_check(board_state, all_pieces, en_passant, piece_code) -> bool:
        """Check if the king is in check."""
        # Check if the king is in check from the rest of the pieces
        # enemy_possible_coords = set()
        pcolor = Piece.get_color(piece_code)
        enemy_color = Piece.get_enemy_color(piece_code)
        enemy_pieces = all_pieces[enemy_color]
        king_coords = all_pieces[pcolor][Piece.KING][pcolor | Piece.KING]

        for piece_code, enemy_list in enemy_pieces.items():
            if piece_code == Piece.PAWN | enemy_color:
                continue

            # NOTE: Keep track of the attacking direction of the enemy piece.
            #       THERE MAY BE MUTLIPLE DIRECTIONS OF ATTACKS.
            for en, en_coords in enemy_list.items():
                if king_coords in Piece.get_possible_coords(board_state, (en, en_coords), en_passant):
                    return True

        # # Check if the king is in check from pawns
        # for en_pawn in enemies_pieces[Piece.PAWN | enemy_color]:
        #     enemy_possible_coords = enemy_possible_coords | en_pawn.get_attack_possible_coords(board_state)
        #     if self.coords in enemy_possible_coords:
        #         return True

        return False

    # @staticmethod
    # def get_enemy_possible_coords(board_state, enemy_pieces, en_passant):
    #     """Get all the enemy moves."""
    #     enemy_possible_coords = set()
    #     for ptype, enemy_list in enemy_pieces.items():
    #         for en, en_coords in enemy_list:
    #             # if piece_code == Piece.PAWN:
    #             #     enemy_possible_coords = enemy_possible_coords | en.get_attack_possible_coords(board_state)
    #             # else:
    #             enemy_possible_coords = (
    #                 enemy_possible_coords | Piece.get_possible_coords((en, en_coords), board_state, en_passant)
    #             )
    #     return enemy_possible_coords

    @staticmethod
    def get_castle_coords(piece_code: int, side: int) -> Optional[List[Tuple[int, int]]]:
        if Piece.get_type(piece_code) == Piece.KING:
            return {
                Piece.WHITE | Piece.RIGHT_PIECE: [(7, 5), (7, 6)],
                Piece.WHITE | Piece.LEFT_PIECE: [(7, 3), (7, 2), (7, 1)],
                Piece.BLACK | Piece.RIGHT_PIECE: [(0, 5), (0, 6)],
                Piece.BLACK | Piece.LEFT_PIECE: [(0, 3), (0, 2), (0, 1)]
            }[Piece.get_color(piece_code) | side]
        return None

    @staticmethod
    def rook_moves(board_state, piece_info):
        """Override the get_moves from Piece class."""
        moves = set()
        for md in [
            MoveDirection.UP,
            MoveDirection.DOWN,
            MoveDirection.LEFT,
            MoveDirection.RIGHT,
        ]:
            Piece.add_moves_in_direction(board_state, 8, piece_info, moves, md)
        return moves

    @staticmethod
    def bishop_moves(board_state, piece_info):
        """Override the get_moves from Piece class."""
        moves = set()
        for md in [
            MoveDirection.UP_LEFT,
            MoveDirection.UP_RIGHT,
            MoveDirection.DOWN_LEFT,
            MoveDirection.DOWN_RIGHT,
        ]:
            Piece.add_moves_in_direction(board_state, 8, piece_info, moves, md)
        return moves

    @staticmethod
    def knight_moves(board_state, piece_info):
        """Knight moves."""
        # We could get 'fancy' and use permutation but it generates 4 more cases
        # which we do not need and it would take couple ifs to get rid of them.
        pcoords = piece_info[1]
        possible_coords = [
            (pcoords[0] - 1, pcoords[1] - 2),
            (pcoords[0] - 2, pcoords[1] - 1),
            (pcoords[0] + 1, pcoords[1] - 2),
            (pcoords[0] + 2, pcoords[1] - 1),
            (pcoords[0] + 1, pcoords[1] + 2),
            (pcoords[0] + 2, pcoords[1] + 1),
            (pcoords[0] - 1, pcoords[1] + 2),
            (pcoords[0] - 2, pcoords[1] + 1),
        ]

        return {
            c
            for c in possible_coords
            if board_state[c] == Piece.EMPTY
            or Piece.get_color(board_state[c]) == Piece.get_enemy_color(piece_info[0])
        }

    @staticmethod
    def queen_moves(board_state, piece_info):
        """Override the get_moves from Piece class."""
        moves = set()
        for md in [MoveDirection.UP, MoveDirection.DOWN, MoveDirection.LEFT, MoveDirection.RIGHT, MoveDirection.UP_LEFT,
                   MoveDirection.UP_RIGHT, MoveDirection.DOWN_LEFT, MoveDirection.DOWN_RIGHT]:
            Piece.add_moves_in_direction(board_state, 8, piece_info, moves, md)
        return moves

    @staticmethod
    def king_moves(board_state, piece_info):
        """Override the get_moves from Piece class."""
        moves = set()
        for md in [MoveDirection.UP, MoveDirection.DOWN, MoveDirection.LEFT, MoveDirection.RIGHT, MoveDirection.UP_LEFT,
                   MoveDirection.UP_RIGHT, MoveDirection.DOWN_LEFT, MoveDirection.DOWN_RIGHT]:
            Piece.add_moves_in_direction(board_state, 2, piece_info, moves, md)
        return moves

    @staticmethod
    def pawn_attack_moves(board_state, piece_info: Dict[int, Tuple[int, int]], en_passant: Optional[Tuple[int, int]]) -> Set[Tuple[int, int]]:
        """Get the attackable coords for the pawn."""
        moves: Set[Tuple[int, int]] = set()
        pcolor: int = Piece.get_color(piece_info[0])
        coords: Tuple[int, int] = piece_info[1]

        if pcolor == Piece.WHITE:
            l_coords = coords[0] - 1, coords[1] - 1
            r_coords = coords[0] - 1, coords[1] + 1
        else:
            l_coords = coords[0] + 1, coords[1] - 1
            r_coords = coords[0] + 1, coords[1] + 1

        # We check for the enemy color to avoid to check for Piece.INVALID
        # for example [5, 8] checks for != Piece.EMPTY and has diff color vs our pcolor
        # Left enemy
        left_enemy = board_state[l_coords]
        if left_enemy != Piece.EMPTY and Piece.get_enemy_color(left_enemy) == pcolor:
            moves.add(l_coords)
        elif en_passant is not None and en_passant == l_coords:
            moves.add(l_coords)
        # Right enemy
        right_enemy = board_state[r_coords]
        if right_enemy != Piece.EMPTY and Piece.get_enemy_color(right_enemy) == pcolor:
            moves.add(r_coords)
        elif en_passant is not None and en_passant == r_coords:
            moves.add(r_coords)

        return moves


    @staticmethod
    def pawn_moves(board_state, piece_info, en_passant: Tuple[int, int]):
        """Override the get_moves from Piece class."""
        moves = set()
        # for md in [
        #     MoveDirection.UP,
        #     MoveDirection.DOWN,
        #     MoveDirection.LEFT,
        #     MoveDirection.RIGHT,
        # ]:
        #     Piece.add_moves_in_direction(board_state, 2, piece_info, moves, md)

        """Override the get_moves from Piece class."""
        moves = set()
        piece_code, piece_coords = piece_info
        if Piece.get_color(piece_code) == Piece.WHITE:
            if piece_coords[0] >= 1:
                coords_to_go = piece_coords[0] - 1, piece_coords[1]
                piece_code = board_state[coords_to_go]
                if piece_code == Piece.EMPTY:
                    moves.add(coords_to_go)
            if piece_coords[0] == 6:
                coords_to_go = piece_coords[0] - 2, piece_coords[1]
                piece_code = board_state[piece_coords[0] - 1, piece_coords[1]]
                piece_code2 = board_state[coords_to_go]
                if piece_code == Piece.EMPTY and piece_code2 == Piece.EMPTY:
                    moves.add(coords_to_go)
        else:
            if piece_coords[0] <= 6:
                coords_to_go = piece_coords[0] + 1, piece_coords[1]
                piece_code = board_state[coords_to_go]
                if piece_code == Piece.EMPTY:
                    moves.add(coords_to_go)
            if piece_coords[0] == 1:
                coords_to_go = piece_coords[0] + 2, piece_coords[1]
                piece_code = board_state[piece_coords[0] + 1, piece_coords[1]]
                piece_code2 = board_state[coords_to_go]
                if piece_code == Piece.EMPTY and piece_code2 == Piece.EMPTY:
                    moves.add(coords_to_go)
        moves |= Piece.pawn_attack_moves(board_state, piece_info, en_passant)
        return moves

    @staticmethod
    def get_possible_coords(board_state, piece_info: Tuple[int, Tuple[int, int]], en_passant: Tuple[int, int]) -> Set[Tuple[int, int]]:
        """Return all the possible coords for a piece.

        Returns all the possible coords given a piece_code and a board_state.

        Parameters
        ----------
            piece_info : Tuple[int, Tuple[int, int]]
                It containers the piece_code and the coordinates of the piece.
        """
        ptype = Piece.get_type(piece_info[0])
        piece_func: Callable = {
            Piece.KING: Piece.king_moves,
            Piece.PAWN: Piece.pawn_moves,
            Piece.KNIGHT: Piece.knight_moves,
            Piece.BISHOP: Piece.bishop_moves,
            Piece.ROOK: Piece.rook_moves,
            Piece.QUEEN: Piece.queen_moves,
        }[ptype]
        if ptype == Piece.PAWN:
            return piece_func(board_state, piece_info, en_passant)
        else:
            return piece_func(board_state, piece_info)

    @staticmethod
    def add_moves_in_direction(
        board_state,
        range_limit: int,
        piece_info: Tuple[int, Tuple[int, int]],
        coords_set: Set[Tuple[int]],
        direction: MoveDirection,
    ) -> None:
        """Found the all moves based of the 'direction' a direction.

        Given a direction it will generate all the moves until it hits either:
        1. An invalid block.
        2. An ally Piece.
        3. An enemy Piece (which he will inclide his square).

        Parameters
        ----------
        board_state : BoardStateList
            A 2d custom matrix that holds information about all the pieces on board.
        coords_set : Set[Tuple[int, int]]
            The set of the valid coords based on the criteria we added above.

        direction : MoveDirection
            The direction of which we want to generate moves to.
        """
        direction_func = Move.get_direction_func(direction)
        curr_pcolor = Piece.get_color(piece_info[0])
        for i in range(1, range_limit):
            coords: Tuple[int, int] = direction_func(piece_info[1], i)
            dir_pc = board_state[coords]
            dir_pcolor = Piece.get_color(dir_pc)

            if dir_pc == Piece.EMPTY:
                coords_set.add(coords)
            elif dir_pc == Piece.INVALID or dir_pcolor == curr_pcolor:
                break
            else:
                coords_set.add(coords)
                break

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
        color = Piece.get_color(piece_code)
        if ptype == Piece.PAWN:
            return "♙" if color == Piece.WHITE else "♟︎"
        elif ptype == Piece.BISHOP:
            return "♗" if color == Piece.WHITE else "♝︎"
        elif ptype == Piece.KNIGHT:
            return "♘" if color == Piece.WHITE else "♞︎"
        elif ptype == Piece.ROOK:
            return "♖" if color == Piece.WHITE else "♜︎"
        elif ptype == Piece.QUEEN:
            return "♕" if color == Piece.WHITE else "♛︎"
        elif ptype == Piece.KING:
            return "♔" if color == Piece.WHITE else "♚︎"
        elif ptype == Piece.EMPTY:
            return " "
        else:
            raise Exception("Not a valid piece_code to get a symbol!")

    @staticmethod
    def get_color(piece_code: int) -> Literal[256, 512]:
        """Filter the piece_code and find the piece color.

        Parameters
        ----------
        piece_code : uint8
            A binary way to represent our pieces

        Returns
        -------
        int
            This will return only the color part of the binary num.
        """
        return piece_code & Piece.COLOR_MASK

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
        if piece_code == Piece.EMPTY:
            return ""
        path = f"{imgs_path}/"
        color = Piece.get_color(piece_code)
        ptype = Piece.get_type(piece_code)

        if color == Piece.WHITE:
            path += "w"
        elif color == Piece.BLACK:
            path += "b"

        if ptype == Piece.KING:
            path += "k"
        elif ptype == Piece.PAWN:
            path += "p"
        elif ptype == Piece.KNIGHT:
            path += "n"
        elif ptype == Piece.BISHOP:
            path += "b"
        elif ptype == Piece.ROOK:
            path += "r"
        elif ptype == Piece.QUEEN:
            path += "q"

        return f"{path}.png"
