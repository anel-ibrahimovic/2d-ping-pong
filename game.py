import pygame
import sys
from table import draw_table
from paddle import Paddle
from ball import Ball
from utils import ball_collides_with_paddle


class Game:
    def __init__(self):
        pygame.init()

        self.screen_width = 1200
        self.screen_height = 1200
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("2D Ping Pong Game")

        self.font = pygame.font.SysFont(None, 48)

        # Table setup
        self.table_x = (self.screen_width - 600) // 2
        self.table_y = (self.screen_height - 1000) // 2
        self.table_width = 600
        self.table_height = 1000

        # Paddles
        paddle_width = 60
        paddle_height = 100
        paddle_speed = 7
        margin = 5

        left_x = self.table_x + (self.table_width // 4) - (paddle_width // 2)
        left_y = self.table_y + self.table_height - paddle_height - margin + 20

        right_x = self.table_x + (3 * self.table_width // 4) - (paddle_width // 2)
        right_y = self.table_y + margin

        self.bottom_paddle = Paddle(left_x, left_y, paddle_width, paddle_height, paddle_speed, self.screen_height)
        self.top_paddle = Paddle(right_x, right_y, paddle_width, paddle_height, paddle_speed, self.screen_height)

        # Ball
        self.ball_radius = 10
        self.ball = Ball(0, 0, self.ball_radius, speed_x=0, speed_y=0)

        self.player_score = 0
        self.ai_score = 0
        self.paddle_direction = None

        # Serving
        self.serve_count = 0
        self.serve_side = 'player'
        self.serve_active = False
        self.ai_serve_delay = 1000
        self.ai_serve_timer_started = False
        self.ai_serve_start_time = 0

        # Track who last hit the ball ('player' or 'ai')
        self.last_hit_by = None

        self.reset_ball_for_serve()
        self.game_over = False

    def reset_ball_for_serve(self):
        if self.serve_side == 'player':
            x = self.bottom_paddle.x + self.bottom_paddle.width // 2
            y = self.table_y + self.table_height - self.ball.radius - 20
        else:
            x = self.top_paddle.x + self.top_paddle.width // 2
            y = self.table_y + self.ball.radius + 20
        self.ball.reset_for_serve(x, y)
        self.serve_active = False
        self.last_hit_by = self.serve_side

    def handle_input(self):
        keys = pygame.key.get_pressed()
        moving_dirs = []

        if keys[pygame.K_LEFT]:
            self.bottom_paddle.move('left', self.table_x, self.table_y, self.table_width, self.table_height)
            moving_dirs.append('left')
        if keys[pygame.K_RIGHT]:
            self.bottom_paddle.move('right', self.table_x, self.table_y, self.table_width, self.table_height)
            moving_dirs.append('right')
        if keys[pygame.K_UP]:
            self.bottom_paddle.move('up', self.table_x, self.table_y, self.table_width, self.table_height)
            moving_dirs.append('up')
        if keys[pygame.K_DOWN]:
            self.bottom_paddle.move('down', self.table_x, self.table_y, self.table_width, self.table_height)
            moving_dirs.append('down')

        self.paddle_direction = moving_dirs[-1] if moving_dirs else None

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            self.screen.fill((0, 0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()
            if keys[pygame.K_r] and self.game_over:
                self.__init__()

            if not self.game_over:
                self.handle_input()
                self.top_paddle.ai_move(self.ball.x, self.table_x, self.table_width)

                # Serve logic
                if not self.serve_active:
                    if self.serve_side == 'player' and keys[pygame.K_UP]:
                        self.ball.speed_y = -9
                        self.ball.speed_x = 0
                        if keys[pygame.K_LEFT]:
                            self.ball.speed_x = -7.5
                        elif keys[pygame.K_RIGHT]:
                            self.ball.speed_x = 7.5
                        self.serve_active = True
                    elif self.serve_side == 'ai':
                        if not self.ai_serve_timer_started:
                            self.ai_serve_start_time = pygame.time.get_ticks()
                            self.ai_serve_timer_started = True
                        elif pygame.time.get_ticks() - self.ai_serve_start_time >= self.ai_serve_delay:
                            self.ball.speed_x = 0
                            self.ball.speed_y = 9
                            self.serve_active = True
                            self.ai_serve_timer_started = False

                self.ball.update()
                self.check_collision_and_score()

            draw_table(self.screen, self.screen_width, self.screen_height)
            self.bottom_paddle.draw(self.screen, angle=45 if self.bottom_paddle.x < self.table_x + self.table_width // 2 else -45)
            self.top_paddle.draw(self.screen, angle=-135 if self.top_paddle.x > self.table_x + self.table_width // 2 else 135)
            self.ball.draw(self.screen)

            score_text = self.font.render(f"Player: {self.player_score}   AI: {self.ai_score}", True, (255, 255, 255))
            self.screen.blit(score_text, (self.screen_width // 2 - score_text.get_width() // 2, 30))

            if self.game_over:
                over_text = self.font.render("Game Over! Press R to Restart", True, (255, 0, 0))
                self.screen.blit(over_text, (self.screen_width // 2 - over_text.get_width() // 2, self.screen_height // 2))

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        sys.exit()

    def check_collision_and_score(self):
        table_x, table_y, table_width, table_height = self.table_x, self.table_y, self.table_width, self.table_height

        ball = self.ball
        middle_line_y = table_y + table_height // 2

        out_left = ball.x + ball.radius < table_x
        out_right = ball.x - ball.radius > table_x + table_width
        out_top = ball.y + ball.radius < table_y
        out_bottom = ball.y - ball.radius > table_y + table_height

        dist_left = table_x - (ball.x + ball.radius)
        dist_right = (ball.x - ball.radius) - (table_x + table_width)
        dist_top = table_y - (ball.y + ball.radius)
        dist_bottom = (ball.y - ball.radius) - (table_y + table_height)

        # Determine which half the ball is currently in
        ball_in_top_half = ball.y < middle_line_y
        ball_in_bottom_half = ball.y >= middle_line_y

        # Check if ball crossed the net (middle line) relative to last hitter
        ball_crossed_net = (self.last_hit_by == 'player' and ball_in_top_half) or \
                           (self.last_hit_by == 'ai' and ball_in_bottom_half)

        if not ball_crossed_net:
            # Ball hasn't crossed net but is out of bounds -> point to opponent of last hitter
            if out_left or out_right or out_top or out_bottom:
                self.award_point('ai' if self.last_hit_by == 'player' else 'player')
        else:
            # Ball crossed net; if it went far out (>200 pixels), point to last hitter
            went_far_out = (
                (out_left and dist_left >= 200) or
                (out_right and dist_right >= 200) or
                (out_top and dist_top >= 200) or
                (out_bottom and dist_bottom >= 200)
            )
            if went_far_out:
                self.award_point(self.last_hit_by)

        # Collision with bottom paddle (player)
        if ball_collides_with_paddle(ball, self.bottom_paddle) and ball.speed_y > 0:
            offset = (ball.x - (self.bottom_paddle.x + self.bottom_paddle.width // 2)) / (self.bottom_paddle.width / 2)
            ball.speed_x = offset * 5
            if self.paddle_direction == 'left':
                ball.speed_x -= 1
            elif self.paddle_direction == 'right':
                ball.speed_x += 1
            ball.speed_y *= -1

            self.last_hit_by = 'player'

        # Collision with top paddle (AI)
        if ball_collides_with_paddle(ball, self.top_paddle) and ball.speed_y < 0:
            offset = (ball.x - (self.top_paddle.x + self.top_paddle.width // 2)) / (self.top_paddle.width / 2)
            ball.speed_x = offset * 5
            ball.speed_y *= -1

            self.last_hit_by = 'ai'

        # Check game over condition
        if self.player_score >= 11 or self.ai_score >= 11:
            self.game_over = True

    def award_point(self, scorer):
        if scorer == 'player':
            self.player_score += 1
        else:
            self.ai_score += 1
        self.serve_count += 1
        if self.serve_count >= 2:
            self.serve_count = 0
            self.serve_side = 'player' if self.serve_side == 'ai' else 'ai'
        self.reset_ball_for_serve()
