import pygame

def ball_collides_with_paddle(ball, paddle):
    ball_rect = pygame.Rect(ball.x - ball.radius, ball.y - ball.radius, ball.radius * 2, ball.radius * 2)
    return ball_rect.colliderect(paddle.rect)
