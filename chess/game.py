"""uuid: A unique undentifier."""
from uuid import uuid4
from chess.board import Board
import pygame
from datetime import datetime
from chess.frontend.visuals import GameVisuals


class Game:
    """This will holds all the info about the game and the players."""

    def __init__(self, debug=False):
        """Construct."""
        self.id: uuid4 = uuid4()
        self.time_created = datetime.now()
        self.board: Board = Board()
        self.debug = debug
        self.py_g = pygame 
        self.visuals = GameVisuals(self.py_g)

    def __str__(self) -> str:
        """Represent the current game and its info."""
        return f"Created: " \
               f"{self.time_created.strftime('%d/%m/%Y %H:%M:%S')} {self.id}"

    def start(self):
        clock = self.py_g.time.Clock()
        self.main_loop()

    def main_loop(self):

        # Game Loop
        running = True
        rect_img = clicked_rect = None
        player_turn = 0

        while running:

            # Keep tracking the position of the mouse
            mouse_x, mouse_y = self.py_g.mouse.get_pos()

            # Keep showing the bg
            self.visuals.show_bg()

            # if history['moved_made']:
            #     self.draw_player_move(history)

            # Keep pieces-img on the screen refreshed
            # for piece in self.board.pieces:
            #     if not piece.click:
            #         tile = self.board.tiles[piece.coords[0]][piece.coords[1]]
            #         self.screen.blit(piece.image, (tile.shape['x'], tile.shape['y']))

            # Look for the game_events
            for event in self.py_g.event.get():
                if event.type == self.py_g.QUIT:
                    running = False
                    self.py_g.quit()
                # elif event.type == self.py_g.MOUSEBUTTONDOWN or event.type == self.py_g.MOUSEBUTTONUP:
                #     pick_piece(mouse_x, mouse_y)
                # elif P2_COMPUTER and history['player'] % 2 != 0:
                #     self.pc_make_move(history, False)
                #     history['player'] += 1

            # If the player has a piece picked
            # if history['drag_flag']:
            #     self.screen.blit(history['dragged_piece'].image, (mouse_x - 50, mouse_y - 50))

            # Update everything on the screen
            self.py_g.display.update()

            pass  # While loop
