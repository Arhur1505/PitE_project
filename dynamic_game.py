import pygame
from settings import screen, WIDTH, HEIGHT, WHITE, GROUND_COLOR, CAR_COLOR, WHEEL_COLOR, DRIVER_COLOR
from Box2D.b2 import polygonShape, circleShape

def draw_body(body, color, offset_x):
    for fixture in body.fixtures:
        shape = fixture.shape
        if isinstance(shape, polygonShape):
            vertices = [(body.transform * v) for v in shape.vertices]
            vertices = [(v[0]*20 - offset_x, HEIGHT - v[1]*20) for v in vertices]
            pygame.draw.polygon(screen, color, vertices)
        elif hasattr(shape, 'vertices'):
            # chainShape
            vertices = [(body.transform * v) for v in shape.vertices]
            points = [(v[0]*20 - offset_x, HEIGHT - v[1]*20) for v in vertices]
            if len(points) > 1:
                pygame.draw.lines(screen, color, False, points, 3)
        elif isinstance(shape, circleShape):
            position = body.transform * shape.pos
            position = (position[0]*20 - offset_x, HEIGHT - position[1]*20)
            pygame.draw.circle(screen, color, (int(position[0]), int(position[1])), int(shape.radius*20))

def game_loop(world, car_body, wheel1, wheel2, driver_body, terrain_bodies, joints, contact_listener, initial_generated):
    clock = pygame.time.Clock()
    offset_x = 0
    running = True

    meters = 0  # Licznik metrów
    generated_up_to_x = initial_generated
    base_height = 5
    flat_until = 50

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

        offset_x = car_body.position[0]*20 - WIDTH/2
        meters = int(car_body.position[0])

        # Jeśli samochód zbliża się do końca wygenerowanego terenu, generuj nowy
        if car_body.position.x + 30 > generated_up_to_x:
            from dynamic_physics import generate_terrain_points, create_terrain_body
            new_start = generated_up_to_x
            new_end = new_start + 50  # generujemy kolejny fragment 50m
            new_points = generate_terrain_points(new_start, new_end, step=5, base_height=base_height, flat_until=flat_until)
            new_body = create_terrain_body(world, new_points)
            terrain_bodies.append(new_body)
            generated_up_to_x = new_end

        world.Step(1/60, 6, 2)

        if contact_listener.game_over:
            print("Game Over!")
            running = False

        # Rysowanie terenu
        for body in terrain_bodies:
            draw_body(body, GROUND_COLOR, offset_x)

        draw_body(car_body, CAR_COLOR, offset_x)
        draw_body(wheel1, WHEEL_COLOR, offset_x)
        draw_body(wheel2, WHEEL_COLOR, offset_x)
        draw_body(driver_body, DRIVER_COLOR, offset_x)

        # Wyświetlanie licznika metrów
        font = pygame.font.Font(None, 36)
        text = font.render(f"Distance: {meters} m", True, (0, 0, 0))
        screen.blit(text, (10, 10))

        pygame.display.flip()
        clock.tick(60)
