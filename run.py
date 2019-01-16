import pygame as pg
import numpy as np
import time

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

from systems import SpriteSheetSequenceSystem
from systems import ResetPipeOffsetSystem
from systems import ResetPipeStateSystem
from systems import ResetPositionSystem
from systems import PlayerStateSystem
from systems import ScoreRenderSystem
from systems import ScrollableSystem
from systems import RenderableSystem
from systems import CollisionSystem
from systems import MovementSystem
from systems import GravitySystem
from systems import ScoreSystem
from systems import FlapSystem
from systems import TiltSystem

from ecs import World

import os

class InputManager(object):
    def __init__(self):
        self.KEYS = { 'SPACE_BAR': False }

    def update(self, events):
        self.KEYS['SPACE_BAR'] = False

        for event in events:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.KEYS['SPACE_BAR'] = True

    def __getitem__(self, index):
        if index not in self.KEYS: return False
        return self.KEYS[index]

display = (640, 980)
fps_cap = 60

os.environ['SDL_VIDEO_CENTERED'] = '1'
pg.init()

window     = pg.display.set_mode(display)
clock      = pg.time.Clock()
font       = pg.font.Font(None , 30)
score_font = pg.font.Font(None, 50)
inputs     = InputManager()

world = World()

gravity_system         = GravitySystem(force=-900)
flap_system            = FlapSystem()
movement_system        = MovementSystem()
tilt_system            = TiltSystem()
scrollable_system      = ScrollableSystem()
collision_system       = CollisionSystem(window)
score_system           = ScoreSystem()
sprite_sheet_system    = SpriteSheetSequenceSystem()
renderable_system      = RenderableSystem(window)
scorerender_system     = ScoreRenderSystem(window, score_font)
resetposition_system   = ResetPositionSystem(window)
resetpipeoffset_system = ResetPipeOffsetSystem((0, 470))
playerstate_system     = PlayerStateSystem(ScrollableComponent(-150, 0), pg.transform.scale(pg.image.load('./res/flappy_dead.png').convert_alpha(), (100, 80)))
resetpipestate_system  = ResetPipeStateSystem()

world.add_system(gravity_system, priority=8)
world.add_system(flap_system, priority=7)
world.add_system(movement_system, priority=6)
world.add_system(tilt_system, priority=5)
world.add_system(scrollable_system, priority=4)
world.add_system(collision_system, priority=3)
world.add_system(score_system, priority=2)
world.add_system(sprite_sheet_system, priority=1)
world.add_system(renderable_system, priority=0)
world.add_system(scorerender_system, priority=-1)
world.add_system(resetposition_system, priority=-2)
world.add_system(resetpipeoffset_system, priority=-3)
world.add_system(playerstate_system, priority=-4)
world.add_system(resetpipestate_system, priority=-5)

player = world.create_entity(
    TransformComponent(180, 490, rot=45),
    RenderableComponent(sprite=None, x=-50, y=-40, size=None, depth=10),
    SpriteSheetSequenceComponent(
        spritesheet = pg.image.load('./res/flappy.png').convert_alpha(),
        size        = (100, 80),
        n_row       = 1,
        n_col       = 4,
        duration    = 0.1
    ),
    RigidBodyComponent(),
    FlapComponent(force=400),
    RectangleColliderComponent(x=-40, y=-40, w=80, h=60),
    PlayerTagComponent(),
    ScoreComponent()
)

sky = world.create_entity(
    TransformComponent(0, 980),
    RenderableComponent(
        sprite = pg.image.load('./res/sky.jpg'),
        x      = 0,
        y      = 0,
        size   = (640, 980),
        depth  = 0
    )
)

clouds = [
    world.create_entity(
        TransformComponent(i * 640, 980),
        RenderableComponent(
            sprite = pg.image.load('./res/clouds.png').convert_alpha(),
            x      = 0,
            y      = 0,
            size   = (640, 980),
            depth  = 1
        ),
        ScrollableComponent(-12, 0),
        ResetPositionComponent(640, 980, -640)
    )
    for i in range(2)
]

buildings = [
    world.create_entity(
        TransformComponent(i * 640, 980),
        RenderableComponent(
            sprite = pg.image.load('./res/buildings.png').convert_alpha(),
            x      = 0,
            y      = 0,
            size   = (640, 980),
            depth  = 2
        ),
        ScrollableComponent(-16, 0),
        ResetPositionComponent(640, 980, -640)
    )
    for i in range(2)
]

trees = [
    world.create_entity(
        TransformComponent(i * 640, 980),
        RenderableComponent(
            sprite = pg.image.load('./res/trees.png').convert_alpha(),
            x      = 0,
            y      = 0,
            size   = (640, 980),
            depth  = 3
        ),
        ScrollableComponent(-22, 0),
        ResetPositionComponent(640, 980, -640)
    )
    for i in range(2)
]

floor = [
    world.create_entity(
        TransformComponent(i * 640, 980),
        RenderableComponent(
            sprite = pg.image.load('./res/floor.png').convert_alpha(),
            x      = 0,
            y      = 0,
            size   = (640, 980),
            depth  = 5
        ),
        ScrollableComponent(-150, 0),
        ResetPositionComponent(640, 980, -640),
        RectangleColliderComponent(x=0, y=980 - 190, w=640, h=190),
        ObstacleTagComponent()
    )
    for i in range(2)
]

pipe_gap        = 200
pipe_pos_x      = 709
pipe_down_pos_y = -396.5 + 260
pipe_up_pos_y   = pipe_down_pos_y + 793

pipe_up = world.create_entity(
    TransformComponent(pipe_pos_x, pipe_up_pos_y + pipe_gap),
    RenderableComponent(
        sprite = pg.image.load('./res/pipe_up.png').convert_alpha(),
        x      = -69,
        y      = -396.5,
        size   = (138, 793),
        depth  = 4
    ),
    ScrollableComponent(-150, 0),
    ResetPositionComponent(pipe_pos_x, pipe_up_pos_y + pipe_gap, -69),
    RectangleColliderComponent(x=-69, y=-396.5, w=138, h=793),
    ObstacleTagComponent(),
    PipeTagComponent()
)

pipe_down = world.create_entity(
    TransformComponent(pipe_pos_x, pipe_down_pos_y),
    RenderableComponent(
        sprite = pg.image.load('./res/pipe_down.png').convert_alpha(),
        x      = -69,
        y      = -396.5,
        size   = (138, 793),
        depth  = 4
    ),
    ScrollableComponent(-150, 0),
    ResetPositionComponent(pipe_pos_x, pipe_down_pos_y, -69),
    RectangleColliderComponent(x=-69, y=-396.5, w=138, h=793),
    ObstacleTagComponent(),
    PipeTagComponent(),
    PipeStateComponent()
)

last_time = time.time()
dt        = 0

running = True
while running:
    current_time   = time.time()
    dt             = current_time - last_time
    last_time      = current_time

    events = pg.event.get()
    for event in events:
        if event.type == pg.QUIT:
            running = False
    inputs.update(events)

    window.fill((0, 0, 0))
    world.update(dt=dt, inputs=inputs)
    window.blit(font.render(f'FPS: {int(clock.get_fps())}', True, (255, 255, 255)), (10, 10))
    pg.display.flip()

    clock.tick(fps_cap)
