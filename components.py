import pygame as pg

from maths import Vector2D

class TransformComponent(object):
    def __init__(self, x, y, rot=None):
        self.pos = Vector2D(x, y)
        self.rot = rot

class RigidBodyComponent(object):
    def __init__(self, vel_x=0, vel_y=0, acc_x=0, acc_y=0):
        self.vel = Vector2D(vel_x, vel_y)
        self.acc = Vector2D(acc_x, acc_y)

class RenderableComponent(object):
    def __init__(self, sprite, x, y, size=None, depth=0):
        self.sprite = sprite if size is None else pg.transform.scale(sprite, size)
        self.pos    = Vector2D(x, -y)
        self.depth  = depth

class SpriteSheetSequenceComponent(object):
    def __init__(self, spritesheet, size, n_row, n_col, duration):
        self.duration    = duration
        self.sprites     = []
        self.clock       = 0
        self.index       = 0

        self._set_sprites(spritesheet, n_col, n_row, size)

    def _set_sprites(self, spritesheet, n_col, n_row, size):
        _w = spritesheet.get_width() // n_col
        _h = spritesheet.get_height() // n_row

        for row in range(n_row):
            for col in range(n_col):
                surf = pg.Surface((_w, _h), pg.SRCALPHA)
                surf.blit(spritesheet, (0, 0), (col * _w, row * _h, _w, _h))
                surf = pg.transform.scale(surf, size)
                self.sprites.append(surf)

class FlapComponent(object):
    def __init__(self, force=10):
        self.force = force

class ScrollableComponent(object):
    def __init__(self, speed_x=0, speed_y=0):
        self.speed = Vector2D(speed_x, speed_y)

class ResetPositionComponent(object):
    def __init__(self, x=0, y=0, thresh=0):
        self.pos    = Vector2D(x, y)
        self.thresh = thresh

class RectangleColliderComponent(object):
    def __init__(self, x, y, w, h):
        self.pos       = Vector2D(x, -y)
        self.w         = w
        self.h         = h
        self.manifolds = []

class PlayerTagComponent(object):
    def __init__(self):
        pass

class ObstacleTagComponent(object):
    def __init__(self):
        pass

class PipeTagComponent(object):
    def __init__(self):
        pass

class PipeStateComponent(object):
    def __init__(self):
        self.value = False

class ScoreComponent(object):
    def __init__(self):
        self.value = 0
