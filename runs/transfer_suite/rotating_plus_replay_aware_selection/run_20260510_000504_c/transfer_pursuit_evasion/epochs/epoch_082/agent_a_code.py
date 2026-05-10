def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) or ("escape" in role) or ("runner" in role) or ("flee" in role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def obst_pen(x, y):
        p = 0
        for ex, ey in obstacles:
            d = abs(x - ex) + abs(y - ey)
            if d == 0:
                return 10**9
            if d <= 2:
                p += (3 - d) * 35
        return p

    # For evader: maximize distance and favor corners; for pursuer: minimize distance and keep away from obstacles.
    best = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        dfo = dist2(nx, ny, ox, oy)
        # Corner bias: choose the corner farthest from opponent (evader) or closest to opponent (pursuer).
        if is_evader:
            corner_target = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
            corner_val = abs(corner_target[0] - nx) + abs(corner_target[1] - ny)
            val = dfo * 2 + corner_val * 4 - obst_pen(nx, ny)
        else:
            # Chase opponent directly, but prefer moves that don't step near obstacles.
            corner_target = min(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
            corner_val = abs(corner_target[0] - nx) + abs(corner_target[1] - ny)
            val = (-dfo) * 2 - obst_pen(nx, ny) - corner_val

        if best_val is None or val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best