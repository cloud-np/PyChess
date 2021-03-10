"""Creates the visuals for the game."""
import pygame


class Background(pygame.sprite.Sprite):
    def __init__(self, image_file, location):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(
            pygame.image.load(image_file), (800, 800))
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location


class GameVisuals:
    def __init__(self, py_g):

        self.screen = py_g.display.set_mode((800, 800))
        self.background = Background("chess/frontend/images/board.png", [0, 0])

        # Title and icon
        py_g.display.set_caption("Chess")
        py_g.display.set_icon(py_g.image.load("chess/frontend/images/chess_icon.png"))

        # Draw Pieces
        # self.draw_pieces()

    def show_bg(self):
        # Keep background-img on the screen refreshed
        self.screen.fill([255, 255, 255])
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.background.image, self.background.rect)