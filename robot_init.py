import pygame
import sys
import math

def init_robot():
    pygame.init()
    screen = pygame.display.set_mode((800,600))
    pygame.display.set_caption("Robot Simulation")
    clock = pygame.time.Clock()

    WHITE = (255, 255, 255)
    BLUE = (50, 120, 220)
    DARK = (30, 30, 30)

    triangle_points = [(30,0), (-15, 15), (-15, -15)]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(DARK)

        # Draw the robot triangle
        center_x = 400
        center_y = 300
        new_points = []
        for x,y in triangle_points:
            new_points.append((x + center_x, y + center_y))
        pygame.draw.polygon(screen, BLUE, new_points)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

def main():
    init_robot()

if __name__ == "__main__":
    main()