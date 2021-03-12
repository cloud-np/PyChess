"""uuid: A unique undentifier."""
from uuid import uuid4

from pygame.constants import QUIT
from chess.board import Board
import pygame
from datetime import datetime
from chess.frontend.visuals import GameVisuals


STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
BOARD_SIZE = 64


class EventType:
    """Enum that holds the types of events."""

    QUIT = -1
    NO_EVENT = 0
    STOP = 1
    START = 2


class Game:
    """Basically the main controller for game visuals and game logic."""

    def __init__(self, debug=False, player1="PC", player2="PC"):
        """Construct."""
        self.id: uuid4 = uuid4()
        self.time_created = datetime.now()
        self.debug = debug
        self.py_g = pygame
        self.board: Board = Board(STARTING_FEN, BOARD_SIZE)
        self.visuals = GameVisuals(self.py_g, BOARD_SIZE, self.board.state)


    def __str__(self) -> str:
        """Represent the current game and its info."""
        return f"Created: " \
               f"{self.time_created.strftime('%d/%m/%Y %H:%M:%S')} {self.id}"

    def start(self):
        """Run basic setup functions."""
        clock = self.py_g.time.Clock()
        self.main_loop()

    def main_loop(self):
        """Major loop of the program."""
        # Game Loop
        is_running = True
        # rect_img = clicked_rect = None
        # player_turn = 0

        while is_running:

            # Keep tracking the position of the mouse
            mouse_x, mouse_y = self.py_g.mouse.get_pos()

            # Keep showing the bg
            self.visuals.draw_bg()

            # if history['moved_made']:
            #     self.draw_player_move(history)

            # Keep pieces-img on the screen refreshed
            self.visuals.draw_pieces()
            # for piece in self.board.pieces:
            #     if not piece.click:
            #         tile = self.board.tiles[piece.coords[0]][piece.coords[1]]
            #         self.screen.blit(piece.image, (tile.shape['x'], tile.shape['y']))

            # Look for the game_events
            event_code = self.check_for_events()
            if event_code == EventType.QUIT:
                is_running = False

            # If the player has a piece picked
            # if history['drag_flag']:
            #     self.screen.blit(history['dragged_piece'].image, (mouse_x - 50, mouse_y - 50))

            # Update everything on the screen
            self.py_g.display.update()

            pass  # While loop

    def check_for_events(self):
        """Check for events that may occur during the game.

        Returns
        -------
        int
            An Event enum that shows which event occured if any.
        """
        for event in self.py_g.event.get():
            if event.type == self.py_g.QUIT:
                self.py_g.quit()
                return EventType.QUIT
            elif event.type == self.py_g.MOUSEBUTTONDOWN or event.type == self.py_g.MOUSEBUTTONUP:
                #     pick_piece(mouse_x, mouse_y)
                pass
            # elif P2_COMPUTER and history['player'] % 2 != 0:
            #     self.pc_make_move(history, False)
            #     history['player'] += 1
        return EventType.NO_EVENT
