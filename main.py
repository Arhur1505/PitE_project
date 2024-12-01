import pygame
import Box2D
from Box2D.b2 import world, vec2, polygonShape, circleShape, revoluteJointDef

BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
X_INIT = 100
Y_INIT = 150
CAR_WIDTH = 80
CAR_HEIGHT = 20
WHEEL_RADIUS = 15

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


_arter_scaleing_height_values = [
    (scale_to_meters(x) * (_step_size), scale_to_meters(_length) - scale_to_meters(y))
    for x, y in enumerate(_just_y_list)
]

# Create static bodies for the ground in Box2D
for i in range(len(_height_values) - 1):
    current = _arter_scaleing_height_values[i]
    next = _arter_scaleing_height_values[i + 1]
    world.CreateStaticBody(
        shapes=Box2D.b2EdgeShape(
            vertices=[current, next]
        )
    )

# Create the car body
car_body = world.CreateDynamicBody(position=(scale_to_meters(X_INIT), scale_to_meters(Y_INIT)))
car_box = car_body.CreatePolygonFixture(
    box=(scale_to_meters(CAR_WIDTH / 2), scale_to_meters(CAR_HEIGHT / 2)),
    density=1.0,
    friction=0.3,
    restitution=0.3,
)

# Create the wheels
left_wheel = world.CreateDynamicBody(position=(
    scale_to_meters(X_INIT - CAR_WIDTH / 2 + WHEEL_RADIUS),
    scale_to_meters(Y_INIT + CAR_HEIGHT / 2)
))
left_wheel.CreateCircleFixture(
    radius=scale_to_meters(WHEEL_RADIUS),
    density=1.0,
    friction=0.9,
    restitution=0.1,
)

right_wheel = world.CreateDynamicBody(position=(
    scale_to_meters(X_INIT + CAR_WIDTH / 2 - WHEEL_RADIUS),
    scale_to_meters(Y_INIT + CAR_HEIGHT / 2)
))
right_wheel.CreateCircleFixture(
    radius=scale_to_meters(WHEEL_RADIUS),
    density=1.0,
    friction=0.9,
    restitution=0.1,
)

# Connect the wheels to the car using revolute joints
joint_def_left = revoluteJointDef(
    bodyA=car_body,
    bodyB=left_wheel,
    localAnchorA=vec2(scale_to_meters(-CAR_WIDTH / 2 + WHEEL_RADIUS), scale_to_meters(CAR_HEIGHT / 2)),
    localAnchorB=vec2(0, 0),
    enableMotor=False
)
world.CreateJoint(joint_def_left)

joint_def_right = revoluteJointDef(
    bodyA=car_body,
    bodyB=right_wheel,
    localAnchorA=vec2(scale_to_meters(CAR_WIDTH / 2 - WHEEL_RADIUS), scale_to_meters(CAR_HEIGHT / 2)),
    localAnchorB=vec2(0, 0),
    enableMotor=False
)
world.CreateJoint(joint_def_right)

# Define force magnitude
force_magnitude = 50.0

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Check for key presses to control the car
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        left_wheel.ApplyTorque(-force_magnitude, wake=True)
        right_wheel.ApplyTorque(-force_magnitude, wake=True)
    if keys[pygame.K_RIGHT]:
        left_wheel.ApplyTorque(force_magnitude, wake=True)
        right_wheel.ApplyTorque(force_magnitude, wake=True)

    # Draw the terrain
    pygame.draw.lines(screen, WHITE, False, _height_values, 5)

    # Draw the car body
    car_position = car_body.position
    car_angle = car_body.angle
    car_pixel_position = (scale_to_pixels(car_position[0]), scale_to_pixels(car_position[1]))
    car_rect = pygame.Rect(0, 0, CAR_WIDTH, CAR_HEIGHT)
    car_rect.center = car_pixel_position
    pygame.draw.rect(screen, BLUE, car_rect)

    # Draw the wheels
    left_wheel_position = left_wheel.position
    left_wheel_pixel_position = (scale_to_pixels(left_wheel_position[0]), scale_to_pixels(left_wheel_position[1]))
    pygame.draw.circle(screen, BLUE, left_wheel_pixel_position, WHEEL_RADIUS)

    right_wheel_position = right_wheel.position
    right_wheel_pixel_position = (scale_to_pixels(right_wheel_position[0]), scale_to_pixels(right_wheel_position[1]))
    pygame.draw.circle(screen, BLUE, right_wheel_pixel_position, WHEEL_RADIUS)

    # Step the Box2D simulation
    world.Step(1 / 60, 6, 2)

    clock.tick(60)
    pygame.display.flip()
    screen.fill((0, 0, 0))

pygame.quit()
