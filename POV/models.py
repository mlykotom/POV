import cv2
from abc import ABC, abstractmethod
import numpy as np


class BaseModel(ABC):
    INVALID_POSITION = (-1, -1)

    @abstractmethod
    def __init__(self, position):
        self.position = position

    @abstractmethod
    def render_model(self, drawer):
        pass

    def render(self, drawer):
        """
        Do not override this
        :param image:
        :return:
        """
        if self.position == self.INVALID_POSITION: return
        self.render_model(drawer)

    def is_visible(self):
        return self.position != self.INVALID_POSITION


class Ball(BaseModel):
    """
    Represents ball in playground
    """
    BALL_KNOWN_RADIUS = 22

    def render_model(self, drawer):
        drawer.draw_rect((self.position, (self.position[0] + 2, self.position[1] + 2)), (255, 0, 0), 3)
        drawer.draw_circle(self.position, self.radius, (0, 200, 0), 1)
        drawer.draw_circle(self.position, self.BALL_KNOWN_RADIUS, (0, 255, 0), 2)

    def __init__(self, position, radius, contour):
        super().__init__(position)
        self.radius = radius
        self.contour = contour


class Dummy(BaseModel):
    """Represents dummy (footbal player) on the line"""

    def render_model(self, drawer):
        drawer.draw_marker(self.footPosition, (0, 255, 0))
        drawer.draw_circle(self.position, 5, (0, 255, 0), -1)

    def __init__(self, position, playerIndex, lineIndex, footPosition, player):
        super().__init__(position)
        self.playerIndex = playerIndex
        self.lineIndex = lineIndex
        self.footPosition = footPosition
        self.player = player
