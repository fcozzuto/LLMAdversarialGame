def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = observation.get("self_role") or "pursuer"
    if role not in ("pursuer", "evader"):
        role = "pursuer"

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def manh(x, y, a, b):
        return abs(x - a) + abs(y - b)

    curd = manh(sx, sy, ox, oy)
    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        nd = manh(nx, ny, ox, oy)
        # Primary: reduce distance if pursuer, increase if evader
        primary = (curd - nd) if role == "pursuer" else (nd - curd)

        # Secondary: avoid edges for evader (staying mobile), avoid corners for pursuer only lightly
        edge_pen = ((nx == 0) + (nx == w - 1) + (ny == 0) + (ny == h - 1))
        edge_pen = edge_pen if role == "evader" else 0.5 * edge_pen

        # Tertiary: local obstacle proximity (discourage moving next to obstacles)
        near = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if (tx, ty) in obs:
                    near += 1

        # Slight preference: move that increases available valid neighbors
        free = 0
        for adx, ady in moves:
            tx, ty = nx + adx, ny + ady
            if valid(tx, ty):
                free += 1

        score = primary * 10.0 + free * (0.8 if role == "pursuer" else 1.0) - edge_pen * 1.2 - near * 0.6

        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]