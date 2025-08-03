import pygame

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
