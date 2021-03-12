"""Holds everything related to a piece."""


class Piece:
    """Info about the piece type moves-set."""

    EMPTY  = 0 
    KING   = 1
    PAWN   = 2
    KNIGHT = 3
    BISHOP = 5
    ROOK   = 6
    QUEEN  = 7

    WHITE  = 8
    BLACK  = 16

    TYPE_MASK = 0b00111
    COLOUR_MASK = 0b11000

    # def __init__(self, piece_code):
    #     if piece_code <= 0:
    #         raise ValueError(f"Invalid piece_code: {piece_code}")

    #     self.piece_code = piece_code
    #     self.moveset = self.__find_correct_moveset()

    @staticmethod
    def get_type(piece_code):
        return piece_code & Piece.TYPE_MASK

    @staticmethod
    def get_colour(piece_code):
        return piece_code & Piece.COLOUR_MASK

    @staticmethod 
    def get_colour_and_type(piece_code):
        return (Piece.get_colour(piece_code), Piece.get_type(piece_code))

    def find_symbol(piece_code):
        symbol = ''
        colour, type = Piece.get_colour_and_type(piece_code)

        if type == Piece.EMPTY:
            return ' '
        if type == Piece.KING:
            symbol += 'k'
        elif type == Piece.PAWN:
            symbol += 'p'
        elif type == Piece.KNIGHT:
            symbol += 'n'
        elif type == Piece.BISHOP:
            symbol += 'b'
        elif type == Piece.ROOK:
            symbol += 'r'
        elif type == Piece.QUEEN:
            symbol += 'q'
        
        if colour == Piece.WHITE:
            return symbol.upper()
        else:
            return symbol



    def find_moveset(piece_code):
        if piece_code & Piece.KING:
            return Piece.king_moveset
        elif piece_code & Piece.PAWN:
            return Piece.pawn_moveset
        elif piece_code & Piece.KNIGHT:
            return Piece.knight_moveset
        elif piece_code & Piece.BISHOP:
            return Piece.bishop_moveset
        elif piece_code & Piece.ROOK:
            return Piece.rook_moveset
        elif piece_code & Piece.QUEEN:
            return Piece.queen_moveset

    @staticmethod
    def queen_moveset():
        pass

    @staticmethod
    def rook_moveset():
        pass

    @staticmethod
    def bishop_moveset():
        pass

    @staticmethod
    def knight_moveset():
        pass

    @staticmethod
    def pawn_moveset():
        pass

    @staticmethod
    def king_moveset(self):
        pass
