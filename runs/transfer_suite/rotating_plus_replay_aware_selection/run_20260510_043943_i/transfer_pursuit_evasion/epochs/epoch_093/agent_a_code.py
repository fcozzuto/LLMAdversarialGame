def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if is_evader:
        target_corner = max(corners, key=lambda c: cheb(ox, oy, c[0], c[1]))
    else:
        target_corner = None

    best_move = [0, 0]
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d_to_opp = cheb(nx, ny, ox, oy)
        # Avoid obstacles: prefer cells not adjacent (cheap proxy)
        adj = 0
        if obstacles:
            for ax, ay in obstacles:
                if cheb(nx, ny, ax, ay) == 1:
                    adj += 1
        if is_evader:
            # Maximize distance from pursuer, and also drift to farthest corner from pursuer
            dist_corner = cheb(nx, ny, target_corner[0], target_corner[1])
            val = (d_to_opp * 10) + dist_corner - (adj * 3)
        else:
            # Minimize distance to pursuer, slight bias toward center to avoid corner traps
            center_bias = -(abs((w - 1) / 2 - nx) + abs((h - 1) / 2 - ny))
            val = (-d_to_opp * 10) + center_bias - (adj * 3)

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move