import pygame


class Ball:
    def __init__(self, x, y, radius, speed_x, speed_y, color=(255, 255, 255)):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.color = color

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y

    def reset(self, x, y):
        self.x = x
        self.y = y
        self.speed_x *= -1  # Reverse direction

    def reset_for_serve(self, x, y):
        self.x = x
        self.y = y
        self.speed_x = 0
        self.speed_y = 0
