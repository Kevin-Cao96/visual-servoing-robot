"""
Coordinate Transform Explorer — understand world-to-robot coordinate conversion

Just two views, no navigation, no PID.

Controls: Q/E to rotate the robot, observe how landmark coordinates change.
"""

import pygame
import sys
import math


def main():
    pygame.init()
    screen = pygame.display.set_mode((1000, 600))
    pygame.display.set_caption(
        "Coordinate Transform Explorer — Q/E to rotate, watch landmark coordinates change"
    )
    clock = pygame.time.Clock()

    WHITE = (255, 255, 255)
    BLUE = (50, 120, 220)
    DARK = (30, 30, 30)
    ORANGE = (255, 180, 50)
    PINK = (240, 80, 160)
    CYAN = (50, 200, 200)
    CAM_BG = (45, 45, 55)

    # Robot (fixed at screen center, does not move)
    cx, cy = 300, 300
    theta = 0.0

    # Two landmarks in world coordinates (fixed)
    landmarks = [
        ((450, 200), PINK, "A"),
        ((180, 420), ORANGE, "B"),
    ]

    # Camera parameters
    cam_w, cam_h = 300, 200
    cam_cx, cam_cy = cam_w // 2, cam_h // 2
    cam_fx = 120

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        omega = -2.0 if keys[pygame.K_q] else (2.0 if keys[pygame.K_e] else 0)
        theta += omega * dt
        theta = math.atan2(math.sin(theta), math.cos(theta))

        # ===== Render =====
        screen.fill(DARK)

        # ---- Left: Top-down View ----
        # Robot (triangle, fixed at center)
        tri = [(30, 0), (-15, -15), (-15, 15)]
        rotated = []
        for lx, ly in tri:
            rx = lx * math.cos(theta) - ly * math.sin(theta)
            ry = lx * math.sin(theta) + ly * math.cos(theta)
            rotated.append((cx + rx, cy + ry))
        pygame.draw.polygon(screen, BLUE, rotated)

        # Robot heading indicator
        fx = cx + 50 * math.cos(theta)
        fy = cy + 50 * math.sin(theta)
        pygame.draw.line(screen, BLUE, (cx, cy), (fx, fy), 2)

        # Draw landmarks and connecting lines
        for (lx, ly), color, name in landmarks:
            pygame.draw.circle(screen, color, (lx, ly), 10)
            font = pygame.font.Font(None, 18)
            screen.blit(font.render(name, True, WHITE), (lx - 4, ly - 24))
            pygame.draw.line(screen, color, (cx, cy), (lx, ly), 1)

        # Forward direction label
        font = pygame.font.Font(None, 18)
        label_fwd = font.render("forward", True, (100, 200, 100))
        screen.blit(
            label_fwd,
            (cx + 55 * math.cos(theta) - 20, cy + 55 * math.sin(theta) - 20),
        )

        # ---- Top-right: Camera View ----
        cam_surf = pygame.Surface((cam_w, cam_h))
        cam_surf.fill(CAM_BG)

        data_lines = []

        for (lx, ly), color, name in landmarks:
            dx = lx - cx
            dy = ly - cy
            distance = math.hypot(dx, dy)

            # Method 1: using angle difference (intuitive)
            target_angle = math.atan2(dy, dx)
            angle_diff = target_angle - theta
            angle_diff = math.atan2(math.sin(angle_diff), math.cos(angle_diff))
            forward1 = distance * math.cos(angle_diff)
            right1 = distance * math.sin(angle_diff)

            # Method 2: using rotation matrix
            forward2 = dx * math.cos(theta) + dy * math.sin(theta)
            right2 = -dx * math.sin(theta) + dy * math.cos(theta)

            data_lines.append(
                (name, distance, angle_diff, forward1, right1, forward2, right2)
            )

            # Draw to camera view
            if forward1 > 0:
                u = cam_cx + cam_fx * right1 / forward1
                v = cam_cy - cam_fx / forward1
                if 0 <= u < cam_w and 0 <= v < cam_h:
                    pygame.draw.circle(cam_surf, color, (int(u), int(v)), 8)
                    f = pygame.font.Font(None, 16)
                    cam_surf.blit(f.render(name, True, WHITE), (int(u) - 4, int(v) - 20))

        # Crosshair
        pygame.draw.line(cam_surf, (80, 80, 90), (cam_cx, 0), (cam_cx, cam_h), 1)
        pygame.draw.line(cam_surf, (80, 80, 90), (0, cam_cy), (cam_w, cam_cy), 1)
        pygame.draw.rect(cam_surf, (100, 100, 120), cam_surf.get_rect(), 2)

        screen.blit(cam_surf, (700, 10))

        # ---- Bottom panel: real-time data ----
        font = pygame.font.Font(None, 22)
        small = pygame.font.Font(None, 18)

        y_pos = 420
        screen.blit(font.render("Q: Rotate Left   E: Rotate Right", True, WHITE), (20, y_pos))
        y_pos += 30

        for name, dist, ang_diff, f1, r1, f2, r2 in data_lines:
            screen.blit(font.render(f"--- Landmark {name} ---", True, WHITE), (20, y_pos))
            y_pos += 24
            screen.blit(small.render(f"Distance: {dist:.0f} px", True, WHITE), (20, y_pos))
            y_pos += 20
            screen.blit(
                small.render(
                    f"Angle Diff: {math.degrees(ang_diff):.0f} deg",
                    True,
                    (200, 200, 100),
                ),
                (20, y_pos),
            )
            y_pos += 20
            screen.blit(
                small.render(
                    f"    = Distance x cos(Angle Diff) = {f1:.1f}  (forward/back)",
                    True,
                    (100, 200, 100),
                ),
                (20, y_pos),
            )
            y_pos += 20
            screen.blit(
                small.render(
                    f"    = Distance x sin(Angle Diff) = {r1:.1f}  (left/right)",
                    True,
                    (200, 120, 120),
                ),
                (20, y_pos),
            )
            y_pos += 20
            screen.blit(
                small.render(
                    f"Verify(rotation matrix): forward={f2:.1f}  right={r2:.1f}",
                    True,
                    (150, 150, 150),
                ),
                (20, y_pos),
            )
            y_pos += 30

        screen.blit(font.render(f"theta = {math.degrees(theta):.0f} deg", True, CYAN), (20, y_pos))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
