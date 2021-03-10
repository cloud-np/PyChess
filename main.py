"""The game class."""
from chess.game import Game
from chess.piece import Piece

if __name__ == "__main__":

    black_knight = Piece.BLACK + Piece.KNIGHT
    print(black_knight)
    g = Game()
    print(g.board.pieces)
    g.main_loop()