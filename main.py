import pygame
import Box2D
from Box2D.b2 import world, staticBody, dynamicBody, polygonShape, circleShape

# Inicjalizacja Pygame i ustawienia
pygame.init()
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
FPS = 60

# Kolory
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GROUND_COLOR = (100, 200, 100)
CAR_COLOR = (200, 0, 0)
WHEEL_COLOR = (0, 0, 0)
DRIVER_COLOR = (50, 50, 200)

# Inicjalizacja Box2D
world = world(gravity=(0, -10), doSleep=True)

# Tworzenie ziemi
ground_body = world.CreateStaticBody(
    position=(0, 0),
    shapes=polygonShape(box=(50, 1))  # Teren 50x1
)

# Dodanie przeszkód na ziemi
ground_shape = ground_body.fixtures[0].shape
for i in range(10, 50, 10):
    ground_body.CreateFixture(
        shape=polygonShape(vertices=[(i, 0), (i + 2, 2), (i + 4, 0)]),
        density=0,
        friction=0.5,
    )

# Tworzenie pojazdu
car_body = world.CreateDynamicBody(position=(5, 2))
car_box = car_body.CreateFixture(
    shape=polygonShape(box=(1.5, 0.5)), density=1, friction=0.3
)

# Tworzenie kół
wheel1 = world.CreateDynamicBody(position=(4, 1))
wheel2 = world.CreateDynamicBody(position=(6, 1))
wheel1.CreateFixture(shape=circleShape(radius=0.5), density=1, friction=0.9)
wheel2.CreateFixture(shape=circleShape(radius=0.5), density=1, friction=0.9)

# Połączenie kół z nadwoziem
joint1 = world.CreateRevoluteJoint(
    bodyA=car_body,
    bodyB=wheel1,
    anchor=wheel1.position,
    collideConnected=False,
    maxMotorTorque=100.0,
    enableMotor=True,
)

joint2 = world.CreateRevoluteJoint(
    bodyA=car_body,
    bodyB=wheel2,
    anchor=wheel2.position,
    collideConnected=False,
    maxMotorTorque=100.0,
    enableMotor=True,
)

# Tworzenie kierowcy
driver_body = world.CreateDynamicBody(position=(5, 2.75))  # Kierowca dotyka góry auta
driver_body.CreateFixture(
    shape=polygonShape(box=(0.3, 0.5)), density=1, friction=0.3  # Prostokątne ciało
)

# Połączenie kierowcy z samochodem
driver_joint = world.CreateWeldJoint(
    bodyA=car_body,
    bodyB=driver_body,
    anchor=(5, 2.75),
    collideConnected=False,
)

# Funkcja rysowania
def draw_body(body, color):
    for fixture in body.fixtures:
        shape = fixture.shape
        if isinstance(shape, polygonShape):
            vertices = [(body.transform * v) * 20 for v in shape.vertices]
            vertices = [(v[0], HEIGHT - v[1]) for v in vertices]
            pygame.draw.polygon(screen, color, vertices)
        elif isinstance(shape, circleShape):
            position = body.transform * shape.pos * 20
            position = (int(position[0]), int(HEIGHT - position[1]))
            pygame.draw.circle(screen, color, position, int(shape.radius * 20))

# Funkcja rysowania kierowcy
def draw_driver():
    draw_body(driver_body, DRIVER_COLOR)  # Rysowanie prostokątnego ciała kierowcy

# Pętla gry
running = True
while running:
    screen.fill(WHITE)

    # Obsługa zdarzeń
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Sterowanie
    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT]:  # Jazda w prawo
        joint1.motorSpeed = -20.0
        joint2.motorSpeed = -20.0
    elif keys[pygame.K_LEFT]:  # Jazda w lewo
        joint1.motorSpeed = 20.0
        joint2.motorSpeed = 20.0
    else:
        joint1.motorSpeed = 0.0
        joint2.motorSpeed = 0.0

    if keys[pygame.K_UP]:  # Obrót w lewo
        car_body.ApplyTorque(50, True)
    if keys[pygame.K_DOWN]:  # Obrót w prawo
        car_body.ApplyTorque(-50, True)

    # Symulacja fizyki
    world.Step(1 / FPS, 6, 2)

    # Rysowanie ziemi, pojazdu i kierowcy
    draw_body(ground_body, GROUND_COLOR)
    draw_body(car_body, CAR_COLOR)
    draw_body(wheel1, WHEEL_COLOR)
    draw_body(wheel2, WHEEL_COLOR)
    draw_driver()  # Rysowanie kierowcy

    # Aktualizacja ekranu
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
