"""Holds everything related to a piece."""


class Piece:
    """Info about the piece type moves-set."""

    EMPTY = 0b0
    KING = 0b1
    PAWN = 0b10
    KNIGHT = 0b11
    BISHOP = 0b100
    ROOK = 0b101
    QUEEN = 0b110

    WHITE = 0b1000
    BLACK = 0b10000

    # def __init__(self, piece_code):
    #     if piece_code <= 0:
    #         raise ValueError(f"Invalid piece_code: {piece_code}")

    #     self.piece_code = piece_code
    #     self.moveset = self.__find_correct_moveset()


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
