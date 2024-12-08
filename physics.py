import Box2D
from Box2D.b2 import world, staticBody, polygonShape

def create_world():
    physics_world = world(gravity=(0, -10), doSleep=True)

    ground_body = physics_world.CreateStaticBody(
        position=(0, 0),
        shapes=polygonShape(box=(500, 1))
    )
    ground_body.CreateFixture(
        shape=polygonShape(box=(500, 1)),
        density=0,
        friction=0.5,
        restitution=0.2
    )

    for i in range(10, 1000, 10):
        ground_body.CreateFixture(
            shape=polygonShape(vertices=[(i, 0), (i + 2, 2), (i + 4, 0)]),
            density=0,
            friction=0.5,
            restitution=0.2
        )

    return physics_world, ground_body
