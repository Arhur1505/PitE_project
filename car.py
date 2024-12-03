from Box2D.b2 import dynamicBody, polygonShape, circleShape

def create_car(world):
    # Tworzenie pojazdu
    car_body = world.CreateDynamicBody(position=(5, 2))
    car_body.CreateFixture(
        shape=polygonShape(box=(1.5, 0.5)), density=1, friction=0.3
    )

    # Tworzenie kół
    wheel1 = world.CreateDynamicBody(position=(4, 1))
    wheel2 = world.CreateDynamicBody(position=(6, 1))
    for wheel in [wheel1, wheel2]:
        wheel.CreateFixture(
            shape=circleShape(radius=0.5),
            density=1,
            friction=0.9,
            restitution=0.5
        )

    # Połączenie kół z nadwoziem
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

    # Tworzenie kierowcy
    driver_body = world.CreateDynamicBody(position=(5, 2.9))
    driver_body.CreateFixture(
        shape=polygonShape(box=(0.4, 0.4)), density=1, friction=0.3
    )
    driver_body.userData = "driver"  # Dodanie userData

    # Połączenie kierowcy z samochodem
    driver_joint = world.CreateWeldJoint(
        bodyA=car_body,
        bodyB=driver_body,
        anchor=(5, 2.75),
        collideConnected=False
    )

    return car_body, wheel1, wheel2, driver_body, joint1, joint2
