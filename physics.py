import Box2D
from Box2D.b2 import world, staticBody, polygonShape
from noise import pnoise1
import numpy as np

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

    contact_listener = CustomContactListener()
    physics_world.contactListener = contact_listener

    start_x = -10
    end_x = 1000
    base_height = 5
    amplitude = 5
    frequency = 0.022

    step = 0.2
    x_values = np.arange(start_x, end_x + step, step)
    dense_points = [
        (float(x), float(base_height + pnoise1(x * frequency + 0.25) * amplitude))
        for x in x_values
    ]

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

    return physics_world, ground_body