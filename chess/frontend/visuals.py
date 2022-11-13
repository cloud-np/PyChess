"""Creates the visuals for the game."""
from email.policy import default
import numpy as np
from chess.frontend.components.background import Background
import pygame as py_g
from typing import List, Tuple, Optional, Any
from colorama import Fore
from chess.board.board import Board
from itertools import chain
from chess.ai.move_picker import random_legal_move
from chess.pieces.piece import Piece


IMGS_PATH = "chess/frontend/assets/images"
BOARD_OFFSET = 21
BOARD_SIZE = (800, 800)
VISUAL_BOARD_SIZE = (1000, 1000)


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
    FLIP_BOARD = 8


class Tile:
    """Visual tile that helps showing the pieces on board."""

    W_TILE_CLICKED_COLOUR = (255, 204, 102)
    B_TILE_CLICKED_COLOUR = (255, 179, 26)

    def __init__(self, coords: Tuple[int, int], is_white: bool = False, text_surface: Optional[py_g.Surface] = None, name: str = ' ', piece_img: Optional[py_g.Surface] = None):
        """Hold the info that are needed to be drawn later on.

        Parameters
        ----------
        coords : Tuple[int, int]
            The coords of the tile.
        name : str
            The name of the tile, by default ' '.
        text_surface : Surface, optional
            This later on will be a holder for text.
        piece_img : Surface, optional
            Holds the img that we will draw on screen, by default None.
        """
        # self.coords: int = Board.normalize_index(index)
        self.coords: Tuple[int, int] = coords
        self.name: str = name
        self.piece_img: Optional[py_g.Surface] = piece_img
        self.is_white: bool = is_white
        self.text_surface: Optional[py_g.Surface] = text_surface
        self.shape: Any = {'x': None, 'y': None, 'w': None, 'h': None}

    def __str__(self):
        """Represent the tile."""
        return f"T[{Fore.MAGENTA}{self.coords}{Fore.RESET}] --> {'*' if self.piece_img is not None else '-'}"


class GameVisuals:
    """Visuals for the game."""

    def __init__(self, game, state: np.ndarray):
        """Needs the same pygame module from the Game class.

        Parameters
        ----------
        py_g : pygame
            The pygame module that another class
            should inisialize and pass it down here.
        """
        self.game = game
        self.show_indexes: bool = False
        self.show_normalized_indexes: bool = False
        self.show_imgs: bool = False
        self.is_running: bool = False
        self.is_piece_picked: bool = False
        self.promoting_piece: Optional[np.uint32] = None
        self.clock = py_g.time.Clock()
        self.screen = py_g.display.set_mode(VISUAL_BOARD_SIZE)
        self.picked_piece = {"img": None, "coords": None}
        self.board_offset: Tuple[int, int] = tuple((vbaxis - baxis) // 2 for vbaxis, baxis in zip(VISUAL_BOARD_SIZE, BOARD_SIZE))
        self.background = Background(f"{IMGS_PATH}/board.png", self.board_offset, BOARD_SIZE)
        self.tiles: List[List[Tile]] = [[Tile((i, j)) for i in range(8)] for j in range(8)]
        self.picked_piece = {"img": None, "coords": None}

        # Title and icon
        py_g.display.set_caption("Chess")
        py_g.font.init()
        self.font = py_g.font.SysFont('Arial', 30)
        # Maybe this crashes only on linux.
        # py_g.display.set_icon(py_g.image.load("{IMGS_PATH}/chess_icon.png"))

        self.load_state(state)

    def set_picked_piece(self, coords):
        """Set the piece that is getting dragged.

        Parameters
        ----------
        index : int
            Index of the tile that had the piece.
        """
        self.picked_piece = {"img": self.tiles[coords[0]][coords[1]].piece_img, "coords": coords}

    def draw_bg(self):
        """Keep background-img on the screen refreshed."""
        self.screen.fill((0, 0, 0))
        if self.background.image is not None and self.background.rect is not None:
            self.screen.blit(self.background.image, self.background.rect)
        else:
            raise Exception("Background image not found.")

    def left_most_tile(self) -> Tile:
        return min((min(row, key=lambda x: x.shape['x']) for row in self.tiles), key=lambda x: x.shape['x'])

    def right_most_tile(self) -> Tile:
        return max((max(row, key=lambda x: x.shape['x']) for row in self.tiles), key=lambda x: x.shape['x'])

    def lowest_most_tile(self) -> Tile:
        return min((min(row, key=lambda x: x.shape['y']) for row in self.tiles), key=lambda x: x.shape['y'])

    def highest_most_tile(self) -> Tile:
        return max((max(row, key=lambda x: x.shape['y']) for row in self.tiles), key=lambda x: x.shape['y'])

    def get_board_corners(self):
        left_tile = self.left_most_tile()
        right_tile = self.right_most_tile()
        highest_tile = self.highest_most_tile()
        lowest_tile = self.lowest_most_tile()

        return left_tile.shape['x'] + self.board_offset[0], right_tile.shape['x'] + self.board_offset[0], lowest_tile.shape['y'] + self.board_offset[1], highest_tile.shape['y']

    def draw_promoting_choice(self) -> None:
        left, right, bottom, top = self.get_board_corners()
        y = (bottom + top) // 2

        color = (30, 54, 50)
        # Set the width, height
        s = py_g.Surface((right + 100, 200))
        s.set_alpha(228)
        s.fill(color)

        if not self.promoting_piece:
            raise Exception("No piece code was given.")
        pcolor = Piece.get_color(self.promoting_piece)
        bishop = Piece.get_img_for_piece(pcolor | Piece.BISHOP, IMGS_PATH)
        knight = Piece.get_img_for_piece(pcolor | Piece.KNIGHT, IMGS_PATH)
        rook = Piece.get_img_for_piece(pcolor | Piece.ROOK, IMGS_PATH)
        queen = Piece.get_img_for_piece(pcolor | Piece.QUEEN, IMGS_PATH)

        # Draw panel
        self.screen.blit(s, (left, y))
        for i, piece in enumerate([bishop, knight, rook, queen]):
            img = py_g.image.load(piece)
            img = py_g.transform.scale(img, (100, 100))
            self.screen.blit(img, (left + 200 + 100 * i, y + 50))

    def draw_indexes(self, normalised=False) -> None:
        """Show the index number of the tile on screen."""
        for i, tile in enumerate(chain.from_iterable(zip(*self.tiles))):
            tile.text_surface = self.font.render(f"{tile.coords if normalised is False else i}", False, (0, 0, 0))
            self.screen.blit(tile.text_surface, (tile.shape['x'] + self.board_offset[0], tile.shape['y'] + self.board_offset[1]))

    def draw_imgs(self) -> None:
        """Show the index number of the tile on screen."""
        for tile in chain.from_iterable(zip(*self.tiles)):
            tile.text_surface = self.font.render(f"{'IMG' if tile.piece_img is not None else ''}", False, (0, 0, 0))
            self.screen.blit(tile.text_surface, (tile.shape['x'] + self.board_offset[0], tile.shape['y'] + self.board_offset[1]))

    def draw_picked_piece(self, m_pos) -> None:
        """Show the picked piece."""
        if self.picked_piece["img"] is None:
            raise Exception("You can't pick an empty tile.")
        self.screen.blit(
            self.picked_piece["img"], (m_pos[0] - 50, m_pos[1] - 50))

    # def draw_played_move(self) -> None:
    #     """Change the colour of the squares of the move that got played."""
    #     rect = [[], []]
    #     for i, row in enumerate(self.tiles):
    #         for j, tile in enumerate(row):
    #             for value in tile.shape.values():
    #                 if i == 0:
    #                     rect[0].append(value)
    #                 else:
    #                     rect[1].append(value)

    #             if j == 0:
    #                 rect[0].append(Tile.W_TILE_CLICKED_COLOUR) if tile.is_white else rect[0].append(Tile.B_TILE_CLICKED_COLOUR)
    #             else:
    #                 rect[1].append(Tile.W_TILE_CLICKED_COLOUR) if tile.is_white else rect[1].append(Tile.B_TILE_CLICKED_COLOUR)

    #     py_g.draw.rect(self.screen, rect[0][4], (rect[0][0], rect[0][1], rect[0][2], rect[0][3]))
    #     py_g.draw.rect(self.screen, rect[1][4], (rect[1][0], rect[1][1], rect[1][2], rect[1][3]))
    def flip_board(self) -> None:
        print("Flipping board...")

    def main_loop(self) -> None:
        """Major visual loop of the program."""
        self.is_running = True

        while self.is_running:
            # NOTE: Make it a more dynamic so the player and PC have different colours.
            # Check if its the PC's turn
            if self.game.player2 == 'PC':
                move_coords = random_legal_move(game=self.game)
                if move_coords is None:
                    print("GG no legal moves")
                else:
                    self.game.make_move(*move_coords)
                    self.load_state(self.game.board.state)
                    print(self.game.board)

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
            elif event_code == EventType.FLIP_BOARD:
                self.flip_board()
            elif event_code == EventType.MOUSE_BUTTONDOWN:
                if self.promoting_piece:
                    self.click_promote((mx, my))
                    self.load_state(self.game.board.state)
                else:
                    self.is_piece_picked = self.try_pick_piece(m_pos=(mx, my))
            elif self.is_piece_picked and event_code == EventType.MOUSE_BUTTONUP:
                # If trying placing the piece was successfull the piece is not longer picked up.
                self.is_piece_picked = not self.try_place_piece(m_pos=(mx, my))

            if self.is_piece_picked:
                self.draw_picked_piece(m_pos=(mx, my))

            if self.show_imgs:
                self.game.generate_all_moves(self.game.board.state, self.game.board.all_pieces, self.game.board.castle_rights, self.game.board.en_passant, 2)
                # self.draw_imgs()

            if self.show_indexes:
                self.draw_indexes()

            if self.show_normalized_indexes:
                self.draw_indexes(normalised=True)

            if self.promoting_piece:
                self.draw_promoting_choice()

            # Update everything on the screen
            py_g.display.update()

    def click_promote(self, m_pos):
        _, coords = self.tile_clicked(m_pos=m_pos)

        match coords:
            case (4, 2) | (3, 2):
                prom_type = Piece.BISHOP
            case (4, 3) | (3, 3):
                prom_type = Piece.KNIGHT
            case (4, 4) | (3, 4):
                prom_type = Piece.ROOK
            case (4, 5) | (3, 5):
                prom_type = Piece.QUEEN
            case _:
                prom_type = None

        if prom_type is not None:
            Board.promote_to(self.game.board.state, self.promoting_piece, prom_type)
            self.promoting_piece = None

    def try_place_piece(self, m_pos) -> bool:
        # sourcery skip: inline-immediately-returned-variable
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
        _, clicked_coords = self.tile_clicked(m_pos)
        start_coords = self.picked_piece["coords"]

        # If this happens place the piece back.
        if start_coords == clicked_coords:
            if self.picked_piece['img'] is not None:
                self.place_picked_piece_back()
            return True
        elif self.game.is_player_move_valid(start_coords, clicked_coords):
            if Board.is_promoting(self.game.board.state[start_coords], clicked_coords):
                # prom = input("Promote to: ")
                # prom_type = {
                #     "q": Piece.QUEEN,
                #     "r": Piece.ROOK,
                #     "k": Piece.KNIGHT,
                #     "b": Piece.BISHOP,
                # }[prom]
                self.promoting_piece = self.game.board.state[start_coords]
            self.game.make_move(self.picked_piece["coords"], clicked_coords)
            print(self.game.board)
            self.load_state(self.game.board.state)
            self.change_cursor("arrow")
            return True
        return False

    def place_picked_piece_back(self) -> None:
        """Place the picked piece back to its original tile."""
        self.tiles[self.picked_piece["coords"][0]][self.picked_piece["coords"]
                                                   [1]].piece_img = self.picked_piece["img"]
        self.picked_piece = {"img": None, "coords": None}
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
        piece, coords = self.tile_clicked(m_pos=m_pos)

        # If a Piece is already being picked.
        if self.picked_piece["coords"] == coords:
            return True
        # If the Piece the user is trying to pick is not its turn to play he/she simply can't pick it.
        elif not self.game.is_piece_turn(coords):
            return False
        elif self.tiles[coords[0]][coords[1]].piece_img is not None and self.game.is_piece_pickable(piece):

            self.change_cursor("diamond")
            self.set_picked_piece(coords)
            self.tiles[coords[0]][coords[1]].piece_img = None
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
        for row in self.tiles:
            for tile in row:
                # if not piece.click:
                if tile.piece_img is not None:
                    self.screen.blit(tile.piece_img, (tile.shape['x'] + self.board_offset[0], tile.shape['y'] + self.board_offset[1]))

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
        row, col = ((m_pos[1] - self.board_offset[1]) // 100), ((m_pos[0] - self.board_offset[0]) // 100)
        piece: np.uint32 = self.game.board.state[row, col]

        if self.game.debug:
            print(m_pos, f"tile: [ {row}, {col} ]")
        return piece, (row, col)

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
                if event.key == py_g.K_f:
                    return EventType.FLIP_BOARD

                #     pick_piece(mouse_x, mouse_y)
            # elif P2_COMPUTER and history['player'] % 2 != 0:
            #     self.pc_make_move(history, False)
            #     history['player'] += 1
        return EventType.NO_EVENT

    def load_state(self, state: np.ndarray):
        """Make the visual tiles for the board.

        Parameters
        ----------
        state : List[List[int]]
            Holds the information for every piece on board.
        """
        x_pos = 0
        y_pos = 0
        width = 100
        height = 100
        colour = True
        # black = (103, 130, 74)
        # white = (204, 255, 204)  # (255, 255, 204)

        for i, row in enumerate(self.tiles):
            if i != 0:
                x_pos = 0
                y_pos += 100
                colour = not colour
            for j, tile in enumerate(row):
                tile.is_white = colour
                colour = not colour
                tile.shape = {'x': x_pos, 'y': y_pos, 'w': width, 'h': height}

                image_path = Piece.get_img_for_piece(state[i, j], IMGS_PATH)
                # In case its an empty tile
                if len(image_path) != 0:
                    # Draw pieces and add the piece to 'database'
                    img = py_g.image.load(image_path)
                    img = py_g.transform.scale(img, (100, 100))
                    tile.piece_img = img
                else:
                    tile.piece_img = None

                # if self.debug is True:
                #     print(f'x: {x_pos} y: {y_pos} i: {i}')
                x_pos += 100
