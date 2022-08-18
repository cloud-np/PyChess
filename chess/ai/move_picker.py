import random


def random_legal_move(game):
    """Get a random legal move from the board state."""
    moves = game.get_all_possible_moves()
    random.shuffle(moves)
    for r_piece_moves in moves:
        if len(r_piece_moves[1]) > 0:
            # Note that there is not a optimal way to get a random el from a set.
            end_coords = random.choice(list(r_piece_moves[1]))
            return r_piece_moves[0], end_coords
    return None
