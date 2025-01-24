import Box2D
from Box2D.b2 import world, staticBody, dynamicBody, polygonShape, circleShape
from noise import pnoise1
import numpy as np
import random

class CustomContactListener(Box2D.b2.contactListener):
    def __init__(self):
        super().__init__()
        self.contacts = {}

    def BeginContact(self, contact):
        self.contacts[contact.fixtureA] = True
        self.contacts[contact.fixtureB] = True

    def EndContact(self, contact):
        self.contacts[contact.fixtureA] = False
        self.contacts[contact.fixtureB] = False

    def is_touching(self, fixture):
        return self.contacts.get(fixture, False)

def create_world():
    physics_world = world(gravity=(0, -10), doSleep=True)

    start_x = 0
    end_x = 500
    base_height = 6
    amplitude = 5.5
    frequency = 0.04

    random_seed = random.randint(0, 1000000)
    noise_offset = random_seed * 0.01

    step = 0.2
    x_values = np.arange(start_x, end_x + step, step)

    dense_points = []
    first_noise_val = pnoise1(10 * frequency + noise_offset)
    flat_height = base_height + first_noise_val * amplitude

    for x in x_values:
        if x < 10:
            y = flat_height
        else:
            noise_val = pnoise1(x * frequency + noise_offset)
            y = base_height + noise_val * amplitude
        dense_points.append((float(x), float(y)))

    min_amplitude = float('inf')
    ramp_start_index = 0
    ramp_length = int(15 / step)

    for i in range(int(25 / step), len(dense_points) - ramp_length):
        segment = dense_points[i:i + ramp_length]
        y_values = [point[1] for point in segment]
        amplitude_segment = max(y_values) - min(y_values)
        if amplitude_segment < min_amplitude:
            min_amplitude = amplitude_segment
            ramp_start_index = i

    ramp_points = []
    ramp_peak_index = ramp_length // 2
    ramp_height = 5
    gap_width = 15

    for j, (x, y) in enumerate(dense_points[ramp_start_index:ramp_start_index + ramp_length]):
        if j < ramp_peak_index:
            new_y = y + (j / ramp_peak_index) * ramp_height
        elif j >= ramp_peak_index + gap_width:
            new_y = y + ((ramp_length - j) / (ramp_length - ramp_peak_index - gap_width)) * ramp_height
        else:
            new_y = base_height - 1

        ramp_points.append((x, new_y))
        dense_points[ramp_start_index + j] = (x, new_y)

    ground_body = physics_world.CreateStaticBody()

    max_vertices = 14
    i = 0
    n = len(dense_points)

    while i < n:
        segment_points = dense_points[i:i + max_vertices]
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

    ground_body.userData = {"points": dense_points}

    ball_position_index = max(0, ramp_start_index - 5)
    ball_position = (
        dense_points[ball_position_index][0],
        dense_points[ball_position_index][1] + 5
    )

    ball_body = physics_world.CreateDynamicBody(
        position=ball_position,
        fixtures=Box2D.b2FixtureDef(
            shape=circleShape(radius=1),
            density=0.5,
            friction=0.5,
            restitution=0.8
        )
    )
    ball_body.userData = {"type": "falling_ball"}

    return physics_world, ground_body, ball_body