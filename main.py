from modules.car import create_car
from modules.game import game_loop
from modules.physics import create_world, GameContactListener


def main():
    try:
        # Tworzenie świata i kuli
        world, ball_body = create_world()

        # Znalezienie obiektu ground_body w świecie
        ground_body = next(
            (body for body in world.bodies if body.userData and "points" in body.userData),
            None
        )
        if ground_body is None:
            raise ValueError("Ground body not found in the world!")

        # Tworzenie samochodu
        car_body, wheel1, wheel2, driver_body, joint1, joint2 = create_car(world)

        # Ustawienie contact listener
        contact_listener = GameContactListener()
        world.contactListener = contact_listener

        # Rozpoczęcie pętli gry
        game_loop(
            world, car_body, wheel1, wheel2, driver_body, ground_body,
            [joint1, joint2], contact_listener, additional_bodies=[ball_body]
        )

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()