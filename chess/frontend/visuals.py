"""Creates the visuals for the game."""
import pygame


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


class GameVisuals:
    """Visuals for the game."""    

    def __init__(self, py_g):
        """Needs the same pygame module from the Game class.

        Parameters
        ----------
        py_g : pygame
            The pygame module that another class 
            should inisialize and pass it down here.
        """        
        self.screen = py_g.display.set_mode((800, 800))
        self.background = Background("chess/frontend/images/board.png", [0, 0])

        # Title and icon
        py_g.display.set_caption("Chess")
        py_g.display.set_icon(py_g.image.load("chess/frontend/images/chess_icon.png"))

        # Draw Pieces
        # self.draw_pieces()

    def show_bg(self):
        """Show the bg img to the screen."""        
        # Keep background-img on the screen refreshed
        # self.screen.fill([255, 255, 255])
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.background.image, self.background.rect)
    
    def draw_pieces(self):
        x_pos = 0
        y_pos = 0
        color = 0
        width = 100
        height = 100
        black = (103, 130, 74)
        white = (204, 255, 204)  # (255, 255, 204)

        i = 0
        for x in range(self.board.rows):
            for y in range(self.board.cols):
                # Draw rect
                # TODO: THIS WILL NEED CHANGE LATER ON
                if color % 2 == 0:
                    self.board.tiles[x][y].shape = {'x': x_pos, 'y': y_pos, 'w': width, 'h': height}
                    self.board.tiles[x][y].is_white = True
                    # self.draw_rect(screen, x, y, x_pos, y_pos, width, height, white)
                else:
                    self.board.tiles[x][y].shape = {'x': x_pos, 'y': y_pos, 'w': width, 'h': height}
                    self.board.tiles[x][y].is_white = False
                    # self.draw_rect(screen, x, y, x_pos, y_pos, width, height, black)

                piece = self.board.tiles[x][y].piece

                # Draw pieces and add the piece to 'database'
                if piece is not None:
                    img = pygame.image.load(piece.image_path)
                    img = pygame.transform.scale(img, (100, 100))
                    # self.board.pieces.append([img, [x_pos, y_pos], piece])
                    piece.image = img
                    self.board.pieces.append(piece)

                # if self.debug is True:
                #     print(f'x: {x_pos} y: {y_pos} i: {i}')
                x_pos += 100
                color += 1
                i += 1
            y_pos += 100
            color += 1
            x_pos = 0