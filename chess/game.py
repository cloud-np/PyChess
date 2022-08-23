"""uuid: A unique undentifier."""
from uuid import uuid4
from uuid import UUID
from typing import List, Tuple, Optional, Set

from chess.board import Board, BoardUtils, BoardStateList, Fen
from datetime import datetime
from chess.pieces.piece import Piece, CastleSide
from chess.move import Move, MoveDecoder
from chess.frontend.visuals import GameVisuals


STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
# PROM_FEN = "3q1rk1/rPpb1ppp/p2bpn2/8/P3P3/4BN2/2p1QPPP/RN3RK1 w - 0 1"
STARTING_FEN = "rnbqk2r/ppp2ppp/3bpn2/3p4/3P4/3BPN2/PPP2PPP/RNBQK2R w KQkq - 0 1"
# Castling
# STARTING_FEN = "r3k2r/pppbqppp/n2bpn2/3p4/3P4/2NBPN2/PPPBQPPP/R3K2R w KQkq - 0 1"
# STARTING_FEN = "r1b1k2r/ppp2ppp/nb1qpn2/2Qp4/3P4/3BPN2/PPP2PPP/RNB1R1K1 b kq - 0 1"
STARTING_FEN = "rn1qkbnr/pb1pp1pp/1pp5/8/3P1p2/N1P1P3/PPQ2PPP/R1B1KBNR b - - 0 1"
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
                # Reveal board state.
                self.board.correct_format_print()
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
        piece_code: int = Board.get_piece(self.board.state, start_coords)
        if piece_code == Piece.EMPTY:
            return False

        all_possible_coords = Game.get_piece_possible_coords(self.board.state, self.board.all_pieces, self.board.castle_rights, self.board.en_passant, piece_code, start_coords)

        # Remove the illegal moves
        all_possible_coords -= Game.get_piece_illegal_coords(self.board.state, self.board.all_pieces, self.board.en_passant, start_coords, piece_code, all_possible_coords)

        # print("Is white king in check: ", self.board.kings[0].in_check(self.board.b_pieces, self.board.state))
        # moves = Piece.get_moveset(start_tile, piece_code)

        # possible_moves = Move.remove_off_bounds_tiles(moves)

        print(f"{Piece.get_symbol(piece_code)}: {start_coords} --> {end_coords}")
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
                coords_set = coords_set - Game.get_piece_illegal_coords(piece, coords_set)
                moves.append((piece.coords, coords_set))
        return moves

    def get_last_played_move(self) -> Optional[Move]:
        """Get the last played move."""
        return self.moves_history[-1] if len(self.moves_history) == 0 else None

    # NOTE: Add en passant.
    @staticmethod
    def get_piece_possible_coords(board_state: BoardStateList, all_pieces, castle_rights, en_passant, piece_code: int, start_coords: Tuple[int, int]) -> Set[Tuple[int, int]]:
        """Get all the possible coords."""
        coords_set = Piece.get_possible_coords(board_state, (piece_code, start_coords), en_passant)
        if Piece.get_type(piece_code) == Piece.KING:
            if castling_moves := Game.get_castling_coords(piece_code, board_state, castle_rights, all_pieces):
                coords_set = coords_set | castling_moves
        # if isinstance(piece_code, Pawn) and self.board.last_piece_moved is not None:
        #     if en_passant_move := piece_code.get_en_passant_coords(self.board.last_piece_moved, self.board.en_passant_coords):
        #         if en_passant_move is not None:
        #             coords_set = coords_set | en_passant_move
        return coords_set

    @staticmethod
    def get_castling_coords(piece_code: int, board_state, castle_rights, all_pieces) -> Set[Tuple[int, int]]:
        """Try adding the roke moves if they are valid."""
        castle_coords = set()

        pcolor = Piece.get_color(piece_code)
        enemy_pieces = all_pieces[Piece.get_enemy_color(piece_code)]
        # Right castle
        if castle_rights[pcolor][1]:
            rcastle: List[Tuple[int, int]] = Piece.get_castle_coords(piece_code, Piece.RIGHT_PIECE)
            if rcastle and not Board.are_coords_under_attack(board_state, rcastle, enemy_pieces) and Board.are_coords_empty(board_state, rcastle):
                castle_coords.add((7, 6) if pcolor == Piece.WHITE else (0, 6))

        # Left castle
        if castle_rights[pcolor][0]:
            lcastle: List[Tuple[int, int]] = Piece.get_castle_coords(piece_code, Piece.LEFT_PIECE)
            if lcastle and not Board.are_coords_under_attack(board_state, lcastle, enemy_pieces) and Board.are_coords_empty(board_state, lcastle):
                castle_coords.add((7, 2) if pcolor == Piece.WHITE else (0, 2))
        return castle_coords

    def get_last_piece_moved(self) -> Optional[Piece]:
        """Get the last piece moved."""
        if len(self.moves_history) > 0:
            return self.board.get_piece(self.board.state[self.get_last_played_move().end_coords])
        return None

    @staticmethod
    def get_last_fen(move: Optional[Move]) -> str:
        return move.fen

    def is_last_piece_same_color(self, piece):
        """Whether or not the last piece played is the same color as the given piece."""
        return self.get_last_piece_moved().color == piece.color

    @staticmethod
    def get_piece_illegal_coords(board_state: BoardStateList, all_pieces, en_passant: Tuple[int, int], start_coords: Tuple[int, int], piece_code: int, coords_set) -> set:
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
        sim_state = Board.simulate_board_state(board_state)
        illegal_coords = set()

        @Game.simulate_move
        def __play_possibly_illegal_move(sim_state, all_pieces, start_coords, end_coords):
            is_king_in_check = Piece.is_king_in_check(sim_state, all_pieces, en_passant, piece_code)
            if is_king_in_check:
                illegal_coords.add(end_coords)

        for c in coords_set:
            __play_possibly_illegal_move(sim_state, all_pieces, start_coords, c)
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
        def __sim_seq(state, all_pieces, piece_code, start_coords, end_coords):
            all_pieces[Piece.get_color(piece_code)][Piece.get_type(piece_code)][piece_code] = end_coords
            state[end_coords] = piece_code
            state[start_coords] = Piece.EMPTY

        def __simulate_move(state, all_pieces, start_coords: tuple, end_coords: tuple) -> None:
            piece_code = state[start_coords]
            __sim_seq(state, all_pieces, piece_code, start_coords=start_coords, end_coords=end_coords)
            func(state, all_pieces, start_coords, end_coords)
            # Simpliest thing to do simulate back what you simulated above.
            __sim_seq(state, all_pieces, piece_code, end_coords=start_coords, start_coords=end_coords)
        return __simulate_move

    # def simulate_move(self, sim_state, start_coords: int, end_coords: int, piece: Piece) -> None:
    #     piece.set_coords(end_coords)
    #     sim_state[end_coords] = piece.piece_code
    #     sim_state[start_coords] = Piece.EMPTY

    def is_piece_turn(self, start_coords):
        return Piece.get_color(self.board.state[start_coords]) == self.board.color_to_move

    def is_player_move_valid(self, start_coords: int, end_coords: int) -> bool:
        """Check if the player move is valid."""
        if self.is_piece_turn(start_coords):
            return self.is_move_valid(start_coords, end_coords)
        return False

    def register_move(self, start_coords: Tuple[int, int], end_coords: Tuple[int, int]) -> Move:
        """Register the a move.

        Find the Piece objs on the given coords and change their attr accordantly.
        Parameters
        ----------
        start_coords : tuple
            The old coords of the piece.
        end_coords : tuple
            The new coords of the piece.
        """
        # NOTE Make it possible so the Pawn can transform here.
        castle_side: Optional[CastleSide]

        moving_piece, castle_side, en_passant = Game.update_board(self.board.state, self.board.all_pieces, self.board.castle_rights, self.board.en_passant, start_coords, end_coords)
        self.board.en_passant = en_passant
        self.board.color_to_move = BoardUtils.swap_colors(self.board.color_to_move)

        # Change the turn.
        # self.is_white_turn = self.board.color_to_move == Piece.WHITE

        # Last move new fen is no the new old fen.
        old_fen = self.board.fen if len(self.moves_history) == 0 else self.moves_history[-1].curr_fen
        # curr_fen = Fen.create_fen(self.board.state, Piece.get_color(moving_piece), self.board.castle_rights)
        curr_fen = Fen.create_fen(self.board.state, Piece.get_color(moving_piece), self.board.castle_rights)
        move = Move(len(self.moves_history), moving_piece, start_coords, end_coords, castle_side, old_fen, curr_fen)
        self.moves_history.append(move)
        return move

    @staticmethod
    def update_board(board_state: BoardStateList, all_pieces, castle_rights, en_passant_coords: Tuple[int, int], old_coords: Tuple[int, int], new_coords: Tuple[int, int]):
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
        # board.try_updating_castling(moving_piece)
        # Change the colour that has to move next.
        moving_piece = board_state[old_coords]
        Board.try_update_castle_rights(castle_rights, moving_piece)

        if Piece.get_type(moving_piece) == Piece.PAWN:
            # Piece.pawn_attack_moves(board_state, (moving_piece, old_coords))
            if abs(old_coords[0] - new_coords[0]) > 1:
                row_skipped = new_coords[0] + (1 if Piece.get_color(moving_piece) == Piece.WHITE else -1)
                en_passant_coords = (row_skipped, new_coords[1])
            else:
                en_passant_coords = None
            # if moving_piece.is_transforming():
            #     ...
        # self.board.transform_pawn_to(moving_pawn, piece_code)

        # Was the move a castling move?
        castle_side = None
        ptype = Piece.get_type(moving_piece)
        if ptype == Piece.KING:
            # Try to get the castling side if it returns None then no castling move was made.
            castle_side = CastleSide.get_side(new_coords)
            if castle_side is not None:
                Game.__update_rook_castle_pos(board_state, castle_side)

        # Update pieces
        # moving_piece.set_coords(new_coords)
        # # moving_piece.times_moved += 1
        # if isinstance(taken_piece, Piece):
        #     self.board.kill_piece(taken_piece)
        #     # NOTE: This needs to look into
        #     taken_piece.set_coords((-1, -1))

        # Update board state.
        board_state[new_coords] = board_state[old_coords]
        board_state[old_coords] = Piece.EMPTY
        # Update piece_lists
        all_pieces[Piece.get_color(moving_piece)][ptype][moving_piece] = new_coords
        return moving_piece, castle_side, en_passant_coords

    @staticmethod
    def __update_rook_castle_pos(board_state: BoardStateList, castle_side: int) -> None:
        """Update the rook's position based on the castling side.

        Parameters
        ----------
        castling_side : int
            Change the board state based on the castling side.
        """
        new_rook_coords, rook_coords = CastleSide.get_rook_posistions(castle_side)
        # Change the coords of the rook and the board state.
        board_state[new_rook_coords] = board_state[rook_coords]
        board_state[rook_coords] = Piece.EMPTY

    def is_piece_pickable(self, piece_code: int) -> bool:
        """Determine if you can pick a piece.

        If the piece is on the same colour as the player
        who is turn to play then the pick is pickable.
        """
        return Piece.get_color(piece_code) == self.board.color_to_move
