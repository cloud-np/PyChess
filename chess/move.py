from chess.piece import Piece


def WRONG_INPUT(u_input): return ValueError(f"Wrong move input: {u_input}")


PIECE_SYMBOLS = "rnbqk"
TILE_NUMBERS = "12345678"
TILE_NAMES = "abcdefgh"

class MoveTypes:
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


class Move:

    def __init__(self, piece_code, start_tile, end_tile, move_code, read_form):
        self.piece_code = piece_code
        self.start_tile = start_tile
        self.end_tile = end_tile
        self.move_code = move_code
        self.read_form = read_form
    
    def __str__(self):
        return f"start_tile: {self.start_tile}\n" + \
               f"end_tile: {self.end_tile}\n" + \
               f"piece_code: {self.piece_code}\n" + \
               f"move_code: {self.move_code}\n"

    @staticmethod
    def decode_to_move(move_str, board, is_white_turn):
        # Because of the case for e.g: "exf4"
        # we can't be sure if the piece is black or not
        piece_code = Piece.EMPTY
        move_code = MoveTypes.NORMAL
        start_tile = -1
        end_tile = -1

        # Find colour
        if (move_str[0] not in TILE_NAMES) and \
           ((move_str[0].isupper() and not is_white_turn) or (move_str[0].islower() and is_white_turn)):
            raise WRONG_INPUT(move_str)
        else:
            piece_code |= Piece.WHITE if move_str[0].isupper() else Piece.BLACK

        # Find piece type
        if move_str[0].lower() in PIECE_SYMBOLS:
            piece_code |= Piece.find_piece_from_symbol(move_str[0].lower())
            if move_str[1] in TILE_NAMES:
                start_tile = board.find_tile_from_piece(piece_code, col=move_str[1])
            else:
                start_tile = board.find_tile_from_piece(piece_code)

        elif move_str[0] in TILE_NAMES:
            piece_code |= Piece.PAWN

        for i, ch in enumerate(move_str[1:]):
            if ch == 'x':
                move_code = Move.has_action_repeated(move_code, MoveTypes.TAKES)
            elif ch == '+':
                move_code = Move.has_action_repeated(move_code, MoveTypes.CHECK)
            elif ch == '#':
                move_code = Move.has_action_repeated(move_code, MoveTypes.CHECKMATE)
            elif ch in TILE_NUMBERS:
                end_tile = board.find_tile_from_str(row=ch, col=move_str[i])
            # We can have a piece symbol only in the very first pos.
            elif ch not in (TILE_NUMBERS + TILE_NAMES):
                raise WRONG_INPUT(move_str)

        return Move(piece_code, start_tile, end_tile, move_code, move_str)

    def has_action_repeated(move_code, move_action) -> int:
        """Check if move action has been repeated.

        Parameters
        ----------
        move_code : int
            A binary way to represent our moves.
        move_action : int
            A binary way to show the type of the move action.
        """        
        if (move_code & MoveTypes.MOVE_MASK) == move_action:
            move_code = MoveTypes.VALUE_ERROR
        else:
            move_code |= move_action
        return move_code

    # TODO Work in progress. (No real reason to make this yet)

    def encode_to_str(self) -> str:
        move_str = ''

        # if self.

        return move_str
