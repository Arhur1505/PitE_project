from physics import create_world
from car import create_car
from game import game_loop
from Box2D.b2 import contactListener


class GameContactListener(contactListener):
    """
    Custom contact listener to detect collisions between the driver and ground.
    If a collision is detected, the game ends.
    """

    def __init__(self):
        contactListener.__init__(self)
        self.game_over = False

    def BeginContact(self, contact):
        body_a = contact.fixtureA.body
        body_b = contact.fixtureB.body
        if (getattr(body_a, 'userData', None) == "driver" and body_b.type == 0) or \
           (getattr(body_b, 'userData', None) == "driver" and body_a.type == 0):
            self.game_over = True


def main():
    try:
        # Create the physics world and objects
        world, ground_body, box_body, ball_body = create_world()  # Upewnij się, że funkcja zwraca wszystkie obiekty
        car_body, wheel1, wheel2, driver_body, joint1, joint2 = create_car(world)

        # Initialize the contact listener
        contact_listener = GameContactListener()
        world.contactListener = contact_listener

        # Start the game loop, including additional objects
        game_loop(
            world, car_body, wheel1, wheel2, driver_body, ground_body,
            [joint1, joint2], contact_listener, additional_bodies=[box_body, ball_body]
        )

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
