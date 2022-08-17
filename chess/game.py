"""uuid: A unique undentifier."""
from uuid import uuid4
from uuid import UUID
from typing import Dict, List

from chess.board import Board
from datetime import datetime
from chess.pieces.piece import Piece
from chess.pieces.king import King, CastleSide
from chess.pieces.rook import Rook, RookCorner
from chess.move import Move
from chess.frontend.visuals import GameVisuals


STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
STARTING_FEN = "rn1qkbnr/pb1pp1pp/1pp5/8/3P1p2/N1P1P3/PPQ2PPP/R1B1KBNR"
# STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"


class Game:
    """Basically the main controller for game visuals and game logic."""

    def __init__(self, debug: bool = False, player1: str = "PC", player2: str = "PC", visuals: bool = True):
        """Construct."""
        self.id: UUID = uuid4()
        self.time_created = datetime.now()
        self.debug: bool = debug
        self.is_white_turn: bool = True
        self.player1 = player1
        self.player2 = player2
        self.board: Board = Board(STARTING_FEN)
        self.running: bool = True
        # self.moves_history:
        self.visuals: bool = visuals
        self.moves_history: list = []
        self.player1_color = Piece.WHITE
        self.player2_color = Piece.BLACK
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

        all_possible_coords = self.get_piece_possible_coords(piece, start_coords)

        # Remove the illegal moves
        all_possible_coords = all_possible_coords - self.get_illegal_coords(piece, all_possible_coords)

        # print("Is white king in check: ", self.board.kings[0].in_check(self.board.b_pieces, self.board.state))
        # moves = Piece.get_moveset(start_tile, piece_code)

        # possible_moves = Move.remove_off_bounds_tiles(moves)

        print(f"{piece.symbol}: {start_coords} --> {end_coords}")
        # print(f"moves: {moves}")

        return end_coords in all_possible_coords

    def get_all_possible_moves(self) -> set:
        """Get all the possible moves."""
        # print('MOVED PIECE: ', piece)
        colors_turn = Piece.WHITE if self.is_white_turn else Piece.BLACK
        moves = []
        for piece_code, piece_list in self.board.all_pieces[colors_turn].items():
            for piece in piece_list:
                coords_set = set()
                coords_set = coords_set | piece.get_possible_coords(self.board.state)

                if isinstance(piece, King):
                    castling_moves = piece.get_castling_coords(self.board)
                    if castling_moves:
                        coords_set = coords_set | castling_moves
                coords_set = coords_set - self.get_illegal_coords(piece, coords_set)
                moves.append((piece.coords, coords_set))
        return moves

    # NOTE: Add en passant.
    def get_piece_possible_coords(self, piece, start_coords) -> set:
        """Get all the possible coords."""
        # print('MOVED PIECE: ', piece)
        coords_set = piece.get_possible_coords(self.board.state)

        if isinstance(piece, King):
            castling_moves = piece.get_castling_coords(self.board)
            if castling_moves:
                coords_set = coords_set | castling_moves
        return coords_set

    def get_illegal_coords(self, piece, coords_set) -> set:
        """Get the illegal coords.

        Parameters
        ----------
        piece : Piece
            The moving piece.
        start_coords : tuple(int)
            His starting pos.
        coords_set : set
            The possible coords.

        Returns
        -------
        set
            All the illegal moves
        """
        # For each simulated move, if the king is in check, then the move is invalid.
        sim_state = self.board.simulated_board_state()
        illegal_coords = set()
        king = self.board.kings[piece.color]
        enemy_pieces = self.board.all_pieces[piece.enemy_color]

        @Game.simulate_move
        def __play_possibly_illegal_move(sim_state, start_coords, end_coords, piece):
            is_king_in_check = king.in_check(enemy_pieces, sim_state)
            if is_king_in_check:
                illegal_coords.add(end_coords)

        for crd in coords_set:
            __play_possibly_illegal_move(sim_state, start_coords=piece.coords, end_coords=crd, piece=piece)
        return illegal_coords

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
        is_piece_white = self.board.get_piece(start_coords).color == Piece.WHITE
        if is_piece_white != self.is_white_turn:
            return False
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

    def register_move(self, start_coords: tuple, end_coords: tuple):
        """Register the a move.

        Find the Piece objs on the given coords and change their attr accordantly.
        Parameters
        ----------
        start_coords : tuple
            The old coords of the piece.
        end_coords : tuple
            The new coords of the piece.
        """
        moving_piece = self.board.get_piece(start_coords)
        taken_piece = self.board.get_piece(end_coords)
        castling_info = self.__update_board(start_coords, end_coords, moving_piece, taken_piece)

        if self.visuals is False:
            self.board.correct_format_print()
        else:
            print(self.board)

        move = Move(len(self.moves_history), start_coords=start_coords, end_coords=end_coords, moving_piece=moving_piece, taken_piece=taken_piece, castling_info=castling_info)
        self.moves_history.append(move)

        # Change the turn.
        self.is_white_turn = not self.is_white_turn
        return move

    def __try_removing_castling(self, moving_piece):
        """Remove castling privileges depending the moving piece."""
        if isinstance(moving_piece, King):
            moving_piece.has_moved = True
        if isinstance(moving_piece, Rook):
            moving_piece.has_moved = True
            if moving_piece.rook_corner in (RookCorner.BOTTOM_RIGHT, RookCorner.TOP_RIGHT):
                self.board.kings[moving_piece.color].r_castle['is_valid'] = False
            if moving_piece.rook_corner in (RookCorner.BOTTOM_LEFT, RookCorner.TOP_LEFT):
                self.board.kings[moving_piece.color].l_castle['is_valid'] = False

    def __update_board(self, old_coords, new_coords, moving_piece, taken_piece) -> Dict[List[int], List[int]]:
        """Update the board state and pieces.

        Parameters
        ----------
        old_coords : tuple[int]
            Holds the starting coords of the piece.
        new_coords : tuple[int]
            Holds the ending coords of the piece.
        moving_piece : Piece
            The Piece that is moving from the old coords to the new coords.
        taken_piece : Piece
            The Piece that is getting killed (if there is any) from the new coords.

        Returns
        -------
        dict
            If the moving piece is a King and the move was castling, return the castling info.
        """
        self.__try_removing_castling(moving_piece)

        # Was the move a castling move?
        castling_side = None
        castling_info = None
        if isinstance(moving_piece, King) and moving_piece.times_moved == 0:
            castling_side = King.castling_side(new_coords)
            if castling_side is not None:
                new_rook_coords, rook_coords = self.__update_rooks_castle_pos(castling_side)
                castling_info = {'rook_coords': rook_coords, 'new_rook_coords': new_rook_coords}

        # Update pieces
        moving_piece.set_coords(new_coords)
        moving_piece.times_moved += 1
        if isinstance(taken_piece, Piece):
            self.board.kill_piece(taken_piece)
            # NOTE: This needs to look into
            taken_piece.set_coords((-1, -1))

        # Update board state.
        self.board.state[new_coords] = self.board.state[old_coords]
        self.board.state[old_coords] = Piece.EMPTY
        return castling_info

    def get_castling_rook_positions(self, castling_side: int) -> tuple:
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
        new_rook_coords, rook_coords = self.get_castling_rook_positions(castling_side)
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
