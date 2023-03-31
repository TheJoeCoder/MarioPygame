from enum import Enum

class MarioState(Enum):
    CROUCH = 0
    IDLE = 1
    RUN = 2

class MarioDirection(Enum):
    LEFT = 0
    FORWARD = 1
    RIGHT = 2

class ControlType(Enum):
    CONTROL = 0
    CAMERA = 1
    CAMERA_SPRITE_MOVE = 2