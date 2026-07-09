import pygame
import sys
import math

def demo_keyboard_control():
    """
    AD 控制三角形移动，Q/E 旋转。
    这就模拟了一台差速机器人。

    关键概念：
    - pygame.key.get_pressed() 检测按键状态
    - dt（delta time）：每帧的时间差，保证不同帧率下移动速度一致
    """
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Lesson 3: AD 移动, Q/E 旋转, 停车")
    clock = pygame.time.Clock()

    WHITE = (255, 255, 255)
    BLUE = (50, 120, 220)
    DARK = (30, 30, 30)

    triangle_local = [(30, 0), (-15, -15), (-15, 15)]
    line_start_points = [(200, 400), (250, 400), (300, 400), (350, 400)]
    line_end_points = [(200, 500), (250, 500), (300, 500), (350, 500)]

    x, y = 400, 300
    theta = 0.0

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 读键盘
        keys = pygame.key.get_pressed()
        v = 100 if keys[pygame.K_d] else (-100 if keys[pygame.K_a] else 0)
        omega = -2.0 if keys[pygame.K_q] else (2.0 if keys[pygame.K_e] else 0)

        # 更新状态（单轮运动学）
        x += v * math.cos(theta) * dt
        y += v * math.sin(theta) * dt
        theta += omega * dt
        theta = math.atan2(math.sin(theta), math.cos(theta))

        # 绘制
        screen.fill(DARK)
        rotated = []
        for lx, ly in triangle_local:
            rx = lx * math.cos(theta) - ly * math.sin(theta)
            ry = lx * math.sin(theta) + ly * math.cos(theta)
            rotated.append((x + rx, y + ry))
        pygame.draw.polygon(screen, BLUE, rotated)
        for i in range(4):
            pygame.draw.line(screen, WHITE, line_start_points[i], line_end_points[i])
        
        font = pygame.font.Font(None, 24)
        text = font.render(f"({x:.1f}, {y:.1f})  theta={theta:.2f}", True, WHITE)
        screen.blit(text, (10, 10))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    demo_keyboard_control()
