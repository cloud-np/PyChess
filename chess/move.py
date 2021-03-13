from chess.piece import Piece


class Move:

    def __init__(self, piece_code, start_tile, end_tile, takes=False, check=False, checkmate=False):
        self.piece_code = piece_code
        self.start_tile = start_tile
        self.end_tile = end_tile
        self.takes = takes
        self.check = check
        self.checkmate = checkmate


    # TODO Work in progress. (No real reason to make this yet)
    @staticmethod
    def decode_to_move(move_str):
        # Because of the case for e.g: "exf4"
        # we can't be sure if the piece is black or not
        piece_code = Piece.EMPTY
        takes = False
        if move_str[0] in "rnbqk":
            if move_str[0].isupper():
                piece_code = Piece.BLACK
            else:
                piece_code = Piece.WHITE
        else:
            piece_code = Piece.PAWN
        
        if move_str[1] == "x":
            takes = True
        
        
        # for ch in move_str[1:]:
        #     chl = ch.lower()
        #     if chl in "rnbqk":
        

        return Move(piece_code,)

    # TODO Work in progress. (No real reason to make this yet)
    # R2b6
    def piece_code_to_str(self):
        colour, type = Piece.get_colour_and_type(self.piece_code)
        if type == Piece.KING:
            pc_str = 'k'
        elif type == Piece.PAWN:
            pc_str = ''
        elif type == Piece.BISHOP:
            pc_str = 'b'
        elif type == Piece.KNIGHT:
            pc_str = 'n'
        elif type == Piece.ROOK:
            pc_str = 'r'
        elif type == Piece.QUEEN:
            pc_str = 'q'
        
        return pc_str
        

    # TODO Work in progress. (No real reason to make this yet)
    def encode_to_str(self) -> str:
        move_str = ''

        # if self.

        return move_str