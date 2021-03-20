from chess.piece import Piece


def WRONG_INPUT(u_input, msg="Wrong move input:"): 
    """Help with readability."""    
    return ValueError(f"{msg} {u_input}")


PIECE_SYMBOLS = "rnbqk"
TILE_NUMBERS = "12345678"
TILE_NAMES = "abcdefgh"

class MoveTypes:
    """A binary way to represent move types."""    

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
    """Holds crucial info about registered moves."""    

    def __init__(self, piece_code, start_tile, end_tile, move_code, read_form):
        """Construct a move with basic components.

        Parameters
        ----------
        piece_code : unit8
            A binary way to represent our Pieces.
        start_tile : int
            The starting tile of the piece right before it moved.
        end_tile : int
            The ending tile of the piece right after it moved.
        move_code : int
            A binary way to represent our MoveTypes.
        read_form : str
            Human readable way to represent the move.
        """        
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

    #TODO write this a bit cleaner.
    def is_symbol_turn(move_str, is_white_turn):
        """Return whether or not its the first symbol correct and if its his team turn to play."""        
        if (move_str[0] not in TILE_NAMES) and \
           ((move_str[0].isupper() and not is_white_turn) 
           or (move_str[0].islower() and is_white_turn)):
            raise WRONG_INPUT(move_str, msg="Wrong piece team entered.")
        return True


    # TODO A regex way should be way more readable but this works for now.
    @staticmethod
    def decode_to_move(move_str, board, is_white_turn):
        """Based on a string that represents the move decode it into a move.

        Parameters
        ----------
        move_str : str
            The str that represents the move.
        board : np.array(64, dtype="uint8")
            Holds the positions of all the pieces on board.
        is_white_turn : bool
            Shows which teams is turn to play.

        Returns
        -------
        Move
            Return the propossed move.

        Raises
        ------
        WRONG_INPUT
            If the string input is not in correct format return an error.
        """        
        # Because of the case for e.g: "exf4"
        # we can't be sure if the piece is black or not
        piece_code = Piece.EMPTY
        move_code = MoveTypes.NORMAL
        start_tile = -1
        end_tile = -1

        # Find colour
        if Move.is_symbol_turn(move_str, is_white_turn) is True:
            piece_code |= Piece.WHITE if is_white_turn else Piece.BLACK

        # Find piece type
        if move_str[0].lower() in PIECE_SYMBOLS:
            piece_code |= Piece.find_piece_from_symbol(move_str[0].lower())
        else:
            piece_code |= Piece.PAWN

        if move_str[1] in TILE_NAMES:
            start_tile = board.get_tile_from_piece(piece_code, col=move_str[1])


        for i, ch in enumerate(move_str[1:]):
            move_code, is_action = Move.check_symbol_for_action(move_code, ch)
            if is_action is False:
                if ch in TILE_NUMBERS:
                    if start_tile == -1:
                        start_tile = board.find_tile_from_str(row=ch, col=move_str[i])
                    end_tile = board.find_tile_from_str(row=ch, col=move_str[i])
                # We can have a piece symbol only in the very first pos.
                elif ch not in (TILE_NUMBERS + TILE_NAMES):
                    raise WRONG_INPUT(move_str)
        

        return Move(piece_code, start_tile, end_tile, move_code, move_str)

    @staticmethod
    def check_symbol_for_action(move_code, ch):
        """Check if the symbol corrisponds to an action."""        
        if ch == 'x':
            return Move.add_action(move_code, MoveTypes.TAKES), True
        elif ch == '+':
            return Move.add_action(move_code, MoveTypes.CHECK), True
        elif ch == '#':
            return Move.add_action(move_code, MoveTypes.CHECKMATE), True
        return move_code, False


    def add_action(move_code, move_action) -> int:
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
