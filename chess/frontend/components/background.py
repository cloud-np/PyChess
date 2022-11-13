import pygame as py_g
from typing import Tuple

class Background(py_g.sprite.Sprite):
    """Helper class to keep showing a background image.

    Parameters
    ----------
    pygame : Pygame
        Helps us to visualize the background img.
    """

    def __init__(self, image_file: str, location: Tuple[int, int], board_size: Tuple[int, int]):
        """Needs basic components for inisializing the bg.

        Parameters
        ----------
        image_file : str
            where the img file is located.
        location : list()
            where it should be showing on the screen.
        """
        py_g.sprite.Sprite.__init__(self)
        self.image = py_g.transform.scale(py_g.image.load(image_file), board_size)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location