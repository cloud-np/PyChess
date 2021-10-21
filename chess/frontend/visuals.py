"""Creates the visuals for the game."""
import pygame as py_g
import numpy as np
from typing import List
from colorama import Fore
from chess.board import Board
from chess.piece import Piece


IMGS_PATH = "chess/frontend/assets/images"
BOARD_OFFSET = 21


class EventType:
    """Enum that holds the types of events."""

    QUIT = -1
    NO_EVENT = 0
    STOP = 1
    START = 2
    SHOW_INDEX = 3
    SHOW_NORMALIZED_INDEX = 4
    SHOW_IMGS = 5
    MOUSE_BUTTONDOWN = 6
    MOUSE_BUTTONUP = 7


class Background(py_g.sprite.Sprite):
    """Helper class to keep showing a background image.

    Parameters
    ----------
    pygame : Pygame
        Helps us to visualize the background img.
    """

    def __init__(self, image_file: str, location: List[int]):
        """Needs basic components for inisializing the bg.

        Parameters
        ----------
        image_file : str
            where the img file is located.
        location : list()
            where it should be showing on the screen.
        """
        py_g.sprite.Sprite.__init__(self)
        self.image = py_g.transform.scale(
            py_g.image.load(image_file), (800, 800))
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location


class Tile:
    """Visual tile that helps showing the pieces on board."""

    W_TILE_CLICKED_COLOUR = (255, 204, 102)
    B_TILE_CLICKED_COLOUR = (255, 179, 26)

    def __init__(self, index: int, is_white: bool = False, text_surface: py_g.Surface = None, name: str = ' ', piece_img: py_g.Surface = None):
        """Hold the info that are needed to be drawn later on.

        Parameters
        ----------
        index : int
            Shows the index on board
        name : str
            The name of the tile, by default ' '
        text_surface : Surface, optional
            This later on will be a holder for text.
        piece_img : Surface, optional
            Holds the img that we will draw on screen, by default None
        """
        self.index: int = Board.normalize_index(index)
        self.name = name
        self.piece_img = piece_img
        self.is_white = is_white
        self.text_surface = text_surface
        self.shape = {'x': None, 'y': None, 'w': None, 'h': None}

    def __str__(self):
        """Represent the tile."""
        return f"T[{Fore.MAGENTA}{self.index}{Fore.RESET}] --> {'*' if self.piece_img is not None else '-'}"


class GameVisuals:
    """Visuals for the game."""

    def __init__(self, game, board_size: int, board_state: np.ndarray):
        """Needs the same pygame module from the Game class.

        Parameters
        ----------
        py_g : pygame
            The pygame module that another class
            should inisialize and pass it down here.
        """
        self.game = game
        self.show_indexes = False
        self.show_normalized_indexes = False
        self.show_imgs = False
        self.is_running = False
        self.is_piece_picked = False
        self.clock = py_g.time.Clock()
        self.screen = py_g.display.set_mode((800, 800))
        self.picked_piece = {"img": None, "index": None}
        self.background = Background(f"{IMGS_PATH}/board.png", [0, 0])
        self.tiles = [Tile(i) for i in range(board_size)]

        # Title and icon
        py_g.display.set_caption("Chess")
        py_g.font.init()
        self.font = py_g.font.SysFont('Arial', 30)
        # Maybe this crashes only on linux.
        # py_g.display.set_icon(py_g.image.load("{IMGS_PATH}/chess_icon.png"))

        self.occupie_tiles(board_state)

    def set_picked_piece(self, index):
        """Set the piece that is getting dragged.

        Parameters
        ----------
        index : int
            Index of the tile that had the piece.
        """
        self.picked_piece = {"img": self.tiles[index].piece_img, "index": index}

    def draw_bg(self):
        """Keep background-img on the screen refreshed."""
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.background.image, self.background.rect)

    def draw_indexes(self, normalised=False) -> None:
        """Show the index number of the tile on screen."""
        for i, tile in enumerate(self.tiles):
            tile.text_surface = self.font.render(f"{tile.index if normalised is False else i}", False, (0, 0, 0))
            self.screen.blit(tile.text_surface, (tile.shape['x'], tile.shape['y']))

    def draw_imgs(self) -> None:
        """Show the index number of the tile on screen."""
        for tile in self.tiles:
            tile.text_surface = self.font.render(f"{'IMG' if tile.piece_img is not None else ''}", False, (0, 0, 0))
            self.screen.blit(tile.text_surface, (tile.shape['x'], tile.shape['y']))

    def draw_picked_piece(self, m_pos) -> None:
        """Show the picked piece."""
        if self.picked_piece["img"] is None:
            raise Exception("You can't pick an empty tile.")
        self.screen.blit(self.picked_piece["img"], (m_pos[0] - 50, m_pos[1] - 50))

    def draw_played_move(self) -> None:
        """Change the colour of the squares of the move that got played."""
        rect = [[], []]
        for i, tile in enumerate(self.tiles):
            for value in tile.shape.values():
                if i == 0:
                    rect[0].append(value)
                else:
                    rect[1].append(value)

            if i == 0:
                rect[0].append(Tile.W_TILE_CLICKED_COLOUR) if tile.is_white else rect[0].append(Tile.B_TILE_CLICKED_COLOUR)
            else:
                rect[1].append(Tile.W_TILE_CLICKED_COLOUR) if tile.is_white else rect[1].append(Tile.B_TILE_CLICKED_COLOUR)

        py_g.draw.rect(self.screen, rect[0][4], (rect[0][0], rect[0][1], rect[0][2], rect[0][3]))
        py_g.draw.rect(self.screen, rect[1][4], (rect[1][0], rect[1][1], rect[1][2], rect[1][3]))

    def main_loop(self) -> None:
        """Major visual loop of the program."""
        # Game Loop
        # rect_img = clicked_rect = None
        # player_turn = 0
        self.is_running = True

        while self.is_running:
            # Keep tracking the position of the mouse
            mx, my = py_g.mouse.get_pos()

            # Keep showing the bg
            self.draw_bg()

            # Keep pieces-img on the screen refreshed
            self.draw_pieces()

            # Look for the game_events
            event_code = GameVisuals.check_for_events()
            if event_code == EventType.QUIT:
                self.is_running = False
            elif event_code == EventType.SHOW_INDEX:
                self.show_indexes = not self.show_indexes
            elif event_code == EventType.SHOW_NORMALIZED_INDEX:
                self.show_normalized_indexes = not self.show_normalized_indexes
            elif event_code == EventType.SHOW_IMGS:
                self.show_imgs = not self.show_imgs
            elif event_code == EventType.MOUSE_BUTTONDOWN:
                self.is_piece_picked = self.try_pick_piece(m_pos=(mx, my))
            elif self.is_piece_picked and event_code == EventType.MOUSE_BUTTONUP:
                # If trying placing the piece was successfull the piece is not longer picked up.
                self.is_piece_picked = not self.try_place_piece(m_pos=(mx, my))

            if self.is_piece_picked:
                self.draw_picked_piece(m_pos=(mx, my))

            if self.show_imgs:
                self.draw_imgs()

            if self.show_indexes:
                self.draw_indexes()

            if self.show_normalized_indexes:
                self.draw_indexes(normalised=True)

            # Update everything on the screen
            py_g.display.update()
            pass  # While loop

    def try_place_piece(self, m_pos) -> bool:
        """Try place the picked piece either back to its original tile or at the specific tile the player clicked.

        Parameters
        ----------
        m_pos : tuple(int, int)
            The pos of the mouse on the screen.

        Returns
        -------
        bool
            Where or not it was able to place the picked piece.
        """
        _, index = self.tile_clicked(m_pos)

        # If this happens place the piece back.
        if self.picked_piece["index"] == index:
            if self.picked_piece['img'] is not None:
                self.place_picked_piece_back()
            return True
        elif self.game.is_player_move_valid(self.picked_piece["index"], index):
            # Update Game state
            self.game.register_move(self.picked_piece["index"], index)
            # Update visuals
            self.swap_picked_piece(index)
            self.change_cursor("arrow")
            return True
        return False

    def swap_picked_piece(self, index) -> None:
        """Swap the picked piece with the tile selected.

        Parameters
        ----------
        index : int
            The index of the new tile.
        """
        new_tile = self.tiles[index]
        old_tile = self.tiles[self.picked_piece["index"]]
        new_tile.piece_img = self.picked_piece["img"]
        old_tile.piece_img = None
        self.picked_piece = {"img": None, "index": None}

    def place_picked_piece_back(self) -> None:
        """Place the picked piece back to its original tile."""
        self.tiles[self.picked_piece["index"]].piece_img = self.picked_piece["img"]
        self.picked_piece = {"img": None, "index": None}
        self.change_cursor("arrow")

    def try_pick_piece(self, m_pos):
        """Try picking up the a piece from a clicked tile.

        Parameters
        ----------
        m_pos : tuple(int, int)
           The position of the mouse on the screen.

        Returns
        -------
        bool
           Whether or not the picking action was successfull.
        """
        piece_code, index = self.tile_clicked(m_pos=m_pos)

        if self.picked_piece["index"] == index:
            return True
        elif self.tiles[index].piece_img is not None and self.game.is_piece_pickable(piece_code):

            self.change_cursor("diamond")
            self.set_picked_piece(index)
            self.tiles[index].piece_img = None
            return True
        elif self.picked_piece['img'] is not None:
            self.place_picked_piece_back()

        return False

    @staticmethod
    def change_cursor(cursor):
        """Change the cursor.

        Parameters
        ----------
        cursor : str
            The cursor type.
        """
        if cursor == "diamond":
            py_g.mouse.set_cursor(*py_g.cursors.diamond)
        elif cursor == "arrow":
            py_g.mouse.set_cursor(*py_g.cursors.arrow)

    def draw_pieces(self):
        """Keep showing the pieces on board."""
        for tile in self.tiles:
            # if not piece.click:
            if tile.piece_img is not None:
                self.screen.blit(tile.piece_img, (tile.shape['x'], tile.shape['y']))

    def tile_clicked(self, m_pos):
        """Get the tile that the user clicked.

        Parameters
        ----------
        m_pos : tuple(int, int)
            The position of the mouse on the screen.

        Returns
        -------
        tuple(int, int)
            The index and piece that occupies the tile.
        """
        index = (m_pos[1] // 100) * 8 + (m_pos[0] // 100)
        piece_code = self.game.board.state[Board.normalize_index(index)]

        if self.game.debug:
            print(m_pos, f"tile: {index}")
        return piece_code, index

    @staticmethod
    def check_for_events():
        """Check for events that may occur during the game.

        Returns
        -------
        int
            An Event enum that shows which event occured if any.
        """
        for event in py_g.event.get():
            if event.type == py_g.QUIT:
                py_g.quit()
                return EventType.QUIT
            elif event.type == py_g.MOUSEBUTTONDOWN:
                return EventType.MOUSE_BUTTONDOWN
            elif event.type == py_g.MOUSEBUTTONUP:
                return EventType.MOUSE_BUTTONUP
            elif event.type == py_g.KEYDOWN:
                if event.key == py_g.K_1:
                    return EventType.SHOW_INDEX
                if event.key == py_g.K_2:
                    return EventType.SHOW_NORMALIZED_INDEX
                if event.key == py_g.K_3:
                    return EventType.SHOW_IMGS

                #     pick_piece(mouse_x, mouse_y)
            # elif P2_COMPUTER and history['player'] % 2 != 0:
            #     self.pc_make_move(history, False)
            #     history['player'] += 1
        return EventType.NO_EVENT

    def occupie_tiles(self, board_state):
        """Make the visual tiles for the board.

        Parameters
        ----------
        board_state : numpy.array(dtype="uint8")
            Holds the information for every tile on board.
        """
        x_pos = 0
        y_pos = 0
        width = 100
        height = 100
        colour = True
        # black = (103, 130, 74)
        # white = (204, 255, 204)  # (255, 255, 204)

        for i, tile in enumerate(self.tiles):
            if i % 8 == 0 and i != 0:
                x_pos = 0
                y_pos += 100
                colour = not colour
            tile.is_white = colour
            colour = not colour
            tile.shape = {'x': x_pos, 'y': y_pos, 'w': width, 'h': height}

            index = Board.normalize_index(i)
            if board_state[index] > Piece.EMPTY:
                if board_state[index] != Piece.INVALID:
                    image_path = Piece.get_img_for_piece(board_state[index], IMGS_PATH)
                    # Draw pieces and add the piece to 'database'
                    img = py_g.image.load(image_path)
                    img = py_g.transform.scale(img, (100, 100))
                    tile.piece_img = img

            # if self.debug is True:
            #     print(f'x: {x_pos} y: {y_pos} i: {i}')
            x_pos += 100
