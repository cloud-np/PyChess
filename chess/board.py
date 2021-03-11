"""board module contains all the classes and methods which are needed for a chessboard to be functional."""
# from bitarray import bitarray
import numpy as np
BOARD_SIZE = 64 

class Board:
    """The way we represent our Board is with bitarrays."""
    
    def __init__(self):
        """Construct all the necessary attributes for the board object."""    
        self.pieces = np.zeros((BOARD_SIZE))
        # self.black_pieces = BOARD_SIZE * bitarray('0')
    
    # def show_white_pieces_pos():
    #     for
    # def __str__(self):

