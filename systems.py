from components import SpriteSheetSequenceComponent
from components import RectangleColliderComponent
from components import ResetPositionComponent
from components import ObstacleTagComponent
from components import ScrollableComponent
from components import RenderableComponent
from components import TransformComponent
from components import RigidBodyComponent
from components import PlayerTagComponent
from components import PipeStateComponent
from components import PipeTagComponent
from components import ScoreComponent
from components import FlapComponent

from maths import Vector2D
from ecs import System

import pygame as pg
import numpy as np
import physics

class SpriteSheetSequenceSystem(System):
    def __init__(self):
        super().__init__()

    def update(self, dt, *args, **kwargs):
        components = self.world.get_components(SpriteSheetSequenceComponent, RenderableComponent)
        if components is None: return

        for ent, (sss, rend) in components:
            sss.clock += dt

            sss.index  += int(sss.clock / sss.duration)
            sss.index  %= len(sss.sprites)
            rend.sprite = sss.sprites[sss.index]

            if sss.clock > sss.duration: sss.clock = 0

class RenderableSystem(System):
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.w      = window.get_width()
        self.h      = window.get_height()

    def update(self, *args, **kwargs):
        components = self.world.get_components(TransformComponent, RenderableComponent)
        if components is None: return

        components.sort(key=lambda x: x[1][1].depth)
        for ent, (trans, rend) in components:
            sprite   = rend.sprite
            if trans.rot != None:
                sprite   = pg.transform.rotate(sprite.copy(), trans.rot)
                rend.pos = Vector2D(-0.5 * sprite.get_width(), 0.5 * sprite.get_height())

            pos   = trans.pos + rend.pos
            pos.y = self.h - pos.y

            self.window.blit(sprite, pos.to_tuple())

        for ent, (trans, col) in self.world.get_components(TransformComponent, RectangleColliderComponent):
            pos   = trans.pos + col.pos
            pos.y = self.h - pos.y

            color = (0, 255, 0) if len(col.manifolds) <= 0 else (255, 0, 0)
            pg.draw.rect(self.window, color, (*pos.to_tuple(), col.w, col.h), 2)

            pos   = Vector2D(trans.pos.x, trans.pos.y)
            pos.y = self.h - pos.y

            color = (0, 0, 255)
            pg.draw.lines(self.window, color, False, [(int(pos.x - 8), int(pos.y)), (int(pos.x + 8), int(pos.y))], 2)
            pg.draw.lines(self.window, color, False, [(int(pos.x), int(pos.y - 8)), (int(pos.x), int(pos.y + 8))], 2)

class ScoreRenderSystem(System):
    def __init__(self, window, font):
        super().__init__()
        self.window = window
        self.w      = window.get_width()
        self.h      = window.get_height()
        self.font   = font

    def update(self, *args, **kwargs):
        components = self.world.get_component(ScoreComponent)
        if components is None: return

        for ent, score in components:
            text      = self.font.render(f'{score.value}', True, (255, 255, 255))
            text_rect = text.get_rect(center=(0.5 * self.w, 50))
            self.window.blit(text, text_rect)

class GravitySystem(System):
    def __init__(self, force=-9.8):
        super().__init__()
        self.force = force

    def update(self, *args, **kwargs):
        components = self.world.get_component(RigidBodyComponent)
        if components is None: return

        for ent, rigid in components:
            rigid.acc += Vector2D(0, self.force)

class FlapSystem(System):
    def __init__(self):
        super().__init__()

    def update(self, inputs, *args, **kwargs):
        components = self.world.get_components(FlapComponent, RigidBodyComponent)
        if components is None: return

        if not inputs['SPACE_BAR']: return

        for ent, (flap, rigid) in components:
            rigid.vel = Vector2D(0, flap.force)

class TiltSystem(System):
    def __init__(self):
        super().__init__()

    def update(self, *args, **kwargs):
        components = self.world.get_components(TransformComponent, RigidBodyComponent)
        if components is None: return

        for ent, (trans, rigid) in components:
            vel       = min(max(rigid.vel.y, -400), 400) / 400
            trans.rot = vel * 45

class MovementSystem(System):
    def __init__(self):
        super().__init__()

    def update(self, dt, *args, **kwargs):
        components = self.world.get_components(TransformComponent, RigidBodyComponent)
        if components is None: return

        for ent, (trans, rigid) in components:
            last_vel   = Vector2D(rigid.vel.x, rigid.vel.y)
            rigid.vel += rigid.acc * dt
            trans.pos += 0.5 * (last_vel + rigid.vel) * dt

            rigid.acc = Vector2D()

class ScrollableSystem(System):
    def __init__(self):
        super().__init__()

    def update(self, dt, *args, **kwargs):
        components = self.world.get_components(TransformComponent, ScrollableComponent)
        if components is None: return

        for ent, (trans, scroll) in components:
            trans.pos += scroll.speed * dt

class ResetPositionSystem(System):
    def __init__(self, window):
        super().__init__()

    def update(self, *args, **kwargs):
        components = self.world.get_components(TransformComponent, ResetPositionComponent)
        if components is None: return

        for ent, (trans, reset) in components:
            if trans.pos.x < reset.thresh:
                trans.pos = Vector2D(reset.pos.x, reset.pos.y)

class ResetPipeOffsetSystem(System):
    def __init__(self, offset_range):
        super().__init__()
        self.offset_range = offset_range

    def update(self, *args, **kwargs):
        components = self.world.get_components(TransformComponent, PipeTagComponent, ResetPositionComponent)
        if components is None: return

        offset = np.random.randint(*self.offset_range)
        for ent, (trans, tag, reset) in components:
            if trans.pos.y <= reset.pos.y:
                trans.pos.y += offset

class ResetPipeStateSystem(System):
    def __init__(self):
        super().__init__()

    def update(self, *args, **kwargs):
        components = self.world.get_components(TransformComponent, ResetPositionComponent, PipeStateComponent)
        if components is None: return

        for ent, (trans, reset, state) in components:
            if trans.pos.x >= reset.pos.x:
                state.value = False

class CollisionSystem(System):
    def __init__(self, window):
        super().__init__()
        self.h = window.get_height()

    def update(self, *args, **kwargs):
        components = self.world.get_components(TransformComponent, RigidBodyComponent, RectangleColliderComponent, PlayerTagComponent)
        if components is None: return

        col_components = self.world.get_components(TransformComponent, RectangleColliderComponent, ObstacleTagComponent)
        if col_components is None: return

        for ent, (trans, rigid, col, tag) in components:
            col.manifolds = []
            for ent_b, (trans_b, col_b, tag_b) in col_components:
                collision = physics.aabb_aabb_collision(trans, col, trans_b, col_b, self.h)
                if collision:
                    col.manifolds.append(ent_b)

class PlayerStateSystem(System):
    def __init__(self, scrollable_component, dead_sprite):
        super().__init__()
        self.scrollable_component = scrollable_component
        self.dead_sprite          = dead_sprite

    def update(self, *args, **kwargs):
        components = self.world.get_components(TransformComponent, RectangleColliderComponent, RenderableComponent, PlayerTagComponent)
        if components is None: return

        for ent, (trans, col, rend, tag) in components:
            if len(col.manifolds) > 0:
                trans.rot   = 0
                rend.sprite = self.dead_sprite

                self.world.remove_component(ent, SpriteSheetSequenceComponent)
                self.world.remove_component(ent, RigidBodyComponent)
                self.world.remove_component(ent, FlapComponent)
                self.world.remove_component(ent, PlayerTagComponent)

                scrollable_component = ScrollableComponent(
                    self.scrollable_component.speed.x,
                    self.scrollable_component.speed.y
                )
                self.world.add_component(ent, scrollable_component)

class ScoreSystem(System):
    def __init__(self):
        super().__init__()

    def update(self, *args, **kwargs):
        components = self.world.get_components(TransformComponent, RectangleColliderComponent, PipeStateComponent, PipeStateComponent)
        if components is None: return

        player_components = self.world.get_components(TransformComponent, RectangleColliderComponent, ScoreComponent, PlayerTagComponent)
        if player_components is None: return

        for p_ent, (p_trans, p_col, p_score, p_tag) in player_components:
            p_pos = p_trans.pos + p_col.pos

            for ent, (trans, col, state, tag) in components:
                if state.value == True: return

                pos    = trans.pos + col.pos
                pos.x += col.w

                if p_pos.x > pos.x:
                    p_score.value += 1
                    state.value    = True
                    return
