"""uuid: A unique undentifier."""
from uuid import uuid4
from uuid import UUID

from chess.board import Board
from datetime import datetime
from chess.pieces.piece import Piece
from chess.pieces.king import King, CastleSide
from chess.move import Move
from chess.frontend.visuals import GameVisuals


# STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
# BOARD_SIZE = 64
# VISUAL_BOARD_SIZE = 64


class Game:
    """Basically the main controller for game visuals and game logic."""

    def __init__(self, debug: bool = False, player1: str = "PC", player2: str = "PC", visuals: bool = True):
        """Construct."""
        self.id: UUID = uuid4()
        self.time_created = datetime.now()
        self.debug: bool = debug
        self.is_white_turn: bool = True
        self.board: Board = Board(STARTING_FEN)
        self.running: bool = True
        # self.moves_history:
        self.visuals: bool = visuals
        if visuals:
            GameVisuals(self, self.board.state).main_loop()
        self.cli_loop()

    def cli_loop(self):
        """Loop for the CLI."""
        while self.running:
            # Get the input.
            input_str = input("Enter the start and end coords: ")
            start_coords, end_coords = Move.parse_coords(input_str)

            # Check if the move is valid.
            # if self.is_player_move_valid(start_coords, end_coords):
            if self.is_move_valid(start_coords, end_coords):
                self.register_move(start_coords, end_coords)
            else:
                print("Invalid move.")

            # Check if the game is over.
            # if self.is_game_over():
            #     self.running = False

    def __str__(self) -> str:
        """Represent the current game and its info."""
        return (
            f"Created: " f"{self.time_created.strftime('%d/%m/%Y %H:%M:%S')} {self.id}"
        )

    def is_move_valid(self, start_coords: int, end_coords: int) -> bool:
        """Check if move is valid.

        Parameters
        ----------
        start_coords : int
            [description]
        end_coords : int
            [description]

        Returns
        -------
        bool
            [description]
        """
        piece = self.board.get_piece(start_coords)
        if piece == Piece.EMPTY:
            return False

        moves = piece.get_moves(self.board.state)

        # Get the castling moves if the playing piece was a King.
        if isinstance(piece, King):
            moves = moves | piece.get_caslting_moves(self.board)

        # Remove the illegal moves
        moves = moves - self.get_illegal_moves(piece, start_coords, moves)

        # print("Is white king in check: ", self.board.kings[0].in_check(self.board.b_pieces, self.board.state))
        # moves = Piece.get_moveset(start_tile, piece_code)

        # possible_moves = Move.remove_off_bounds_tiles(moves)

        print(f"{piece.symbol}: {start_coords} --> {end_coords}")
        # print(f"moves: {moves}")

        return end_coords in moves

    # NOTE: Add en passant.
    def get_all_moves(self, piece, start_coords):
        """Get all the possible moves."""
        # print('MOVED PIECE: ', piece)
        moves = piece.get_moves(self.board.state)

        if isinstance(piece, King):
            castling_moves = piece.get_caslting_moves(self.board)
            if castling_moves:
                moves = moves | castling_moves
        return moves

    def get_illegal_moves(self, piece, start_coords, moves) -> set:
        """Get the illegal moves.

        Parameters
        ----------
        piece : Piece
            The moving piece.
        start_coords : tuple(int)
            His starting pos.
        moves : set
            The possible moves.

        Returns
        -------
        set
            All the illegal moves
        """
        # For each simulated move, if the king is in check, then the move is invalid.
        sim_state = self.board.simulated_board_state()
        illegal_moves = set()
        king = self.board.kings[piece.color]
        enemy_pieces = self.board.all_pieces[piece.enemy_color]

        @Game.simulate_move
        def __play_possibly_illegal_move(sim_state, start_coords, end_coords, piece):
            is_king_in_check = king.in_check(enemy_pieces, sim_state)
            if is_king_in_check:
                illegal_moves.add(end_coords)

        for move in moves:
            __play_possibly_illegal_move(sim_state, start_coords=start_coords, end_coords=move, piece=piece)
        return illegal_moves

    @staticmethod
    def simulate_move(func):
        """Simulate a move decorator.

        If a given functions changes the board state by playing a move,
        simple revert to its original state before the move.
        Parameters
        ----------
        func : function
            The function that should changes a board state.
        """
        def __sim_seq(sim_state, start_coords, end_coords, piece):
            piece.set_coords(end_coords)
            sim_state[end_coords] = piece.piece_code
            sim_state[start_coords] = Piece.EMPTY

        def __simulate_move(sim_state, start_coords: tuple, end_coords: tuple, piece: Piece) -> None:
            __sim_seq(sim_state, piece=piece, start_coords=start_coords, end_coords=end_coords)
            func(sim_state, start_coords, end_coords, piece)
            # Simpliest thing to do simulate back what you simulated above.
            __sim_seq(sim_state, piece=piece, end_coords=start_coords, start_coords=end_coords)
        return __simulate_move

    # def simulate_move(self, sim_state, start_coords: int, end_coords: int, piece: Piece) -> None:
    #     piece.set_coords(end_coords)
    #     sim_state[end_coords] = piece.piece_code
    #     sim_state[start_coords] = Piece.EMPTY

    def is_player_move_valid(self, start_coords: int, end_coords: int) -> bool:
        """Check if the player move is valid."""
        return self.is_move_valid(start_coords, end_coords)
    #     """Return whether or not the player move is valid.

    #     We take for granted that the given input is correct and the
    #     starting tile does have the correct piece code.

    #     Parameters
    #     ----------
    #     start_tile : int
    #         Starting coords of the piece.
    #     end_tile : int
    #         Ending coords of the piece.

    #     Returns
    #     -------
    #     bool
    #         Returns whether or not a move is valid.
    #     """
    #     piece = self.board.get_piece(start_coords)
    #     if piece == Piece.EMPTY:
    #         return False
    #     moves = piece.get_moves(self.board.state)
    #     # For each simulated move, if the king is in check, then the move is invalid.

    #     # sim_state = self.board.simulated_board_state()
    #     # sim_state[end_coords] = sim_state[start_coords]
    #     # for move in moves:
    #     #     sim_state = self.board.simulated_board_state()
    #     #     sim_state_copy = sim_state.copy()
    #     # print(self.board.w_king[0].in_check(self.board.b_pieces, self.board.state))
    #     # moves = Piece.get_moveset(start_tile, piece_code)

    #     # possible_moves = Move.remove_off_bounds_tiles(moves)

    #     print(f"{piece.symbol}: {start_coords} --> {end_coords}")
    #     print(f"moves: {moves}")
    #     return end_coords in moves

    def register_move(self, old_coords: tuple, new_coords: tuple):
        """Register the a move.

        Find the Piece objs on the given coords and change their attr accordantly.


        Parameters
        ----------
        old_coords : tuple
            The old coords of the piece.
        new_coords : tuple
            The new coords of the piece.
        """
        # Update pieces.
        moving_piece = self.board.get_piece(old_coords)
        taken_piece = self.board.get_piece(new_coords)

        castling_side = None
        castling_info = None
        if isinstance(moving_piece, King):
            castling_side = King.castling_side(new_coords)
            new_rook_coords, rook_coords = self.__update_rooks_castle_pos(castling_side)
            castling_info = {'rook_coords': rook_coords, 'new_rook_coords': new_rook_coords}

        # Update pieces
        moving_piece.set_coords(new_coords)
        if isinstance(taken_piece, Piece):
            self.board.kill_piece(taken_piece)
            # NOTE: This needs to look into
            taken_piece.set_coords((-1, -1))

        # Update board state.
        self.board.state[new_coords] = self.board.state[old_coords]
        self.board.state[old_coords] = Piece.EMPTY

        self.is_white_turn = not self.is_white_turn

        if self.visuals is False:
            self.board.correct_format_print()
        else:
            print(self.board)
        return castling_info

    def get_caslting_rook_positions(self, castling_side: int) -> tuple:
        """Return the positions of the rooks involved in a castling."""
        if castling_side == CastleSide.WK_SIDE_R:
            rook_castle_coords = (7, 5)
            rook_coords = (7, 7)
        elif castling_side == CastleSide.WK_SIDE_L:
            rook_castle_coords = (7, 3)
            rook_coords = (7, 0)
        elif castling_side == CastleSide.BK_SIDE_R:
            rook_castle_coords = (0, 5)
            rook_coords = (0, 7)
        elif castling_side == CastleSide.BK_SIDE_L:
            rook_castle_coords = (0, 3)
            rook_coords = (0, 0)
        else:
            raise ValueError("Invalid castling side.")
        return rook_castle_coords, rook_coords

    def __update_rooks_castle_pos(self, castling_side: int):
        """Update the rook's position based on the castling side.

        Parameters
        ----------
        castling_side : int
            Change the board state based on the castling side.
        """
        new_rook_coords, rook_coords = self.get_caslting_rook_positions(castling_side)
        # Change the coords of the rook and the board state.
        self.board.get_piece(rook_coords).set_coords(new_rook_coords)
        self.board.state[new_rook_coords] = self.board.state[rook_coords]
        self.board.state[rook_coords] = Piece.EMPTY
        return new_rook_coords, rook_coords

    def is_piece_pickable(self, piece) -> bool:
        """Determine if you can pick a piece.

        If the piece is on the same colour as the player
        who is turn to play then the pick is pickable.
        """
        # return isinstance(piece, Piece) and piece.is_white == self.is_white_turn
        return True
