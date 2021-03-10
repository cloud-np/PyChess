"""bitarray: efficient arrays of booleans."""
from bitarray import bitarray
BOARD_SIZE = 64 

class Board:
    """The way we represent our Board is with bitarrays."""
    
    def __init__(self):
        """Construct all the necessary attributes for the board object."""    
        self.white_pieces = BOARD_SIZE * bitarray('0')
        self.black_pieces = BOARD_SIZE * bitarray('0')
