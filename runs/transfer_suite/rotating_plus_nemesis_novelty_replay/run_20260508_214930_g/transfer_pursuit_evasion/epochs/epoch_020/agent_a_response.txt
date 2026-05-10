def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for b in obstacles:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            obs.add((int(b[0]), int(b[1])))

    role = (observation.get("self_role", "") or "").lower()
    pursuer = ("purs" in role) or ("chase" in role) or ("hunter" in role)

    capr = int(observation.get("capture_radius", 0))
    capr2 = capr * capr

    actions = [(-1, -1), (-1, 0), (-1, 1),
               (0, -1), (0, 0), (0, 1),
               (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obs
    def d2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    candidates = []
    for dx, dy in actions:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: d2(c[0], c[1], ox, oy))
    # small deterministic tie-break: prefer moves in fixed action order
    best = None
    for dx, dy, nx, ny in candidates:
        if pursuer:
            val = -d2(nx, ny, ox, oy)
            if d2(nx, ny, ox, oy) <= capr2:
                val += 1e9
            # encourage advancing towards opponent while keeping away from obstacles not directly available (light center bias)
            val += -abs((nx - (w - 1) / 2.0)) * 0.01 - abs((ny - (h - 1) / 2.0)) * 0.01
            # slight preference to reduce max(|dx|,|dy|) i.e. diagonals when helpful
            val += (1 if (dx != 0 and dy != 0) else 0) * 0.001
        else:
            val = d2(nx, ny, ox, oy)  # maximize distance
            if d2(nx, ny, ox, oy) <= capr2:
                val -= 1e9
            val += d2(nx, ny, far_corner[0], far_corner[1]) * 0.02  # drift to safest corner
            # discourage staying still unless it's already best
            val += (-0.002 if (dx == 0 and dy == 0) else 0.0)
            val += (1 if (dx != 0 or dy != 0) else 0) * 0.0005
        if best is None or val > best[0]:
            best = (val, dx, dy)

    return [int(best[1]), int(best[2])]