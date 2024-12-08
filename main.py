from physics import create_world
from car import create_car
from game import game_loop
from Box2D.b2 import contactListener

class GameContactListener(contactListener):
    def __init__(self):
        contactListener.__init__(self)
        self.game_over = False

    def BeginContact(self, contact):
        body_a = contact.fixtureA.body
        body_b = contact.fixtureB.body
        if (getattr(body_a, 'userData', None) == "driver" and body_b.type == 0) or \
           (getattr(body_b, 'userData', None) == "driver" and body_a.type == 0):
            self.game_over = True

if __name__ == "__main__":
    world, ground_body = create_world()
    car_body, wheel1, wheel2, driver_body, joint1, joint2 = create_car(world)

    contact_listener = GameContactListener()
    world.contactListener = contact_listener

    game_loop(world, car_body, wheel1, wheel2, driver_body, ground_body, [joint1, joint2], contact_listener)
