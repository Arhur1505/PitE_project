from Box2D.b2 import world, staticBody, polygonShape

def create_world():
    physics_world = world(gravity=(0, -10), doSleep=True)
    return physics_world

def create_ground_segment(world, start_x, width=10):
    ground_body = world.CreateStaticBody(
        position=(start_x, 0),
        shapes=polygonShape(box=(width / 2, 1))
    )
    ground_body.CreateFixture(
        shape=polygonShape(box=(width / 2, 1)),
        density=0,
        friction=0.5,
        restitution=0.2
    )
    return ground_body