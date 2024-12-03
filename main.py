import pygame
from Box2D.b2 import world, staticBody, dynamicBody, polygonShape, circleShape, contactListener

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
    shapes=polygonShape(box=(500, 1))  # Teren 50x1
)
ground_body.CreateFixture(
    shape=polygonShape(box=(50, 1)),
    density=0,
    friction=0.5,
    restitution=0.2  # Dodano odbicie dla ziemi
)

# Dodanie przeszkód na ziemi
ground_shape = ground_body.fixtures[0].shape
for i in range(10, 500, 10):
    ground_body.CreateFixture(
        shape=polygonShape(vertices=[(i, 0), (i + 2, 2), (i + 4, 0)]),
        density=0,
        friction=0.5,
        restitution=0.2  # Dodano odbicie dla przeszkód
    )

# Tworzenie pojazdu
car_body = world.CreateDynamicBody(position=(5, 2))
car_box = car_body.CreateFixture(
    shape=polygonShape(box=(1.5, 0.5)), density=1, friction=0.3
)

# Tworzenie kół
wheel1 = world.CreateDynamicBody(position=(4, 1))
wheel2 = world.CreateDynamicBody(position=(6, 1))
wheel1.CreateFixture(
    shape=circleShape(radius=0.5),
    density=1,
    friction=0.9,
    restitution=0.5  # Dodano odbicie dla kół
)
wheel2.CreateFixture(
    shape=circleShape(radius=0.5),
    density=1,
    friction=0.9,
    restitution=0.5  # Dodano odbicie dla kół
)

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
driver_body = world.CreateDynamicBody(position=(5, 2.9))  # Kierowca dotyka góry auta
driver_body.CreateFixture(
    shape=polygonShape(box=(0.4, 0.4)), density=1, friction=0.3  # Kwadratowe ciało kierowcy
)

# Połączenie kierowcy z samochodem
driver_joint = world.CreateWeldJoint(
    bodyA=car_body,
    bodyB=driver_body,
    anchor=(5, 2.75),
    collideConnected=False,
)

# Klasa do obsługi kolizji
class GameContactListener(contactListener):
    def __init__(self):
        contactListener.__init__(self)
        self.game_over = False

    def BeginContact(self, contact):
        # Sprawdź, czy kierowca dotknął ziemi
        body_a = contact.fixtureA.body
        body_b = contact.fixtureB.body
        if (body_a == driver_body and body_b == ground_body) or (body_b == driver_body and body_a == ground_body):
            self.game_over = True

# Ustawienie obsługi kolizji
contact_listener = GameContactListener()
world.contactListener = contact_listener


# Funkcja rysowania kierowcy
def draw_driver():
    draw_body(driver_body, DRIVER_COLOR)
# Dodaj zmienną przesunięcia
offset_x = 0

# Funkcja rysowania z przesunięciem
def draw_body(body, color):
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
    if keys[pygame.K_RIGHT]:  # Jazda w prawo i moment obrotowy w lewo
        joint1.motorSpeed = -30.0
        joint2.motorSpeed = -30.0
        car_body.ApplyTorque(10, True)
    elif keys[pygame.K_LEFT]:  # Jazda w lewo i moment obrotowy w prawo
        joint1.motorSpeed = 30.0
        joint2.motorSpeed = 30.0
        car_body.ApplyTorque(-10, True)
    else:
        joint1.motorSpeed = 0.0
        joint2.motorSpeed = 0.0

    # Aktualizacja przesunięcia ekranu na podstawie pozycji pojazdu
    offset_x = car_body.position[0] * 20 - WIDTH / 2

    # Symulacja fizyki
    world.Step(1 / FPS, 6, 2)

    # Sprawdzenie, czy gra się skończyła
    if contact_listener.game_over:
        print("Game Over!")
        running = False

    # Rysowanie ziemi, pojazdu i kierowcy
    draw_body(ground_body, GROUND_COLOR)
    draw_body(car_body, CAR_COLOR)
    draw_body(wheel1, WHEEL_COLOR)
    draw_body(wheel2, WHEEL_COLOR)
    draw_driver()

    # Aktualizacja ekranu
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()