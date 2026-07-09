import pygame
import sys
import math

def demo_collision():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Lesson 3: 障碍物 + 碰撞检测")
    clock = pygame.time.Clock()
    BLUE = (50, 120, 220)
    RED = (220, 60, 60)
    DARK = (30, 30, 30)
    GRAY = (100, 100, 100)
    YELLOW = (255, 220, 50)

    triangle_local = [(30, 0), (-15, -15), (-15, 15)]
    robot_radius = max(math.hypot(x, y) for x, y in triangle_local)
    obstacles = [(500, 300, 40), (200, 200, 30), (600, 450, 50), (300, 500, 35)]
    x, y, theta = 100, 100, 0.0

    def check_collision(px, py):
        for ox, oy, r in obstacles:
            dx = px - ox
            dy = py - oy
            if dx * dx + dy * dy < (r + robot_radius) ** 2:
                return True
        return False

    def which_collision(px, py):
        """返回 (ox, oy, r) 如果 (px,py) 与某障碍物碰撞，否则 None"""
        for ox, oy, r in obstacles:
            dx = px - ox
            dy = py - oy
            if dx * dx + dy * dy < (r + robot_radius) ** 2:
                return (ox, oy, r)
        return None

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        v = 200 if keys[pygame.K_w] else (-100 if keys[pygame.K_s] else 0)
        omega = -2.0 if keys[pygame.K_q] else (2.0 if keys[pygame.K_e] else 0)

        # 预判下一帧位置
        nx = x + v * math.cos(theta) * dt
        ny = y + v * math.sin(theta) * dt
        blocked_obstacle = which_collision(nx, ny) if (v != 0 or omega != 0) else None

        if blocked_obstacle is None:
            x, y = nx, ny
        theta += omega * dt

        screen.fill(DARK)

        # 画障碍物：被挡的变红，其余的灰色
        for ox, oy, r in obstacles:
            if (ox, oy, r) == blocked_obstacle:
                color = RED
            else:
                color = GRAY
            pygame.draw.circle(screen, color, (int(ox), int(oy)), r)

        # 画机器人：被挡住时变红
        robot_color = RED if blocked_obstacle else BLUE
        rotated = []
        for lx, ly in triangle_local:
            rx = lx * math.cos(theta) - ly * math.sin(theta)
            ry = lx * math.sin(theta) + ly * math.cos(theta)
            rotated.append((x + rx, y + ry))
        pygame.draw.polygon(screen, robot_color, rotated)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    demo_collision()
