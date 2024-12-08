from Box2D.b2 import world, staticBody, chainShape
import random
from scipy.interpolate import CubicSpline

def create_world():
    physics_world = world(gravity=(0, -10), doSleep=True)
    return physics_world


def generate_hilly_points(start_x, end_x, step, base_height):
    key_x = list(range(start_x, end_x + 1, step))
    key_y = [random.uniform(-2, 2) + base_height for _ in key_x]

    if len(key_x) < 4:
        # Jeśli za mało punktów do spline, po prostu zwróć liniową interpolację
        return list(zip(key_x, key_y))

    cs = CubicSpline(key_x, key_y)
    dense_points = []
    for x in range(start_x, end_x + 1):
        y = cs(x)
        dense_points.append((float(x), float(y)))
    return dense_points


def generate_terrain_points(start_x, end_x, step=5, base_height=5, flat_until=50, start_point=None):
    """
    Generuje płynne punkty terenu pomiędzy start_x a end_x.
    Do 'flat_until' teren jest płaski na wysokości base_height.
    Po przekroczeniu flat_until zaczynamy generować górki z CubicSpline.
    Jeżeli start_point jest podany (x, y), to używamy go jako pierwszego punktu,
    a start_x dostosowujemy do start_point[0].
    """

    points = []
    if start_point is not None:
        # Upewniamy się, że start_x pokrywa się z start_point.x
        start_x = int(start_point[0])
        # Dodajemy punkt startowy na początek
        points.append(start_point)
        current_height = start_point[1]
    else:
        # Jeżeli brak punktu startowego, przyjmij płaski teren na start
        points.append((start_x, base_height))
        current_height = base_height

    # Teraz musimy wygenerować pozostałe punkty od (start_x+1) do end_x (o ile jest dalej niż start_x)
    if end_x <= start_x:
        # Jeśli end_x jest równy lub mniejszy od start_x, nic nie generujemy
        return points

    # Zakładamy, że pierwszy już jest, więc generujemy od start_x+1 do end_x
    segment_start = start_x
    segment_end = end_x

    # Sprawdzamy, w którym rejonie się znajdujemy (płaski, górzysty, czy mieszany)
    if segment_end <= flat_until:
        # Cały nowy fragment jest płaski
        # Punkt startowy już dodany, generujemy kolejne
        for x in range(segment_start + 1, segment_end + 1):
            points.append((x, base_height))
    elif segment_start >= flat_until:
        # Cały fragment jest górzysty
        # Kluczowe: start_point musi być uwzględniony w spline
        # Aby spline był ciągły, możemy dorzucić start_point do key_points
        # jednak nasza funkcja generate_hilly_points zaczyna od zera.
        # Możemy to rozwiązać dwojako:
        # 1. Zmodyfikować generate_hilly_points aby przyjmowała startową wysokość.
        # 2. Wygenerować hilly_points i upewnić się, że pierwszy punkt pokrywa się z start_point.

        # Najprościej na razie zakładamy, że jeśli mamy start_point w górach,
        # to po prostu generujemy hilly_points i nadpisujemy pierwszy punkt.

        hilly = generate_hilly_points(segment_start, segment_end, step, base_height)
        # Pierwszy punkt hilly odpowiada segment_start, my już mamy start_point w points.
        # Aby zachować ciągłość, możemy usunąć pierwszy punkt z hilly, bo już go mamy w 'points'.
        # Ale TYLKO jeśli start_point jest faktycznie tym samym x-em
        if points[-1][0] == hilly[0][0]:
            hilly = hilly[1:]  # pomijamy pierwszy punkt hilly, bo już go mamy
        points.extend(hilly)
    else:
        # Częściowo płaski, częściowo górzysty
        # Do flat_until płasko, potem górki
        flat_part_end = flat_until

        # Najpierw płaski kawałek do flat_until
        for x in range(segment_start + 1, flat_part_end + 1):
            points.append((x, base_height))

        # Następnie górzysty kawałek od flat_until+1 do segment_end
        hilly = generate_hilly_points(flat_until + 1, segment_end, step, base_height)
        # Jeśli ostatni płaski punkt to (flat_until, base_height), a pierwszy górzysty to (flat_until+1, coś),
        # to wszystko jest ciągłe.
        points.extend(hilly)

    return points

def create_terrain_body(world, points):
    ground_body = world.CreateStaticBody()
    chain = chainShape(vertices=points)
    ground_body.CreateFixture(shape=chain, density=0, friction=0.6, restitution=0.2)
    return ground_body
