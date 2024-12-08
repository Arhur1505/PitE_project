import Box2D
from Box2D.b2 import world, staticBody, chainShape
import math
from noise import pnoise1


def create_world():
    physics_world = world(gravity=(0, -10), doSleep=True)

    # Parametry terenu
    start_x = 0
    end_x = 1000
    base_height = 5
    amplitude = 5
    frequency = 0.022  # Im mniejsza wartość, tym wolniejsze zmiany wysokości

    dense_points = []
    for x in range(start_x, end_x + 1):
        # Generujemy wysokość na podstawie perlin noise
        noise_val = pnoise1(x * frequency+0.25)  # zakres -1 do 1
        y = base_height + noise_val * amplitude
        dense_points.append((float(x), float(y)))

    ground_body = physics_world.CreateStaticBody()
    ground_body.CreateFixture(
        shape=chainShape(vertices=dense_points),
        density=0,
        friction=0.6,
        restitution=0.2
    )

    ground_body.userData = {
        "points": dense_points,
        "start_x": start_x,
        "end_x": end_x
    }

    return physics_world, ground_body
