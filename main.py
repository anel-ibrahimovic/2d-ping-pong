import pygame
import sys


def draw_table(screen, screen_width, screen_height):
    screen.fill((0, 0, 0))

    table_width = 600
    table_height = 1000

    table_x = (screen_width - table_width) // 2
    table_y = (screen_height - table_height) // 2

    table_color = (0, 0, 195)
    line_color = (255, 255, 255)
    line_width = 5

    pygame.draw.rect(screen, table_color, (table_x, table_y, table_width, table_height))
    pygame.draw.rect(screen, line_color, (table_x, table_y, table_width, table_height), line_width)

    x = table_x + table_width // 2
    pygame.draw.line(screen, line_color, (x, table_y), (x, table_y + table_height), line_width)

    horizontal_y = table_y + table_height // 2
    pygame.draw.line(screen, line_color, (table_x, horizontal_y), (table_x + table_width, horizontal_y), 3)

    return table_x, table_y, table_width, table_height


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

        allowed_outside = 10
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
        if center_x < target_x and self.x + self.width < table_x + table_width:
            self.x += self.speed
        elif center_x > target_x and self.x > table_x:
            self.x -= self.speed
        self.update_rect()


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
        self.speed_x *= -1

    def reset_for_serve(self, x, y):
        self.x = x
        self.y = y
        self.speed_x = 0
        self.speed_y = 0


def ball_collides_with_paddle(ball, paddle):
    ball_rect = pygame.Rect(ball.x - ball.radius, ball.y - ball.radius, ball.radius * 2, ball.radius * 2)
    return ball_rect.colliderect(paddle.rect)


def main():
    pygame.init()

    screen_width = 1200
    screen_height = 1200
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Ping Pong Game with Score")

    font = pygame.font.SysFont(None, 48)

    paddle_width = 60
    paddle_height = 100
    paddle_speed = 3
    margin = 5

    table_x = (screen_width - 600) // 2
    table_y = (screen_height - 1000) // 2
    table_width = 600
    table_height = 1000

    left_x = table_x + (table_width // 4) - (paddle_width // 2)
    left_y = table_y + table_height - paddle_height - margin + 20

    right_x = table_x + (3 * table_width // 4) - (paddle_width // 2)
    right_y = table_y + margin

    bottom_paddle = Paddle(left_x, left_y, paddle_width, paddle_height, paddle_speed, screen_height)
    top_paddle = Paddle(right_x, right_y, paddle_width, paddle_height, paddle_speed, screen_height)

    ball_radius = 10
    ball = Ball(0, 0, ball_radius, speed_x=0, speed_y=0)

    player_score = 0
    ai_score = 0

    paddle_direction = None
    serve_count = 0
    serve_side = 'player'
    serve_active = False

    def reset_ball_for_serve():
        nonlocal serve_active
        if serve_side == 'player':
            ball_start_x = bottom_paddle.x + bottom_paddle.width // 2
            ball_start_y = bottom_paddle.y - ball.radius - 1
        else:
            ball_start_x = top_paddle.x + top_paddle.width // 2
            ball_start_y = top_paddle.y + top_paddle.height + ball.radius + 1
        ball.reset_for_serve(ball_start_x, ball_start_y)
        serve_active = False

    ai_serve_delay = 1000
    ai_serve_timer_started = False
    ai_serve_start_time = 0

    reset_ball_for_serve()

    running = True
    game_over = False

    while running:
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        if keys[pygame.K_r] and game_over:
            player_score = 0
            ai_score = 0
            game_over = False
            serve_side = 'player'
            reset_ball_for_serve()

        if not game_over:
            moving_dirs = []

            if keys[pygame.K_LEFT]:
                bottom_paddle.move('left', table_x, table_y, table_width, table_height)
                moving_dirs.append('left')
            if keys[pygame.K_RIGHT]:
                bottom_paddle.move('right', table_x, table_y, table_width, table_height)
                moving_dirs.append('right')
            if keys[pygame.K_UP]:
                bottom_paddle.move('up', table_x, table_y, table_width, table_height)
                moving_dirs.append('up')
            if keys[pygame.K_DOWN]:
                bottom_paddle.move('down', table_x, table_y, table_width, table_height)
                moving_dirs.append('down')

            paddle_direction = moving_dirs[-1] if moving_dirs else None

            top_paddle.ai_move(ball.x, table_x, table_width)

            if not serve_active:
                if serve_side == 'player' and keys[pygame.K_UP]:
                    ball.speed_y = -3
                    ball.speed_x = 0
                    if keys[pygame.K_LEFT]:
                        ball.speed_x = -1.5
                    elif keys[pygame.K_RIGHT]:
                        ball.speed_x = 1.5
                    serve_active = True
                elif serve_side == 'ai':
                    if not ai_serve_timer_started:
                        ai_serve_start_time = pygame.time.get_ticks()
                        ai_serve_timer_started = True
                    elif pygame.time.get_ticks() - ai_serve_start_time >= ai_serve_delay:
                        ball.speed_x = 0
                        ball.speed_y = 3
                        serve_active = True
                        ai_serve_timer_started = False

            ball.update()

            middle_line_y = table_y + table_height // 2

            out_left = ball.x + ball.radius < table_x
            out_right = ball.x - ball.radius > table_x + table_width
            out_top = ball.y + ball.radius < table_y
            out_bottom = ball.y - ball.radius > table_y + table_height

            dist_left = table_x - (ball.x + ball.radius)
            dist_right = (ball.x - ball.radius) - (table_x + table_width)
            dist_top = table_y - (ball.y + ball.radius)
            dist_bottom = (ball.y - ball.radius) - (table_y + table_height)

            if serve_side == 'player':
                ball_crossed_middle = ball.y + ball.radius < middle_line_y
            else:
                ball_crossed_middle = ball.y - ball.radius > middle_line_y

            if (out_left or out_right or out_top or out_bottom) and not ball_crossed_middle:
                if serve_side == 'player':
                    ai_score += 1
                else:
                    player_score += 1
                serve_count += 1
                if serve_count >= 2:
                    serve_count = 0
                    serve_side = 'player' if serve_side == 'ai' else 'ai'
                reset_ball_for_serve()

            elif ball_crossed_middle:
                went_far_out = (
                    (out_left and dist_left >= 200) or
                    (out_right and dist_right >= 200) or
                    (out_top and dist_top >= 200) or
                    (out_bottom and dist_bottom >= 200)
                )
                if went_far_out:
                    if serve_side == 'player':
                        player_score += 1
                    else:
                        ai_score += 1
                    serve_count += 1
                    if serve_count >= 2:
                        serve_count = 0
                        serve_side = 'player' if serve_side == 'ai' else 'ai'
                    reset_ball_for_serve()

            if ball_collides_with_paddle(ball, bottom_paddle) and ball.speed_y > 0:
                hit_position = (ball.x - (bottom_paddle.x + bottom_paddle.width // 2)) / (bottom_paddle.width / 2)
                ball.speed_x = hit_position * 5
                if paddle_direction == 'left':
                    ball.speed_x -= 1
                elif paddle_direction == 'right':
                    ball.speed_x += 1
                ball.speed_y *= -1

            if ball_collides_with_paddle(ball, top_paddle) and ball.speed_y < 0:
                hit_position = (ball.x - (top_paddle.x + top_paddle.width // 2)) / (top_paddle.width / 2)
                ball.speed_x = hit_position * 5
                ball.speed_y *= -1

            if player_score >= 11 or ai_score >= 11:
                game_over = True

        draw_table(screen, screen_width, screen_height)

        bottom_paddle.draw(screen, angle=45 if bottom_paddle.x < table_x + table_width // 2 else -45)
        top_paddle.draw(screen, angle=-135 if top_paddle.x > table_x + table_width // 2 else 135)

        ball.draw(screen)

        score_text = font.render(f"Player: {player_score}   AI: {ai_score}", True, (255, 255, 255))
        screen.blit(score_text, (screen_width // 2 - score_text.get_width() // 2, 30))

        if game_over:
            over_text = font.render("Game Over! Press R to Restart", True, (255, 0, 0))
            screen.blit(over_text, (screen_width // 2 - over_text.get_width() // 2, screen_height // 2))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
