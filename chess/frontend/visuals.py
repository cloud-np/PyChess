"""Creates the visuals for the game."""
import pygame
from chess.piece import Piece

IMGS_PATH = "chess/assets/images"


class Background(pygame.sprite.Sprite):
    """Helper class to keep showing a background image.

    Parameters
    ----------
    pygame : Pygame 
        Helps us to visualize the background img.
    """

    def __init__(self, image_file, location):
        """Needs basic components for inisializing the bg.

        Parameters
        ----------
        image_file : str
            where the img file is located.
        location : list()
            where it should be showing on the screen.
        """
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(
            pygame.image.load(image_file), (800, 800))
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location


class Tile:
    """Visual tile that helps showing the pieces on board."""    

    def __init__(self, index, name=' ', piece_img=None):
        """Hold the info that are needed to be drawn later on.

        Parameters
        ----------
        index : int
            Shows the index on board
        name : str
            The name of the tile, by default ' '
        piece_img : Surface, optional
            Holds the img that we will draw on screen, by default None
        """        
        self.index = index
        self.name = name
        self.piece_img = piece_img
        self.shape = {'x': None, 'y': None, 'w': None, 'h': None}


class GameVisuals:
    """Visuals for the game."""

    def __init__(self, py_g, board_size, board_state):
        """Needs the same pygame module from the Game class.

        Parameters
        ----------
        py_g : pygame
            The pygame module that another class 
            should inisialize and pass it down here.
        """
        self.screen = py_g.display.set_mode((800, 800))
        self.background = Background(f"{IMGS_PATH}/board.png", [0, 0])
        self.tiles = [Tile(i) for i in range(board_size)]

        # Title and icon
        py_g.display.set_caption("Chess")
        # Maybe this crashes only on linux.
        # py_g.display.set_icon(py_g.image.load("{IMGS_PATH}/chess_icon.png"))

        self.py_g = py_g
        self.create_tiles(board_state)

    def draw_bg(self):
        """Keep background-img on the screen refreshed."""
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.background.image, self.background.rect)

    @staticmethod
    def get_img_for_piece(piece_code):
        """Find the correct img for a piece.

        Parameters
        ----------
        piece_code : uint8
            A way we represent our pieces.

        Returns
        -------
        str
            The path of the piece img.
        """
        path = f"{IMGS_PATH}/"

        colour, type = Piece.get_colour_and_type(piece_code)

        if colour == Piece.WHITE:
            path += 'w'
        elif colour == Piece.BLACK:
            path += 'b'

        if type == Piece.KING:
            path += 'k'
        elif type == Piece.PAWN:
            path += 'p'
        elif type == Piece.KNIGHT:
            path += 'n'
        elif type == Piece.BISHOP:
            path += 'b'
        elif type == Piece.ROOK:
            path += 'r'
        elif type == Piece.QUEEN:
            path += 'q'

        return f"{path}.png"
    
    def draw_pieces(self):
        """Keep showing the pieces on board."""        
        for tile in self.tiles:
            # if not piece.click:
            if tile.piece_img is not None:
                self.screen.blit(tile.piece_img, (tile.shape['x'], tile.shape['y']))


    def create_tiles(self, board_state):
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
        # black = (103, 130, 74)
        # white = (204, 255, 204)  # (255, 255, 204)

        for i, tile in enumerate(self.tiles):
            if i % 8 == 0 and i != 0:
                x_pos = 0
                y_pos += 100
            tile.shape = {'x': x_pos, 'y': y_pos, 'w': width, 'h': height}

            if board_state[i] > 0:
                image_path = GameVisuals.get_img_for_piece(board_state[i])
                # Draw pieces and add the piece to 'database'
                img = pygame.image.load(image_path)
                img = pygame.transform.scale(img, (100, 100))
                # self.board.pieces.append([img, [x_pos, y_pos], piece])
                tile.piece_img = img
                # piece.image = img
                # self.board.pieces.append(piece)

            # if self.debug is True:
            #     print(f'x: {x_pos} y: {y_pos} i: {i}')
            x_pos += 100
