"""uuid: A unique undentifier."""
from uuid import uuid4
from uuid import UUID
from typing import List, Tuple, Optional, Set

from chess.board import Board, BoardUtils
from datetime import datetime
from chess.pieces.piece import Piece
from chess.pieces.pawn import Pawn
from chess.pieces.king import King, CastleSide
from chess.move import Move, MoveDecoder
from chess.frontend.visuals import GameVisuals


STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
PROM_FEN = "3q1rk1/rPpb1ppp/p2bpn2/8/P3P3/4BN2/2p1QPPP/RN3RK1 w - 0 1"
STARTING_FEN = "rnbqk2r/ppp2ppp/3bpn2/3p4/3P4/3BPN2/PPP2PPP/RNBQK2R w KQkq - 0 1"
# STARTING_FEN = "rn1qkbnr/pb1pp1pp/1pp5/8/3P1p2/N1P1P3/PPQ2PPP/R1B1KBNR b"
# STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"


class Game:
    """Basically the main controller for game visuals and game logic."""

    def __init__(self, debug: bool = False, player1: str = "PC", player2: str = "PC", visuals: bool = True):
        """Construct."""
        self.id: UUID = uuid4()
        self.time_created = datetime.now()
        self.debug: bool = debug
        self.player1 = player1
        self.player2 = player2
        self.board: Board = Board(STARTING_FEN)
        self.is_white_turn: bool = self.board.colour_to_move == Piece.WHITE
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
            start_coords, end_coords = MoveDecoder.parse_coords(input_str)

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
            Starting coords of the move.
        end_coords : int
            Ending coords of the move.

        Returns
        -------
        bool
            Whether or not the move is valid.
        """
        piece = self.board.get_piece(start_coords)
        if piece == Piece.EMPTY:
            return False

        all_possible_coords = self.get_piece_possible_coords(piece, start_coords)

        # Remove the illegal moves
        all_possible_coords -= self.get_piece_illegal_coords(piece, all_possible_coords)

        # print("Is white king in check: ", self.board.kings[0].in_check(self.board.b_pieces, self.board.state))
        # moves = Piece.get_moveset(start_tile, piece_code)

        # possible_moves = Move.remove_off_bounds_tiles(moves)

        print(f"{piece.symbol}: {start_coords} --> {end_coords}")
        # print(f"moves: {moves}")

        return end_coords in all_possible_coords

    # NOTE: Why not just call get_piece_possible_coords for each piece???
    def get_all_possible_moves(self) -> List[Tuple[int, int]]:
        """Get all the possible moves."""
        # colors_turn = Piece.WHITE if  else Piece.BLACK
        moves = []
        for piece_code, piece_list in self.board.all_pieces[self.board.colour_to_move].items():
            for piece in piece_list:
                coords_set = set()
                coords_set = coords_set | piece.get_possible_coords(self.board.state)
                # if isinstance(piece, King):
                #     if castling_moves := piece.get_castling_coords(self.board):
                #         coords_set = coords_set | castling_moves
                # if isinstance(piece, Pawn) and self.board.last_piece_moved is not None:
                #     if en_passant_move := piece.get_en_passant_coords(self.board.last_piece_moved, self.board.en_passant_coords):
                #         if en_passant_move is not None:
                #             coords_set = coords_set | en_passant_move
                coords_set = coords_set - self.get_piece_illegal_coords(piece, coords_set)
                moves.append((piece.coords, coords_set))
        return moves

    def get_last_played_move(self) -> Optional[Move]:
        """Get the last played move."""
        return self.moves_history[-1] if len(self.moves_history) == 0 else None

    # NOTE: Add en passant.
    def get_piece_possible_coords(self, piece, start_coords: Tuple[int, int]) -> Set[Tuple[int, int]]:
        """Get all the possible coords."""
        coords_set = piece.get_possible_coords(self.board.state)
        if isinstance(piece, King):
            if castling_moves := piece.get_castling_coords(self.board):
                coords_set = coords_set | castling_moves
        if isinstance(piece, Pawn) and self.board.last_piece_moved is not None:
            if en_passant_move := piece.get_en_passant_coords(self.board.last_piece_moved, self.board.en_passant_coords):
                if en_passant_move is not None:
                    coords_set = coords_set | en_passant_move
        return coords_set

    def get_last_piece_moved(self) -> Optional[Piece]:
        """Get the last piece moved."""
        if len(self.moves_history) > 0:
            return self.board.get_piece(self.board.state[self.get_last_played_move().end_coords])
        return None

    def is_last_piece_same_color(self, piece):
        """Whether or not the last piece played is the same color as the given piece."""
        return self.get_last_piece_moved().color == piece.color

    def get_piece_illegal_coords(self, piece, coords_set) -> set:
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
        moving_piece: Piece = self.board.get_piece(start_coords)
        taken_piece: Piece = self.board.get_piece(end_coords)

        # NOTE Make it possible so the Pawn can transform here.

        castling_info = self.__update_board(start_coords, end_coords, moving_piece, taken_piece)
        # Reveal board state.
        if self.visuals is False:
            self.board.correct_format_print()
        else:
            print(self.board)

        # Change the turn.
        self.is_white_turn = self.board.colour_to_move == Piece.WHITE

        # Last move new fen is no the new old fen.
        old_fen = self.board.fen if len(self.moves_history) == 0 else self.moves_history[-1].new_fen
        move = Move(len(self.moves_history), start_coords, end_coords, castling_info, old_fen, new_fen=self.board.fen)
        self.moves_history.append(move)
        return move

    def __update_board(self, old_coords, new_coords, moving_piece, taken_piece):
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
        Dict[List[int], List[int]]
            If the moving piece is a King and the move was castling, return the castling info.
        """
        self.board.try_updating_castling(moving_piece)
        # Change the colour that has to move next.
        self.board.colour_to_move = BoardUtils.swap_colours(self.board.colour_to_move)

        if moving_piece.ptype == Piece.PAWN:
            if abs(old_coords[0] - new_coords[0]) > 1:
                row_skipped = new_coords[0] + (1 if moving_piece.color == Piece.WHITE else -1)
                self.board.en_passant_coords = (row_skipped, new_coords[1])
            else:
                self.board.en_passant_coords = None
            if moving_piece.is_transforming():
                ...
            # self.board.transform_pawn_to(moving_pawn, piece_code)

        # Was the move a castling move?
        castling_side = None
        castling_info = None
        if isinstance(moving_piece, King) and moving_piece.times_moved == 0:
            if castling_side := King.castling_side(new_coords):
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
        self.board.fen = self.board.get_fen()
        self.board.last_piece_moved = moving_piece
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
