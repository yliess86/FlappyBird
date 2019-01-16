import numpy as np

from maths import Vector2D

def aabb_aabb_collision(trans_a, col_a, trans_b, col_b, h):
    pos_a   = trans_a.pos + col_a.pos
    pos_b   = trans_b.pos + col_b.pos
    pos_a.y = h - pos_a.y
    pos_b.y = h - pos_b.y

    if pos_b.x > pos_a.x + col_a.w: return False
    if pos_b.x + col_b.w < pos_a.x: return False
    if pos_b.y > pos_a.y + col_a.h: return False
    if pos_b.y + col_b.h < pos_a.y: return False

    return True
