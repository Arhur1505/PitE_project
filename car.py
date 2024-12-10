from Box2D.b2 import polygonShape, circleShape

def create_car(world):
    # Podnieś pojazd wyżej, np. na y=20
    car_body = world.CreateDynamicBody(position=(5, 20))
    car_body.CreateFixture(
        shape=polygonShape(box=(1.5, 0.5)), density=1, friction=0.3
    )

    wheel1 = world.CreateDynamicBody(position=(4, 19))
    wheel2 = world.CreateDynamicBody(position=(6, 19))
    for wheel in [wheel1, wheel2]:
        wheel.CreateFixture(
            shape=circleShape(radius=0.5),
            density=1,
            friction=0.9,
            restitution=0.5
        )

    joint1 = world.CreateRevoluteJoint(
        bodyA=car_body,
        bodyB=wheel1,
        anchor=wheel1.position,
        collideConnected=False,
        maxMotorTorque=100.0,
        enableMotor=True
    )
    joint2 = world.CreateRevoluteJoint(
        bodyA=car_body,
        bodyB=wheel2,
        anchor=wheel2.position,
        collideConnected=False,
        maxMotorTorque=100.0,
        enableMotor=True
    )

    driver_body = world.CreateDynamicBody(position=(5, 20.9))
    driver_body.CreateFixture(
        shape=polygonShape(box=(0.4, 0.4)), density=1, friction=0.3
    )
    driver_body.userData = "driver"

    driver_joint = world.CreateWeldJoint(
        bodyA=car_body,
        bodyB=driver_body,
        anchor=(5, 20.75),
        collideConnected=False
    )

    return car_body, wheel1, wheel2, driver_body, joint1, joint2
