SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Kolory
SKY_COLOR = (135, 206, 235)
GROUND_COLOR = (34, 139, 34)

# Stałe fizyczne
GRAVITY = 9.81  # Przyspieszenie grawitacyjne (m/s^2)

# Parametry pojazdu
CAR_MASS = 1000  # Masa pojazdu w kilogramach
CAR_ENGINE_FORCE = 15000  # Maksymalna siła silnika (N)
CAR_BRAKE_FORCE = 12000  # Siła hamowania (N)
CAR_FRICTION = 0.5  # Współczynnik tarcia
CAR_AIR_RESISTANCE = 0.3  # Opór powietrza (kg/m)

# Parametry kół
WHEEL_RADIUS = 0.34  # Promień koła w metrach
WHEEL_MASS = 20  # Masa koła w kilogramach
WHEEL_FRICTION = 0.9  # Współczynnik tarcia koła

# Inne
TIME_STEP = 1 / 60  # Czas pomiędzy klatkami (sekundy)

# Tryb renderowania (True - włączone, False - wyłączone)
RENDER_MODE = True