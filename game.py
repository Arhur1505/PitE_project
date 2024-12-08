import pygame
from settings import screen, WIDTH, HEIGHT, WHITE, GROUND_COLOR, CAR_COLOR, WHEEL_COLOR, DRIVER_COLOR, BLACK

def draw_body(body, color, offset_x):
    from Box2D.b2 import polygonShape, circleShape, chainShape

    SCALE = 20
    if body.userData and "points" in body.userData:
        terrain_points = body.userData["points"]
        line_points = []
        for (x,y) in terrain_points:
            px = x * SCALE - offset_x
            py = HEIGHT - (y * SCALE)
            line_points.append((px, py))
        # Rysujemy linię terenu
        pygame.draw.lines(screen, color, False, line_points, 3)
    else:
        # Rysowanie innych ciał (auto, koła, kierowca)
        for fixture in body.fixtures:
            shape = fixture.shape
            if isinstance(shape, polygonShape):
                vertices = [(body.transform * v) for v in shape.vertices]
                transformed = []
                for v in vertices:
                    px = v[0]*SCALE - offset_x
                    py = HEIGHT - v[1]*SCALE
                    transformed.append((px, py))
                pygame.draw.polygon(screen, color, transformed)
            elif isinstance(shape, circleShape):
                position = body.transform * shape.pos
                px = position[0]*SCALE - offset_x
                py = HEIGHT - position[1]*SCALE
                pygame.draw.circle(screen, color, (int(px), int(py)), int(shape.radius*SCALE))

def game_loop(world, car_body, wheel1, wheel2, driver_body, ground_body, joints, contact_listener):
    clock = pygame.time.Clock()
    offset_x = 0
    running = True

    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Sterowanie
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

        offset_x = car_body.position[0]*20 - WIDTH / 2

        world.Step(1/60, 6, 2)

        if contact_listener.game_over:
            print("Game Over!")
            running = False

        # Rysowanie terenu i obiektów
        draw_body(ground_body, GROUND_COLOR, offset_x)
        draw_body(car_body, CAR_COLOR, offset_x)
        draw_body(wheel1, WHEEL_COLOR, offset_x)
        draw_body(wheel2, WHEEL_COLOR, offset_x)
        draw_body(driver_body, DRIVER_COLOR, offset_x)

        # Wyświetlanie licznika odległości
        distance = int(car_body.position[0])
        font = pygame.font.Font(None, 36)
        text = font.render(f"Distance: {distance} m", True, BLACK)
        screen.blit(text, (10, 10))

        pygame.display.flip()
        clock.tick(60)
