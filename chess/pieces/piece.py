"""Includes the base class for each Piece."""
from chess.move import MoveDirection, Move
from typing import Tuple, Set


class Piece:
    """Base class that holds info about the piece."""

    EMPTY = 0
    KING = 1
    PAWN = 2
    KNIGHT = 3
    BISHOP = 4
    ROOK = 5
    QUEEN = 6

    WHITE = 8
    BLACK = 16
    INVALID = 32

    TYPE_MASK = 0b000111
    COLOUR_MASK = 0b011000
    ERROR_MASK = 0b100000

    def __init__(self, piece_code: int, coords: tuple):
        """Init the piece.

        Parameters
        ----------
        color : int
            The color of the created piece.
        ptype : int
            The type of the piece.
        symbol : str
            The symbol that is shown when printing the piece.
        coords : tuple
            The coordinates of the piece.
        """
        self.piece_code: int = piece_code
        self.color: int = Piece.get_colour(piece_code)
        self.enemy_color: int = Piece.get_enemy_colour(piece_code)
        self.ptype: int = Piece.get_type(piece_code)
        self.symbol: int = Piece.get_symbol(piece_code)
        self.coords: tuple = coords
        self.times_moved: int = 0
        self.is_dead: bool = False
    #     self.simulated: dict = {'is_simulated': False, 'og_coords': coords}

    # def unsimulate_move(self, end_coords):
    #     """Simulate the piece."""
    #     self.simulated['is_simulated'] = False
    #     self.coords = self.simulated['og_coords']

    # def simulate_move(self, end_coords):
    #     """Simulate the piece."""
    #     self.simulated['is_simulated'] = True
    #     self.coords = end_coords

    def __eq__(self, other: 'Piece'):
        """Overload the == when it is applied on two Piece classes to check if they are equal based on their coords and piececode."""
        if not isinstance(other, Piece):
            return False
        return self.__key() == other.__key()

    def __key(self):
        return tuple((self.piece_code, *self.coords))

    @staticmethod
    def get_enemy_colour(piece_code):
        """Given a piece code return the enemy colour."""
        color = Piece.get_colour(piece_code)
        return Piece.WHITE if color == Piece.BLACK else Piece.BLACK

    @staticmethod
    def get_enemy_possible_coords(enemy_pieces, board_state):
        """Get all the enemy moves."""
        enemy_possible_coords = set()
        for piece_code, enemy_list in enemy_pieces.items():
            for en in enemy_list:
                if piece_code == Piece.PAWN:
                    enemy_possible_coords = enemy_possible_coords | en.get_attack_possible_coords(board_state)
                else:
                    enemy_possible_coords = enemy_possible_coords | en.get_possible_coords(board_state)
        return enemy_possible_coords

    def add_moves_in_direction(self, board_state, coords_set: Set[Tuple[int]], direction: MoveDirection) -> None:
        """Found the all moves based of the 'direction' a direction.

        Given a direction it will generate all the moves until it hits either:
        1. An invalid block.
        2. An ally Piece.
        3. An enemy Piece (which he will inclide his square).

        Parameters
        ----------
        board_state : BoardStateList
            A 2d custom matrix that holds information about all the pieces on board.
        coords_set : set[tuple[int]]
            The set of the valid coords based on the criteria we added above.

        direction : MoveDirection
            The direction of which we want to generate moves to.
        """
        direction_func = Move.get_direction_func(direction)
        for i in range(1, self.range_limit):
            coords: tuple[int] = direction_func(self.coords, i)
            piece_code = board_state[coords]
            color = Piece.get_colour(piece_code)
            if piece_code == Piece.EMPTY:
                coords_set.add(coords)
            elif piece_code == Piece.INVALID or color == self.color:
                break
            elif color != self.color:
                coords_set.add(coords)
                break

    # def is_piece_and_same_color(self, o_piece) -> tuple[bool]:
    #     """Check if the given arg is an instance of Piece and then if it has the same color."""
    #     if isinstance(o_piece, Piece):
    #         if o_piece.color != self.color:
    #             return True, True
    #         return True, False
    #     return False, False

    def __hash__(self):
        """Make the obj hashable so it can be used in Sets etc."""
        return hash(self.__key())

    def __str__(self):
        """Show the piece and the coords that is on."""
        return f" {self.symbol}  coords: [{self.coords[0]}, {self.coords[1]}]"

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
        color = Piece.get_colour(piece_code)
        if ptype == Piece.PAWN:
            return '♙' if color == Piece.WHITE else '♟︎'
        elif ptype == Piece.BISHOP:
            return '♗' if color == Piece.WHITE else '♝︎'
        elif ptype == Piece.KNIGHT:
            return '♘' if color == Piece.WHITE else '♞︎'
        elif ptype == Piece.ROOK:
            return '♖' if color == Piece.WHITE else '♜︎'
        elif ptype == Piece.QUEEN:
            return '♕' if color == Piece.WHITE else '♛︎'
        elif ptype == Piece.KING:
            return '♔' if color == Piece.WHITE else '♚︎'
        elif ptype == Piece.EMPTY:
            return ' '
        else:
            raise Exception('Not a valid piece_code to get a symbol!')

    @staticmethod
    def get_colour(piece_code: int) -> int:
        """Filter the piece_code and find the piece colour.

        Parameters
        ----------
        piece_code : uint8
            A binary way to represent our pieces

        Returns
        -------
        int
            This will return only the colour part of the binary num.
        """
        return piece_code & Piece.COLOUR_MASK

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
            return ''
        path = f"{imgs_path}/"
        color = Piece.get_colour(piece_code)
        ptype = Piece.get_type(piece_code)

        if color == Piece.WHITE:
            path += 'w'
        elif color == Piece.BLACK:
            path += 'b'

        if ptype == Piece.KING:
            path += 'k'
        elif ptype == Piece.PAWN:
            path += 'p'
        elif ptype == Piece.KNIGHT:
            path += 'n'
        elif ptype == Piece.BISHOP:
            path += 'b'
        elif ptype == Piece.ROOK:
            path += 'r'
        elif ptype == Piece.QUEEN:
            path += 'q'

        return f"{path}.png"
