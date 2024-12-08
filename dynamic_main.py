from dynamic_physics import create_world, generate_terrain_points, create_terrain_body
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
        if getattr(body_a, 'userData', None) == "driver" or getattr(body_b, 'userData', None) == "driver":
            self.game_over = True

if __name__ == "__main__":
    world = create_world()

    base_height = 5
    flat_until = 50

    # Generujemy pierwszy fragment terenu (np. do x=50, całość płaska)
    initial_points = generate_terrain_points(0, 50, step=5, base_height=base_height, flat_until=flat_until)
    terrain_body = create_terrain_body(world, initial_points)
    terrain_bodies = [terrain_body]

    car_body, wheel1, wheel2, driver_body, joint1, joint2 = create_car(world)

    contact_listener = GameContactListener()
    world.contactListener = contact_listener

    game_loop(world, car_body, wheel1, wheel2, driver_body, terrain_bodies, [joint1, joint2], contact_listener, initial_generated=50)
