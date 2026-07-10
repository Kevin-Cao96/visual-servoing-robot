"""
 相机 + 视觉伺服 demo
 
 运行： python outputs/visual_servo_bot/work/camera_demo.py
 
 世界俯视图（左边）：机器人（三角形） + 两个彩色 landmark
 相机视图（右上角）：机器人"眼中"看到的 landmark
 
 操作：
   鼠标点击 landmark → 机器人用视觉伺服走过去
   WASD / QE → 手动控制
 """
 
import pygame
import sys
import math
 
 # 颜色
WHITE = (255, 255, 255)
BLUE = (50, 120, 220)
DARK = (30, 30, 30)
ORANGE = (255, 180, 50)
PINK = (240, 80, 160)
CAM_BG = (45, 45, 55)

k_linear = 1.0
k_angular = 10.0

pygame.init()
screen = pygame.display.set_mode((1000, 600))

def world_to_camera(lx, ly, robot_x, robot_y, robot_landmark_theta):
    """把 landmark 的世界坐标转成机器人视角的 (forward, right)。"""
    dx = lx - robot_x
    dy = ly - robot_y
    distance = math.hypot(dx, dy)
    pygame.draw.line(screen, WHITE, (lx,ly), (robot_x, robot_y))
    forward = distance * math.cos(robot_landmark_theta)
    right = distance * math.sin(robot_landmark_theta)
    return forward, right, distance
 
 
def camera_to_screen(forward, right, cam_fx, cam_cx, cam_cy, distance):
    """把机器人视角坐标投影到相机画面像素坐标，视野外返回 None。"""
    if forward <= 0:
        return None  # 在背后，看不见
    u = cam_cx + cam_fx * right / forward
    v = cam_cy - cam_fx / forward  # 越近越靠下，越远越靠上
    if distance > 300: r = 500/distance
    else :r = min(30, 1500/distance)# 在 return 之前
    if abs(right / forward) > math.tan(math.pi/4):  # fov = pi/2
        return None
    return int(u), int(v), int(r)
 
 
def main():
    pygame.display.set_caption("视觉伺服: 点击 landmark 让它自动走过去")
    clock = pygame.time.Clock()
 
    # 机器人
    triangle_local = [(30, 0), (-15, -15), (-15, 15)]
    x, y, theta = 400, 300, 0.0
 
    # 相机参数
    cam_w, cam_h = 240, 180
    cam_cx, cam_cy = cam_w // 2, cam_h // 2  # 画面中心
    cam_fx = 100  # 焦距（越大视野越窄）
 
    # Landmarks：世界坐标 (x, y), 颜色, 名字
    landmarks = [
         {"pos": (650, 200), "color": PINK, "name": "A"},
         {"pos": (180, 480), "color": ORANGE, "name": "B"},
    ]
 
    target_idx = None
    target = None
    integral = 0
    auto_mode = True
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                auto_mode = not auto_mode
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for i, lm in enumerate(landmarks):
                    lx, ly = lm['pos']
                    if math.hypot(mx - lx, my - ly) < 15:
                        target_idx = i
                        target = lm
                        break
        if auto_mode == False:            
            if target is not None:
                tx, ty = target['pos']
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
                if distance < 5: 
                    v=0;
                    pygame.draw.circle(screen, target['color'], (tx,ty), 12)
                    target_idx = None

                omega = k_angular * angle_diff
                x += v * math.cos(theta) * dt
                y += v * math.sin(theta) * dt
                theta += omega * dt     
        else:
            # ---- 键盘控制 ----
            keys = pygame.key.get_pressed()
            v = 100 if keys[pygame.K_w] else (-100 if keys[pygame.K_s] else 0)
            omega = -2.0 if keys[pygame.K_q] else (2.0 if keys[pygame.K_e] else 0)
    
            # ---- 运动学更新 ----
            x += v * math.cos(theta) * dt
            y += v * math.sin(theta) * dt
            theta += omega * dt
            theta = math.atan2(math.sin(theta), math.cos(theta))
 
        # ====================== 绘制 ======================
 
        # ---- 主画面（俯视图）----
        screen.fill(DARK)
 
        # 画 landmark
        for i, lm in enumerate(landmarks):
            lx, ly = lm["pos"]
            color = (255, 255, 255) if i == target_idx else lm["color"]
            pygame.draw.circle(screen, color, (int(lx), int(ly)), 12)
            font = pygame.font.Font(None, 18)
            label = font.render(lm["name"], True, WHITE)
            screen.blit(label, (lx - 4, ly - 24))
 
        # 画机器人
        rotated = []
        for lx, ly in triangle_local:
            rx = lx * math.cos(theta) - ly * math.sin(theta)
            ry = lx * math.sin(theta) + ly * math.cos(theta)
            rotated.append((x + rx, y + ry))
        pygame.draw.polygon(screen, BLUE, rotated)

        #FOV cone
        fov = math.pi / 2  # 90° 视野
        arc_pts = []
        for a in [i * 0.01 for i in range(int(-fov/2 / 0.01), int(fov/2 / 0.01) + 1)]:
            angle = theta + a
            arc_pts.append((x + 200 * math.cos(angle), y + 200 * math.sin(angle)))
        pygame.draw.polygon(screen, (50, 50, 60), [(x, y)] + arc_pts, 1)
 
        # ---- 相机画面（右上角）----
        camera_surf = pygame.Surface((cam_w, cam_h))
        camera_surf.fill(CAM_BG)
 
        # 投影每个 landmark
        for lm in landmarks:
            lx, ly = lm["pos"]
            landmark_theta = math.atan2(ly-y, lx-x)
            robot_landmark_theta = landmark_theta - theta
            robot_landmark_theta = math.atan2(math.sin(robot_landmark_theta), math.cos(robot_landmark_theta))
            fwd, rgt, dist = world_to_camera(lx, ly, x, y, robot_landmark_theta)
            uvr = camera_to_screen(fwd, rgt, cam_fx, cam_cx, cam_cy, dist)
            if uvr is not None:
                u, v, r = uvr
                if 0 <= u < cam_w and 0 <= v < cam_h:
                    pygame.draw.circle(camera_surf, lm["color"], (u, v), r)
                    # 标名字
                    font = pygame.font.Font(None, 16)
                    name = font.render(lm["name"], True, WHITE)
                    camera_surf.blit(name, (u - 4, v - 18))
 
        # 十字线（画面中心）
        pygame.draw.line(camera_surf, (80, 80, 90), (cam_cx, 0), (cam_cx, cam_h), 1)
        pygame.draw.line(camera_surf, (80, 80, 90), (0, cam_cy), (cam_w, cam_cy), 1)
 
        # 边框
        pygame.draw.rect(camera_surf, (100, 100, 120), camera_surf.get_rect(), 2)
 
        screen.blit(camera_surf, (760, 10))
 
        # ---- HUD ----
        font = pygame.font.Font(None, 22)
        lines = [
            "W/S: Forward/Backward  Q/E: Turn",
            f"theta={theta:.2f}",
            f"Target: {landmarks[target_idx]['name'] if target_idx is not None else 'None'}",
        ]
        for i, text in enumerate(lines):
            surf = font.render(text, True, WHITE)
            screen.blit(surf, (10, 520 + i * 20))
 
        pygame.display.flip()
 
    pygame.quit()
    sys.exit()
 
 
if __name__ == "__main__":
    main()