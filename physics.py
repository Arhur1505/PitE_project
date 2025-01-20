import Box2D
from Box2D.b2 import world, staticBody, dynamicBody, polygonShape, circleShape
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

    start_x = 0
    end_x = 1000
    base_height = 4
    amplitude = 6
    frequency = 0.07

    step = 0.2
    x_values = np.arange(start_x, end_x + step, step)
    dense_points = []
    ramp_array = []

    for value in x_values:
        if value > 45 and value < 70:
            height = dense_points[-1][1] + 0.1
            ramp_array.append((value, height))
            
        elif value > 75 and value < 100:
            height = ramp_array[-1][1]
            ramp_array.remove(ramp_array[-1])
        else:
            height = base_height + pnoise1(value * frequency + 0.25) * amplitude
        dense_points.append((float(value), float(height)))

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

    box_position = (50, base_height + 5)
    box_body = physics_world.CreateDynamicBody(
        position=box_position,
        fixtures=Box2D.b2FixtureDef(
            shape=polygonShape(box=(1, 1)),
            density=0.1,
            friction=0.2,
            restitution=0.1
        )
    )
    box_body.userData = {"type": "pushable_object"}

    ball_position = (60, base_height + 30)
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

    return physics_world, ground_body, box_body, ball_body
