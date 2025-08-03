import pygame


class Paddle:
    def __init__(self, x, y, width, height, speed, screen_height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.screen_height = screen_height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen, angle=0):
        paddle_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        paddle_color = (200, 30, 30)
        handle_color = (205, 133, 63)

        head_radius = self.width // 2
        head_center = (head_radius, head_radius)
        pygame.draw.circle(paddle_surface, paddle_color, head_center, head_radius)

        handle_width = self.width // 4
        handle_height = self.height - 2 * head_radius
        handle_x = (self.width - handle_width) // 2
        handle_y = 2 * head_radius
        pygame.draw.rect(paddle_surface, handle_color, (handle_x, handle_y, handle_width, handle_height))

        rotated_surface = pygame.transform.rotate(paddle_surface, angle)
        rotated_rect = rotated_surface.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))

        screen.blit(rotated_surface, rotated_rect.topleft)

    def move(self, direction, table_x, table_y, table_width, table_height):
        vertical_move_range = 30

        if self.y > table_y + table_height // 2:
            boundary_top = table_y + table_height - self.height - vertical_move_range
            extra_down = 50
            boundary_bottom = table_y + table_height - self.height + extra_down
        else:
            boundary_top = table_y
            boundary_bottom = table_y + vertical_move_range

        allowed_outside = 30
        boundary_left = table_x - allowed_outside
        boundary_right = table_x + table_width + allowed_outside

        if direction == 'left' and self.x > boundary_left:
            self.x -= self.speed
        elif direction == 'right' and self.x + self.width < boundary_right:
            self.x += self.speed
        elif direction == 'up' and self.y > boundary_top:
            self.y -= self.speed
        elif direction == 'down' and self.y < boundary_bottom:
            self.y += self.speed

        self.update_rect()

    def update_rect(self):
        self.rect.topleft = (self.x, self.y)

    def ai_move(self, target_x, table_x, table_width):
        center_x = self.x + self.width // 2
        deadzone = 3

        if center_x < target_x - deadzone and self.x + self.width < table_x + table_width:
            self.x += self.speed
        elif center_x > target_x + deadzone and self.x > table_x:
            self.x -= self.speed

        self.update_rect()
