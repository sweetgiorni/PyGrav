import sys
import pygame
import math
import random

pygame.init()
TIMESTEP = 60
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
size = width, height = pygame.display.get_surface().get_size()
centerPos = (width / 2, height / 2)
black = 0, 0, 0


clock = pygame.time.Clock()

class Vector2:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    @classmethod
    def from_list(cls, position):
        return Vector2(position[0], position[1])

    def __iter__(self):
        return iter((self.x, self.y))

    def __str__(self):
        return str(self.x) + ", " + str(self.y)

    def __add__(self, other):
        if type(other) is Vector2:
            return Vector2(self.x + other.x, self.y + other.y)
        raise Exception("Can't add Vector2 and " + type(other))

    def __sub__(self, other):
        if type(other) is Vector2:
            return Vector2(self.x - other.x, self.y - other.y)
        raise Exception("Can't subtract Vector2 and " + type(other))

    def __mul__(self, other):
        if type(other) is int or type(other)is float:
            return Vector2(self.x * other, self.y * other)
        raise Exception("Can't multiply Vector2 and " + type(other))

    # Return the vector as a list
    def list(self): return [self.x, self.y]

    # Calculate the distance between two Vector2s
    @staticmethod
    def distance(a, b):
        return math.sqrt(pow(b.x - a.x, 2) + pow(b.y - a.y, 2))

    @staticmethod
    def magnitude(vec):
        return math.sqrt(vec.x * vec.x + vec.y * vec.y)

    def normalized(self):
        return Vector2.normalize(self)
    @staticmethod
    def normalize(vec):
        mag = Vector2.magnitude(vec)
        return Vector2(vec.x / mag, vec.y / mag)

    # Given vectors points a and b, return a unit vector that points a towards b
    @staticmethod
    def point_towards(a, b):
        v = Vector2(b.x - a.x, b.y - a.y)
        return v.normalized()


class Planet:
    planets = []
    G = .4

    def __init__(self, radius=10, mass=100, position=Vector2(0, 0), velocity=Vector2(0, 0), immovable=False, color=(255, 255, 255)):
        self.radius = radius
        self.mass = mass
        self.immovable = immovable
        if type(position) is tuple:
            self.position = Vector2.from_list(position)
        elif type(position) is Vector2:
            self.position = position
        if type(velocity) is tuple:
            self.velocity = Vector2.from_list(velocity)
        elif type(velocity) is Vector2:
            self.velocity = velocity
        self.surface = pygame.Surface((2*radius, 2*radius))
        self.surface.fill(black)
        pygame.draw.circle(self.surface, color, (radius, radius), radius)
        Planet.planets.append(self)

    @classmethod
    def simulate(cls):
        for p in cls.planets:
            p.update_position()
        for p in cls.planets:
            p.calculate_grav_force()

    def update_position(self):
        if self.immovable:
            return
        self.position.x += self.velocity.x
        self.position.y += self.velocity.y

    def calculate_grav_force(self):
        for other_planet in Planet.planets:
            if other_planet is not self:
                distance = Vector2.distance(self.position, other_planet.position)
                # Check to see if the two planets are touching, and if so, do something about it
                if distance - self.radius - other_planet.radius <= 0:
                    # Destroy the less massive one I guess...
                    smaller_planet = self if self.mass < other_planet.mass else other_planet
                    Planet.planets.remove(smaller_planet)
                    del smaller_planet
                # F = GMm / r^2
                f = (Planet.G * self.mass * other_planet.mass) / pow(distance, 2)
                f /= self.mass
                # Convert force scalar into an appropriate vector
                force_vector = Vector2.point_towards(self.position, other_planet.position) * f
                self.velocity += force_vector


sun = Planet(radius=25, position=Vector2.from_list(centerPos), mass=1000, immovable=True, color=(239, 223, 0))


# Add some random planets
def populate_system():
    for i in range(0, 15):
        radius = random.randint(5,15)
        mass = random.randint(5,15)
        position = Vector2(random.randint(0, width), random.randint(0, height))
        # Add a force tangent to the sun to increase chances of an orbiting body
        tan_line = Vector2.point_towards(position, sun.position)  # This points towards the sun
        tan_line.x, tan_line.y = tan_line.y, tan_line.x
        tan_line.x *= -1
        tan_line.normalized()
        force = random.uniform(.25, 1.5)
        tan_line *= force
        velocity = tan_line
        p = Planet(radius, mass, position, velocity)


populate_system()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                sys.exit()
    screen.fill(black)
    Planet.simulate()
    for planet in Planet.planets:
        screen.blit(planet.surface, planet.position.list())
    pygame.display.flip()
    clock.tick(TIMESTEP)
