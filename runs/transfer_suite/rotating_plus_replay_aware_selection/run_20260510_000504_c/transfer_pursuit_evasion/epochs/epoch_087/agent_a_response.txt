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

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def obstacle_pen(x, y):
        if (x, y) in obstacles:
            return 10**9
        pen = 0
        for ex, ey in obstacles:
            d = abs(x - ex) + abs(y - ey)
            if d == 0:
                return 10**9
            if d <= 2:
                pen += (3 - d) * 120
        return pen

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        op = obstacle_pen(nx, ny)
        if op >= 10**9:
            continue
        d2 = dist2(nx, ny, ox, oy)
        center_bias = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) * 0.01
        if is_evader:
            # maximize distance from pursuer; avoid obstacles
            val = d2 - op + center_bias
        else:
            # minimize distance to pursuer; avoid obstacles
            val = -d2 - op + center_bias
        if best is None or val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best