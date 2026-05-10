def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))
    role = observation.get("self_role", "pursuer")
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    tx, ty = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))  # escape corner bias
    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        center = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        escape_bias = dist2(nx, ny, tx, ty) - 0.5 * (abs(nx - tx) + abs(ny - ty))
        align = -0.25 * (abs(nx - ox) + abs(ny - oy))

        if role == "pursuer":
            score = (-d) + align - 0.01 * center
        else:
            score = d + 0.07 * escape_bias - 0.01 * center

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move