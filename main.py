"""The game class."""
from chess.game import Game
from chess.move import Move

if __name__ == "__main__":

    # g = Game()
    g = Game(no_visuals=True)
    move = Move.decode_to_move("Raxd1", g.board, g.is_white_turn)
    print('\n')
    print(move)
    move = Move.decode_to_move("Ngg3", g.board, g.is_white_turn)
    print('\n')
    print(move)
    move = Move.decode_to_move("e4xf4+", g.board, g.is_white_turn)
    print('\n')
    print(move)
    move = Move.decode_to_move("Ne2e6", g.board, g.is_white_turn)
    print('\n')
    print(move)