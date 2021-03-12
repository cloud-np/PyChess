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
    def get_colour(piece_code):
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

    @staticmethod 
    def get_colour_and_type(piece_code):
        """Get both the colour and the type of the piece.

        Parameters
        ----------
        piece_code : uint8
            A binary way to represent our pieces

        Returns
        -------
        tuple 
            A tuple with both the colour and the type of the piece.
        """        
        return (Piece.get_colour(piece_code), Piece.get_type(piece_code))

    def find_symbol(piece_code):
        """Find the correct symbol for a piece.

        Parameters
        ----------
        piece_code : uint8
            A binary way to represent our pieces

        Returns
        -------
        str
            The corresponding symbol for the piece.
        """        
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
        """Find the correct moveset for a piece.

        Parameters
        ----------
        piece_code : uint8
            A binary way to represent our pieces

        Returns
        -------
        function
            The corresponding moveset for the piece.
        """        
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
    def queen_moveset(pos):
        """Generate queen moves based on the position."""        
        pass

    @staticmethod
    def rook_moveset(pos):
        """Generate rook moves based on the position."""        
        pass

    @staticmethod
    def bishop_moveset(pos):
        """Generate bishop moves based on the position."""        
        pass

    @staticmethod
    def knight_moveset(pos):
        """Generate knight moves based on the position."""        
        pass

    @staticmethod
    def pawn_moveset(pos):
        """Generate pawn moves based on the position."""        
        pass

    @staticmethod
    def king_moveset(pos):
        """Generate king moves based on the position."""        
        pass
