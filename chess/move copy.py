from chess.piece import Piece


WRONG_INPUT = lambda u_input: ValueError(f"Wrong move input: {u_input}")
PIECE_SYMBOLS = "rnbqkp"
TILE_NUMBERS = "12345678"
TILE_NAMES = "abcdefgh"

class Move:

    NORMAL = 0
    TAKES = 1
    CHECK = 2
    CASTLE_SHORT = 3
    CASTLE_LONG = 5
    CHECKMATE = 6
    EN_PASSAT = 7

    ILLEGAL = 8
    VALUE_ERROR = 16

    MOVE_MASK = 0b00111
    ERROR_MASK = 0b11000

    def __init__(self, piece_code, start_tile, end_tile, move_code):
        self.piece_code = piece_code
        self.start_tile = start_tile
        self.end_tile = end_tile
        self.move_code = move_code


    # TODO Work in progress. (No real reason to make this yet)
    @staticmethod
    def decode_to_move(move_str):
        # Because of the case for e.g: "exf4"
        # we can't be sure if the piece is black or not
        piece_code = Piece.EMPTY
        move_code = Move.NORMAL
        start_tile = -1
        end_tile = -1
        if move_str[0] in "rnbqk":
            piece_code = Piece.BLACK if move_str[0].isupper() else Piece.WHITE
        else:
            piece_code = Piece.PAWN
       
        for i, ch in enumerate(move_str):
            if ch not in (PIECE_SYMBOLS + TILE_NUMBERS + TILE_NAMES):
                raise WRONG_INPUT
            if ch in TILE_NUMBERS:
                if move_str[i - 1].lower() in "":
                    pass

            if ch == 'x':
                Move.has_action_repeated(move_code, Move.TAKES)
            elif ch == '+':
                Move.has_action_repeated(move_code, Move.CHECK)
            elif ch == '#':
                Move.has_action_repeated(move_code, Move.CHECKMATE)

        

        return Move(piece_code, start_tile, end_tile, move_code)

    def has_action_repeated(move_code, move_action):
        if (move_code & Move.MOVE_MASK) == move_action:
            move_code = Move.VALUE_ERROR
        else:
            move_code |= move_action

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
