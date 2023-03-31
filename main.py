import pygame
import pickle

from gamelib import *

snes_width=256
snes_height=224

max_x_velocity = 5
max_y_velocity = 5

# deprecated
def scale(measurement: int) -> int:
    return measurement

def x_percent(percent: int) -> int:
    return round((percent/100) * snes_width)

def y_percent(percent: int) -> int:
    return round((percent/100) * snes_height)

pygame.init()

canvas = pygame.display.set_mode((snes_width, snes_height))
clock = pygame.time.Clock()

pygame.display.set_caption("Sooper Mario Bros")


sprite_files = [
    ["sprites/mario/mario-normal-idle-left.png", (32, 200, 248)],
    ["sprites/mario/mario-normal-idle-forward.png", (32, 200, 248)],
    ["sprites/mario/mario-normal-idle-right.png", (32, 200, 248)],
    ["sprites/mario/mario-normal-lift-left.png", (32, 200, 248)],
    ["sprites/mario/mario-normal-lift-right.png", (32, 200, 248)],
    ["sprites/mario/mario-normal-idlelift-left.png", (32, 200, 248)],
    ["sprites/mario/mario-normal-idlelift-right.png", (32, 200, 248)],
    ["sprites/mario/mario-normal-runlift-left.png", (32, 200, 248)],
    ["sprites/mario/mario-normal-runlift-right.png", (32, 200, 248)],
    ["sprites/mario/mario-normal-crouch-forward.png", (32, 200, 248)],
    ["sprites/mario/mario-normal-crouchlift-forward.png", (32, 200, 248)],
    ["sprites/mario/mario-normal-climbleft-back.png", (32, 200, 248)],
    ["sprites/mario/mario-normal-climbright-back.png", (32, 200, 248)],
    ["sprites/mario/mario-normal-push-left.png", (32, 200, 248)],
    ["sprites/mario/mario-normal-push-right.png", (32, 200, 248)],
    ["sprites/mario/mario-normal-run-left.png", (32, 200, 248)],
    ["sprites/mario/mario-normal-run-right.png", (32, 200, 248)],
    ["sprites/mario/mario-normal-waveleft-forward.png", (32, 200, 248)],
    ["sprites/mario/mario-normal-waveright-forward.png", (32, 200, 248)]
]

sprites = []

for file in sprite_files:
    imgsprite = pygame.image.load(file[0]).convert()
    pygame.Surface.set_colorkey(imgsprite, file[1])
    sprites.append(imgsprite)

class Mario():
    def __init__(self) -> None:
        self.x = x_percent(50)
        self.y = y_percent(50)
        self.x_velocity = 0
        self.y_velocity = 0
        self.state = MarioState.IDLE
        self.dir = MarioDirection.LEFT
        self.lifting = False
        self.crouching = False
        self.inAir = True # TODO set to false once physics is complete
        self.bounding_rectangle = None
    def updateState(self) -> None:
        if self.crouching == True:
            self.state = MarioState.CROUCH
            self.dir = MarioDirection.FORWARD
            # Crouching doesn't let you move, so can ignore rest of state update
            return
        if self.x_velocity < 0:
            # moving left
            self.dir = MarioDirection.LEFT
            self.state = MarioState.RUN
        if self.x_velocity > 0:
            # moving right
            self.state = MarioState.RUN
            self.dir = MarioDirection.RIGHT
        if self.x_velocity == 0:
            # idle (we have no faling animations at this point)
            self.state = MarioState.IDLE
            # Direction doesn't need to be changed
        # TODO
    def getAnim(self) -> int:
        anim = 0
        if self.state == MarioState.IDLE:
            if self.lifting == True:
                if self.dir == MarioDirection.LEFT:
                    anim = 7
                elif self.dir == MarioDirection.RIGHT:
                    anim = 8
            else:
                # set animation to sprite offset + direction integer
                offset = 0
                anim = offset + self.dir.value
        elif self.state == MarioState.RUN:
            if self.lifting == True:
                # Lifting animation
                if self.dir == MarioDirection.LEFT:
                    anim = 7
                elif self.dir == MarioDirection.RIGHT:
                    anim = 8
            else:
                # Normal run animation
                if self.dir == MarioDirection.LEFT:
                    anim = 15
                else:
                    anim = 16
        # print(self.state, self.dir, self.lifting, self.x_velocity, self.y_velocity, anim)
        return anim
    def draw(self) -> None:
        canvas.blit(sprites[self.getAnim()], dest=camera.world_to_camera(mario.x, mario.y))
    def physics(self, collidabletiles: list, canfall: bool) -> None:
        # Called once per tick
        # Computes physics
        # Get bounding box for current physics cycle
        self.bounding_rectangle = sprites[self.getAnim()].get_rect()
        self.bounding_rectangle.left, self.bounding_rectangle.top = camera.world_to_camera(self.x, self.y)
        # Tone movement speed down a bit (proper slowdown)
        self.x_velocity = self.x_velocity * 0.9
        self.y_velocity = self.y_velocity * 0.9
        # Physics
        if canfall == True:
            if self.y_velocity >= 0:
                if self.inAir:
                    self.y_velocity += 0.8
        colliding = False
        for tilegroup in collidabletiles:
            for tile in tilegroup.sprites():
                if self.bounding_rectangle.colliderect(tile.rect):
                    colliding = True
                    print("colliding with sprite")
        if colliding:
            self.x_velocity = -self.x_velocity
            self.y_velocity = -self.y_velocity
        # Movement speed clamp
        # X
        if self.x_velocity > max_x_velocity:
            # Above max right, set to max
            self.x_velocity = max_x_velocity
        elif self.x_velocity < -max_x_velocity:
            # Above max left, set to max
            self.x_velocity = -max_x_velocity
        elif self.x_velocity < 0.001 and self.x_velocity > -0.001:
            # Between left 0.001 and right 0.001, set to 0
            self.x_velocity = 0
        # Y
        if self.y_velocity > max_y_velocity:
            # Above max down, set to max
            self.y_velocity = max_y_velocity
        elif self.y_velocity < -max_y_velocity:
            # Above max up, set to max
            self.y_velocity = -max_y_velocity
        elif self.y_velocity < 0.001 and self.y_velocity > -0.001:
            # Between down 0.001 and up 0.001, set to 0
            self.y_velocity = 0
        # Check control type and void previous logic (there's probably a better place to put this)
        if (controltype == ControlType.CAMERA_SPRITE_MOVE):
            # ignore all physics if the camera mode is CAMERA_SPRITE_MOVE
            self.x_velocity = 0
            self.y_velocity = 0
            self.x, self.y = camera.camera_to_world(x_percent(50), y_percent(50))
            self.updateState()
            return
        # Adds velocity to X+Y
        self.x += self.x_velocity
        self.y += self.y_velocity
        # Update state
        self.updateState()
    def debug(self) -> None:
        font_size = 15
        font = pygame.font.SysFont(None, font_size)
        arr = []
        arr.append("W " + str(self.x) + " " + str(self.y))
        arr.append("C " + str(camera.world_to_camera(self.x, self.y)))
        arr.append("V " + str(self.x_velocity) + " " + str(self.y_velocity))
        counter = 0
        for text in arr:
            img = font.render(text, True, (255, 255, 255))
            canvas.blit(img, (0, counter))
            counter += font_size
        


class Background(pygame.sprite.Sprite):
    def __init__(self, image_file, location) -> None:
        pygame.sprite.Sprite.__init__(self)  #call Sprite initializer
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location
    def draw(self) -> None:
        canvas.blit(self.image, dest=camera.world_to_camera(self.rect.left, self.rect.top))

class Tile(pygame.sprite.Sprite):
    def __init__(self, image_file, location, keycolour) -> None:
        pygame.sprite.Sprite.__init__(self)  #call Sprite initializer
        self.image = pygame.image.load(image_file)
        pygame.Surface.set_colorkey(self.image, keycolour)
        self.rect = self.image.get_rect()
        self.worldx, self.worldy = location
    def update(self):
        self.rect.left, self.rect.top = camera.world_to_camera(self.worldx, self.worldy)
    def draw(self):
        # canvas.blit(self.image, dest=camera.world_to_camera(self.worldx, self.worldy))
        canvas.blit(self.image, dest=(self.rect.left, self.rect.top))


class Camera():
    def __init__(self, x=0, y=0) -> None:
        self.x = x
        self.y = y
    def move(self, movement_vector=(0,0)) -> None:
        self.x += movement_vector[0]
        self.y += movement_vector[1]
    def mariocheck(self) -> None:
        # if mario is at edge of camera move the camera to compensate
        checkpos = self.world_to_camera(mario.x, mario.y)
        if checkpos[0] >= x_percent(70) or checkpos[0] <= x_percent(20):
            # Move screen left or right (mario's direction)
            self.move((1 * mario.x_velocity, 0))
        if checkpos[1] >= y_percent(55) or checkpos[1] <= y_percent(45):
            # Move screen up or down (mario's direction)
            self.move((0, 1 * mario.y_velocity))
    def world_to_camera(self, x, y) -> int:
        return [x - camera.x, y - camera.y]
    def camera_to_world(self, x, y) -> int:
        return [x + camera.x, y + camera.y]

exit = False

mario = Mario()
bg = Background("bg/background.png", (0,0))
camera = Camera(0, 0)

controltype = ControlType.CONTROL
keepMarioInFrame = True

goRight = False
goLeft = False
goUp = False
goDown = False

# TODO REPLACE THIS CODE
worldtilegroup = pygame.sprite.RenderPlain()
for i in range(0, 256, 16):
    worldtilegroup.add(Tile("tiles/world/luckyblock.png", (i, 480), (60, 188, 252)))
# TODO END REPLACE THIS CODE


while not exit:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == ord('a'):
                goLeft = True
            if event.key == pygame.K_RIGHT or event.key == ord('d'):
                goRight = True
            if event.key == pygame.K_UP or event.key == ord('w'):
                goUp = True
            if event.key == pygame.K_DOWN or event.key == ord('s'):
                goDown = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == ord('a'):
                goLeft = False
            if event.key == pygame.K_RIGHT or event.key == ord('d'):
                goRight = False
            if event.key == pygame.K_UP or event.key == ord('w'):
                goUp = False
            if event.key == pygame.K_DOWN or event.key == ord('s'):
                goDown = False
    if controltype == ControlType.CONTROL:
        if goRight:
            if mario.x_velocity < 0:
                # Going right, cancel movement left
                mario.x_velocity = 0
            mario.x_velocity += 1
        elif goLeft:
            if mario.x_velocity > 0:
                mario.x_velocity = 0
            mario.x_velocity -= 1
    if controltype == ControlType.CAMERA or controltype == ControlType.CAMERA_SPRITE_MOVE:
        if goRight:
            camera.move((10, 0))
        if goLeft:
            camera.move((-10, 0))
        if goUp:
            camera.move((0, -10))
        if goDown:
            camera.move((0, 10))
    pygame.draw.rect(canvas, (60, 188, 252),  pygame.Rect(0, 0, snes_width, snes_height))
    bg.draw()
    # PLACEHOLDER DRAW CODE: TODO REPLACE 
    worldtilegroup.update()
    for worldtile in worldtilegroup.sprites():
        worldtile.draw()
    # END PLACEHOLDER DRAW CODE
    mario.physics([worldtilegroup], True)
    mario.draw()
    mario.debug() # DEBUG - REMOVE LATER
    if keepMarioInFrame:
        camera.mariocheck()
    pygame.display.update()
    # Wait for delta time (locked 50fps)
    clock.tick(50)
