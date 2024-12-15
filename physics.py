import Box2D
from Box2D.b2 import world, staticBody, polygonShape
import math
from noise import pnoise1
import numpy as np

def create_world():
    physics_world = world(gravity=(0, -10), doSleep=True)

    start_x = -10
    end_x = 1000
    base_height = 5
    amplitude = 5
    frequency = 0.022

    step = 0.2
    x_values = np.arange(start_x, end_x+step, step)

    dense_points = []
    for x in x_values:
        noise_val = pnoise1(x * frequency + 0.25)
        y = base_height + noise_val * amplitude
        dense_points.append((float(x), float(y)))

    ground_body = physics_world.CreateStaticBody()

    max_vertices = 14
    i = 0
    n = len(dense_points)

    while i < n:
        segment_points = dense_points[i:i+max_vertices]
        if len(segment_points) < 2:
            break

        x_start = segment_points[0][0]
        x_end = segment_points[-1][0]

        polygon_points = list(segment_points)
        polygon_points.append((x_end, 0.0))
        polygon_points.append((x_start, 0.0))

        ground_body.CreateFixture(
            shape=polygonShape(vertices=polygon_points),
            density=0,
            friction=0.6,
            restitution=0.2
        )

        i += max_vertices

    ground_body.userData = {
        "points": dense_points,
        "start_x": start_x,
        "end_x": end_x
    }

    return physics_world, ground_body
