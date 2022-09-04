"""uuid: A unique undentifier."""
from uuid import uuid4
import numpy as np
from uuid import UUID
from typing import List, Tuple, Optional, Set

from chess.board import Board, BoardUtils, Fen
from datetime import datetime
from chess.moves.movegenerator import MoveGenerator
from chess.pieces.piece import Piece, CastleSide
from chess.moves.move import Move, MoveDecoder
from chess.frontend.visuals import GameVisuals


STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
STARTING_FEN = "rnbqk2r/ppp2ppp/3bpn2/3p4/3P4/3BPN2/PPP2PPP/RNBQK2R w KQkq - 0 1"
# Promotion
# STARTING_FEN = "3q1rk1/rPpb1ppp/p2bpn2/8/P3P3/4BN2/2p1QPPP/RN3RK1 w - - 0 1"
# Castling
STARTING_FEN = "r3k2r/pppbqppp/n2bpn2/3p4/3P4/2NBPN2/PPPBQPPP/R3K2R w KQkq - 0 1"
# STARTING_FEN = "r1b1k2r/ppp2ppp/nb1qpn2/2Qp4/3P4/3BPN2/PPP2PPP/RNB1R1K1 b kq - 0 1"
# STARTING_FEN = "rn1qkbnr/pb1pp1pp/1pp5/8/3P1p2/N1P1P3/PPQ2PPP/R1B1KBNR b - - 0 1"
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
        self.movegen: MoveGenerator = MoveGenerator(self.board)
        self.visuals: bool = visuals
        self.moves_history: List[Move] = []
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
            if start_coords is None or end_coords is None:
                print("Invalid coords.")
                continue

            # Check if the move is valid.
            # if self.is_player_move_valid(start_coords, end_coords):
            if self.is_move_valid(start_coords, end_coords):
                # Game.is_promoting(self.board.state, start_coords, end_coords)
                if Board.is_promoting(self.board.state[start_coords], end_coords):
                    prom = input("Promote to: ")
                    prom_type = {
                        "q": Piece.QUEEN,
                        "r": Piece.ROOK,
                        "k": Piece.KNIGHT,
                        "b": Piece.BISHOP,
                    }[prom]
                    Board.promote_to(self.board.state, self.board.state[start_coords], prom_type)
                self.make_move(start_coords, end_coords)
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

    # @staticmethod
    # def is_promoting(state, start_coords: Tuple[int, int], end_coords: Tuple[int, int]) -> bool:
    #     return Board.is_promoting(state[start_coords], end_coords)

    def is_move_valid(self, start_coords: Tuple[int, int], end_coords: Tuple[int, int]) -> bool:
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
        piece: np.uint32 = self.board.state[start_coords]
        if piece == Piece.EMPTY:
            return False

        legal_piece_coords = self.get_legal_coords(start_coords)

        print(f"{Piece.get_symbol(piece)}: {start_coords} --> {end_coords}")
        # print(f"moves: {moves}")

        return end_coords in legal_piece_coords
    
    def get_legal_coords(self, start_coords):
        all_possible_coords = self.get_piece_possible_coords(start_coords)
        # Remove the illegal moves
        all_possible_coords -= self.get_piece_illegal_coords(start_coords, self.board.state[start_coords], all_possible_coords)
        return all_possible_coords

    def get_all_possible_moves(self) -> List[Tuple[int, Tuple[int, int]]]:
        """Get all the possible moves."""
        # colors_turn = Piece.WHITE if  else Piece.BLACK
        moves = []
        # for color in [Piece.WHITE, Piece.BLACK]:
        #     for _, piece_list in all_pieces[color].items():
        #         for piece, pstart_coords in piece_list.items():
        #             coords_set = set()
        #             coords_set = Game.get_legal_coords(state, castle_rights, en_passant, pstart_coords)
        #             moves.append((pstart_coords, coords_set))
        return moves

    def get_last_played_move(self) -> Optional[Move]:
        """Get the last played move."""
        return self.moves_history[-1] if len(self.moves_history) == 0 else None

    def get_piece_possible_coords(self, start_coords: Tuple[int, int]) -> Set[Tuple[int, int]]:
        """Get all the possible coords."""
        piece = self.board.state[start_coords]
        coords_set = self.movegen.get_possible_coords((piece, start_coords))
        if Piece.get_type(piece) == Piece.KING:
            if castling_moves := self.get_castling_coords(piece):
                coords_set = coords_set | castling_moves
        return coords_set

    # def generate_all_moves(self, depth: int) -> int:
    #     if depth == 0:
    #         return 1

    #     num_posistions = 0

    #     @Game.simulate_move
    #     def play_move(state, en_passant, start_coords, end_coords) -> None:
    #         # _, _, en_passant, _ = self.update_board(castle_rights, en_passant, 0, start_coords, end_coords)
    #         num_posistions += self.generate_all_moves(depth - 1)

    #     all_moves: List[Tuple[int, Tuple[int, int]]]
    #     all_moves = self.get_all_possible_moves()
    #     for start_coords, coords in all_moves:
    #         for crd in coords:
    #             play_move(state, start_coords, crd)

    #     return num_posistions

    def get_castling_coords(self, piece: np.uint32) -> Set[Tuple[int, int]]:
        """Try adding the roke moves if they are valid."""
        castle_coords = set()

        pcolor = Piece.get_color(piece)
        enemies = self.board.get_enemies(Piece.get_color(piece))
        # Right castle
        if self.board.castle_rights[pcolor][1]:
            rcastle: Optional[List[Tuple[int, int]]] = Piece.get_castle_coords(piece, Piece.RIGHT_PIECE)
            if rcastle and not self.movegen.are_coords_under_attack(rcastle, pcolor) and self.board.are_coords_empty(rcastle):
                castle_coords.add((7, 6) if pcolor == Piece.WHITE else (0, 6))

        # Left castle
        if self.board.castle_rights[pcolor][0]:
            lcastle: Optional[List[Tuple[int, int]]] = Piece.get_castle_coords(piece, Piece.LEFT_PIECE)
            if lcastle and not self.movegen.are_coords_under_attack(lcastle, pcolor) and self.board.are_coords_empty(lcastle):
                castle_coords.add((7, 2) if pcolor == Piece.WHITE else (0, 2))
        return castle_coords

    def get_piece_illegal_coords(self, start_coords: Tuple[int, int], piece: np.uint32, coords_set: Set[Tuple[int, int]]) -> Set[Tuple[int, int]]:
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
        sim_state = Board.simulate_state(self.board.state)
        pcolor = Piece.get_color(piece)
        enemies = self.board.get_enemies(pcolor)
        illegal_coords = set()

        @self.simulate_move
        def __play_possibly_illegal_move(start_coords, end_coords):
            is_king_in_check = self.movegen.is_king_in_check(enemies, self.board.get_king_coords(pcolor))
            if is_king_in_check:
                illegal_coords.add(end_coords)

        for crd in coords_set:
            __play_possibly_illegal_move(start_coords, crd)
        return illegal_coords

    def simulate_move(self, func):
        """Simulate a move decorator.

        If a given functions changes the board state by playing a move,
        simple revert to its original state before the move.
        Parameters
        ----------
        func : function
            The function that should changes a board state.
        """
        def __sim_seq(piece, start_coords, end_coords):
            self.board.state[end_coords] = piece
            self.board.state[start_coords] = Piece.EMPTY

        def __simulate_move(state, start_coords: tuple, end_coords: tuple) -> None:
            piece = state[start_coords]
            __sim_seq(piece, start_coords=start_coords, end_coords=end_coords)
            func(state, start_coords, end_coords)
            # Simpliest thing to do simulate back what you simulated above.
            __sim_seq(piece, start_coords=end_coords, end_coords=start_coords)
        return __simulate_move

    def is_piece_turn(self, start_coords):
        return Piece.get_color(self.board.state[start_coords]) == self.board.color_to_move

    def is_player_move_valid(self, start_coords: Tuple[int, int], end_coords: Tuple[int, int]) -> bool:
        """Check if the player move is valid."""
        if self.is_piece_turn(start_coords):
            return self.is_move_valid(start_coords, end_coords)
        return False

    def make_move(self, start_coords: Tuple[int, int], end_coords: Tuple[int, int]) -> Move:

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
        castle_side: Optional[int]
        moving_piece, castle_side = self.update_board(start_coords, end_coords)
        # Change the turn.
        self.board.color_to_move = BoardUtils.swap_colors(self.board.color_to_move)

        # Last move new fen is no the new old fen.
        old_fen = self.board.fen if len(self.moves_history) == 0 else self.moves_history[-1].curr_fen
        curr_fen = Fen.create_fen(self.board.state, Piece.get_color(moving_piece), self.board.castle_rights, self.board.en_passant, self.board.half_move_clock, self.board.full_move)
        move = Move(len(self.moves_history), moving_piece, start_coords, end_coords, castle_side, old_fen, curr_fen)
        self.moves_history.append(move)
        return move

    def unmake_move(self, start_coords: Tuple[int, int], end_coords: Tuple[int, int]) -> Move:

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
        castle_side: Optional[int]
        moving_piece, castle_side = self.update_board(start_coords, end_coords)
        # Change the turn.
        self.board.color_to_move = BoardUtils.swap_colors(self.board.color_to_move)

        # Last move new fen is no the new old fen.
        old_fen = self.board.fen if len(self.moves_history) == 0 else self.moves_history[-1].curr_fen
        curr_fen = Fen.create_fen(self.board.state, Piece.get_color(moving_piece), self.board.castle_rights, self.board.en_passant, self.board.half_move_clock, self.board.full_move)
        move = Move(len(self.moves_history), moving_piece, start_coords, end_coords, castle_side, old_fen, curr_fen)
        self.moves_history.append(move)
        return move

    def update_board(self, start_coords: Tuple[int, int], end_coords: Tuple[int, int]):
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
        # Change the colour that has to move next.
        moving_piece = self.board.state[start_coords]
        mpcolor = Piece.get_color(moving_piece)
        mptype = Piece.get_type(moving_piece)

        # Captured piece
        captured_piece = self.board.state[end_coords]
        cpcolor = Piece.get_color(captured_piece)
        cptype = Piece.get_type(captured_piece)

        self.board.try_update_castle_rights(moving_piece)
        if mptype == Piece.PAWN:
            if self.board.en_passant is not None and self.board.en_passant == end_coords:
                # Only a white piece's en-passant square can be on 5th row.
                if  self.board.en_passant[0] == 5:
                    # Kill the white piece.
                    self.board.state[self.board.en_passant[0] - 1, self.board.en_passant[1]] = Piece.EMPTY
                elif self.board.en_passant[0] == 2:
                    # Kill the black piece.
                    self.board.state[self.board.en_passant[0] + 1, self.board.en_passant[1]] = Piece.EMPTY

            if abs(start_coords[0] - end_coords[0]) > 1:
                row_skipped = end_coords[0] + (1 if mpcolor == Piece.WHITE else -1)
                self.board.en_passant = (row_skipped, end_coords[1])
            else:
                self.board.en_passant = None

        # Was the move a castling move?
        castle_side: Optional[int] = None
        if mptype == Piece.KING:
            # Try to get the castling side if it returns None then no castling move was made.
            castle_side = CastleSide.get_side(end_coords)
            if castle_side is not None:
                self.__update_rook_castle_pos(castle_side)

        # Update board state.
        if captured_piece != Piece.EMPTY or mptype == Piece.PAWN:
            self.board.half_move_clock = 0
        else:
            self.board.half_move_clock += 1 
        
        # Update moving piece coords
        self.board.all_pieces[mpcolor][mptype][moving_piece] = end_coords
        # Remove the captured piece.
        if captured_piece != Piece.EMPTY:
            self.board.all_pieces[cpcolor][cptype].pop(captured_piece)
        self.board.state[end_coords] = self.board.state[start_coords]
        self.board.state[start_coords] = Piece.EMPTY
        self.board.full_move = len(self.moves_history) + 1
        return moving_piece, castle_side

    def __update_rook_castle_pos(self, castle_side: int) -> None:
        """Update the rook's position based on the castling side.

        Parameters
        ----------
        castling_side : int
            Change the board state based on the castling side.
        """
        new_rook_coords, rook_coords = CastleSide.get_rook_posistions(castle_side)
        # Change the coords of the rook and the board state.
        self.board.state[new_rook_coords] = self.board.state[rook_coords]
        self.board.state[rook_coords] = Piece.EMPTY

    def is_piece_pickable(self, piece: np.uint32) -> bool:
        """Determine if you can pick a piece.

        If the piece is on the same colour as the player
        who is turn to play then the pick is pickable.
        """
        return Piece.get_color(piece) == self.board.color_to_move
