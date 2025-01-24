import pygame
from modules.settings import (
    screen, WIDTH, HEIGHT, WHITE, GROUND_COLOR, CAR_COLOR,
    WHEEL_COLOR, DRIVER_COLOR, BLACK, MAP_MIN_Y, END_X
)
from Box2D.b2 import polygonShape, circleShape

SCALE = 20

def draw_body(body, color, offset_x):
    if body.userData and "points" in body.userData:
        terrain_points = body.userData.get("points", [])
        if terrain_points:
            polygon_points = [
                (x * SCALE - offset_x, HEIGHT - y * SCALE) for (x, y) in terrain_points
            ]
            polygon_points.append((terrain_points[-1][0] * SCALE - offset_x, HEIGHT))
            polygon_points.append((terrain_points[0][0] * SCALE - offset_x, HEIGHT))
            pygame.draw.polygon(screen, GROUND_COLOR, polygon_points)
    else:
        for fixture in body.fixtures:
            shape = fixture.shape
            if isinstance(shape, polygonShape):
                vertices = [(body.transform * v) for v in shape.vertices]
                transformed = [
                    (v[0] * SCALE - offset_x, HEIGHT - v[1] * SCALE) for v in vertices
                ]
                pygame.draw.polygon(screen, color, transformed)
            elif isinstance(shape, circleShape):
                position = body.transform * shape.pos
                px = position[0] * SCALE - offset_x
                py = HEIGHT - position[1] * SCALE
                pygame.draw.circle(screen, color, (int(px), int(py)), int(shape.radius * SCALE))

def check_game_over(car_body, contact_listener):
    if contact_listener.game_over:
        print("Game Over! You fell!")
        return True

    if car_body.position[1] < MAP_MIN_Y:
        print("Game Over! You've fallen off the map!")
        return True

    if car_body.position[0] >= END_X:
        print("Congratulations! You've completed the map!")
        return True

    return False

def game_loop(world, car_body, wheel1, wheel2, driver_body, ground_body, joints, contact_listener, additional_bodies=[]):
    clock = pygame.time.Clock()
    offset_x = 0
    running = True

    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            joints[0].motorSpeed = -30.0
            joints[1].motorSpeed = -30.0
        elif keys[pygame.K_LEFT]:
            joints[0].motorSpeed = 30.0
            joints[1].motorSpeed = 30.0
        else:
            joints[0].motorSpeed = 0.0
            joints[1].motorSpeed = 0.0

        offset_x = car_body.position[0] * 20 - WIDTH / 2

        world.Step(1 / 60, 6, 2)

        if check_game_over(car_body, contact_listener):
            running = False

        draw_body(ground_body, GROUND_COLOR, offset_x)
        draw_body(car_body, CAR_COLOR, offset_x)
        draw_body(wheel1, WHEEL_COLOR, offset_x)
        draw_body(wheel2, WHEEL_COLOR, offset_x)
        draw_body(driver_body, DRIVER_COLOR, offset_x)

        for body in additional_bodies:
            draw_body(body, BLACK, offset_x)

        distance = int(car_body.position[0])
        font = pygame.font.Font(None, 36)
        text = font.render(f"Distance: {distance} m", True, BLACK)
        screen.blit(text, (10, 10))

        pygame.display.flip()
        clock.tick(60)