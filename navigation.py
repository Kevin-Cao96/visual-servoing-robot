import pygame
import sys
import math
import random

def demo_go_to_point():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Lesson 4: 点击 -> 机器人自动走过去")
    clock = pygame.time.Clock()
    
    k_linear = 1.0
    k_angular = 10.0
    WHITE = (255, 255, 255)
    BLUE = (50, 120, 220)
    GREEN = (60, 200, 60)
    DARK = (30, 30, 30)
    ORANGE = (255, 180, 50)
    CAM_BG = (50, 50, 60)     # 深蓝灰色，和主画面区分
    integral = 0
    triangle_local = [(30, 0), (-15, -15), (-15, 15)]
    cam_fx = 120               # 焦距参数，控制视角宽度
    cam_cx = 100               # 相机画面中心 x
    cam_cy = 75                # 相机画面中心 y
    cam_w, cam_h = 200, 150    # 相机画面尺寸
    objects = [(200, 100, 30), (600, 400, 40)]
    x, y, theta = 400, 300, 0.0
    target = None
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                target = event.pos
                integral = 0
        v, omega = 0, 0
        if target is not None:
            tx, ty = target
            dx = tx - x
            dy = ty - y
            distance = math.hypot(dx, dy)
            target_angle = math.atan2(dy, dx)
            angle_diff = target_angle - theta
            angle_diff = math.atan2(math.sin(angle_diff), math.cos(angle_diff))
            #print(integral)
            if distance > 25:
                if distance > 200: v_desired = 200
                else :v_desired = k_linear * distance
                friction = 20
                v = max(0, v_desired - friction)
            else:   
                integral += distance * dt
                v = integral
            if distance < 5: v=0;
            omega = k_angular * angle_diff
            x += v * math.cos(theta) * dt
            y += v * math.sin(theta) * dt
            theta += omega * dt
            
        screen.fill(DARK)
        camera_surf = pygame.Surface((cam_w, cam_h))
        camera_surf.fill(CAM_BG)    
        # 投影 landmark (200, 400) 到相机画面
        for lx,ly,_ in objects:
            dx = lx - x
            dy = ly - y
            target_angle = math.atan2(ly, lx)   
            angle_diff = target_angle - theta
            angle_diff = math.atan2(math.sin(angle_diff), math.cos(angle_diff))  # 归一化

            # 如果在正面，画出来
            if abs(angle_diff) < math.pi / 2:   # ±90° 以内
                u = cam_cx + cam_fx * math.tan(angle_diff)
                pygame.draw.circle(camera_surf, ORANGE, (int(u), cam_cy), 6)
            screen.blit(camera_surf, (800 - cam_w - 10, 10))
        if target:
            pygame.draw.circle(screen, GREEN, (int(target[0]), int(target[1])), 8, 2)
            pygame.draw.line(screen, GREEN, (int(x), int(y)), target, 1)
        rotated = []
        for lx, ly in triangle_local:
            rx = lx * math.cos(theta) - ly * math.sin(theta)
            ry = lx * math.sin(theta) + ly * math.cos(theta)
            rotated.append((x + rx, y + ry))
        pygame.draw.polygon(screen, BLUE, rotated)
        for ox,oy,r in objects:
            pygame.draw.circle(screen, ORANGE, (ox,oy), r)
        font = pygame.font.Font(None, 24)
        info = f"(v={v:.1f}, omega={omega:.2f}, distance={distance:.2f})" if target else "Click anywhere"
        text = font.render(info, True, WHITE)
        screen.blit(text, (10, 10))
        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    demo_go_to_point()