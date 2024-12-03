from dynamic_physics import create_world, create_ground_segment
from car import create_car
from dynamic_game import game_loop
from Box2D.b2 import contactListener

class GameContactListener(contactListener):
    def __init__(self):
        contactListener.__init__(self)
        self.game_over = False

    def BeginContact(self, contact):
        body_a = contact.fixtureA.body
        body_b = contact.fixtureB.body
        if body_a.userData == "driver" or body_b.userData == "driver":
            self.game_over = True

if __name__ == "__main__":
    world = create_world()
    segments = []
    segment_width = 10
    loaded_distance = 50
    last_segment_x = 0

    while last_segment_x < loaded_distance:
        ground_segment = create_ground_segment(world, last_segment_x, width=segment_width)
        segments.append(ground_segment)
        last_segment_x += segment_width

    car_body, wheel1, wheel2, driver_body, joint1, joint2 = create_car(world)

    contact_listener = GameContactListener()
    world.contactListener = contact_listener

    game_loop(world, car_body, wheel1, wheel2, driver_body, segments, [joint1, joint2], contact_listener)