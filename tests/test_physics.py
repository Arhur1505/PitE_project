import unittest
from src.physics import Physics

class TestPhysics(unittest.TestCase):
    def test_physics_update(self):
        physics = Physics(
            mass=1000,
            engine_force=5000,
            brake_force=7000,
            friction=0.5,
            air_resistance=0.3,
        )
        physics.throttle = 1.0
        physics.brake = 0.0
        incline = 0  # Równy teren
        delta_time = 1/60

        initial_velocity = physics.velocity
        physics.update(incline, delta_time)
        self.assertTrue(physics.velocity > initial_velocity)

if __name__ == '__main__':
    unittest.main()
