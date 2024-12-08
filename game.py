import pygame
from settings import screen, WIDTH, HEIGHT, WHITE, GROUND_COLOR, CAR_COLOR, WHEEL_COLOR, DRIVER_COLOR, BLACK

def draw_body(body, color, offset_x):
    from Box2D.b2 import polygonShape, circleShape
    for fixture in body.fixtures:
        shape = fixture.shape
        if isinstance(shape, polygonShape):
            vertices = [(body.transform * v) * 20 for v in shape.vertices]
            vertices = [(v[0] - offset_x, HEIGHT - v[1]) for v in vertices]
            pygame.draw.polygon(screen, color, vertices)
        elif isinstance(shape, circleShape):
            position = body.transform * shape.pos * 20
            position = (int(position[0] - offset_x), int(HEIGHT - position[1]))
            pygame.draw.circle(screen, color, position, int(shape.radius * 20))

def game_loop(world, car_body, wheel1, wheel2, driver_body, ground_body, joints, contact_listener):
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

        if contact_listener.game_over:
            print("Game Over!")
            running = False

        draw_body(ground_body, GROUND_COLOR, offset_x)
        draw_body(car_body, CAR_COLOR, offset_x)
        draw_body(wheel1, WHEEL_COLOR, offset_x)
        draw_body(wheel2, WHEEL_COLOR, offset_x)
        draw_body(driver_body, DRIVER_COLOR, offset_x)

        distance = int(car_body.position[0])  # w metrach
        font = pygame.font.Font(None, 36)
        text = font.render(f"Distance: {distance} m", True, BLACK)
        screen.blit(text, (10, 10))

        pygame.display.flip()
        clock.tick(60)
