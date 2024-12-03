import pygame
import circle
import Box2D
from Box2D.b2 import world

BLUE = (0, 0, 255)
X_INIT = 100
Y_INIT = 150
RADIUS = 20

_width = 1200
_length = 600
_step_size = 20

pygame.init()
screen = pygame.display.set_mode((_width, _length))
clock = pygame.time.Clock()

world = world(gravity=(0, 10))

_file = open("map_file.txt", "r")
_just_y_list = list(map(float, _file.read().split()))
_file.close()

_height_values = [(x * _step_size, _length - y) for x, y in enumerate(_just_y_list)]

def scale_to_meters(x):
    return x / 50

def scale_to_pixels(x):
    return x * 50

_arter_scaleing_height_values = [(scale_to_meters(x) * (_step_size), scale_to_meters(_length) - scale_to_meters(y)) for x, y in enumerate(_just_y_list)]

# tenen w box2D
for i in range(len(_height_values) - 1):
    current = _arter_scaleing_height_values[i]
    next = _arter_scaleing_height_values[i + 1]
    world.CreateStaticBody(
        shapes = Box2D.b2EdgeShape(
            vertices = [current, next]
        )
    )

dynamic_circle = world.CreateDynamicBody(position = (scale_to_meters(X_INIT), scale_to_meters(Y_INIT)))
dynamic_circle.CreateCircleFixture(
    radius = scale_to_meters(20),
    density = 10,
    friction = 0.3,
    restitution = 0.5,
)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.draw.lines(screen, (255, 255, 255), False, _height_values , 5)
    
    position = dynamic_circle.position
    pixel_position = (scale_to_pixels(position[0]), scale_to_pixels(position[1]))
    
    _object = circle.Circle(20, pixel_position)
    _object.draw(screen)
    
    world.Step(1/60, 6, 2)
    
    clock.tick(60)
    pygame.display.flip()
    screen.fill((0, 0, 0))

pygame.quit()