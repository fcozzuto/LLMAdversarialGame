def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    self_role = observation.get("self_role", "pursuer")
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x, y):
        dx = x - ox
        dy = y - oy
        return dx * dx + dy * dy

    def corner_bias(x, y):
        # Prefer nearest corner for evader; for pursuer, avoid giving corner advantage by opposite.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = None
        for cx, cy in corners:
            d = (x - cx) * (x - cx) + (y - cy) * (y - cy)
            if best is None or d < best:
                best = d
        return best if best is not None else 0

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            d = dist2(nx, ny)
            cb = corner_bias(nx, ny)
            # Deterministic tie-break with move ordering as listed.
            candidates.append((dx, dy, d, cb))

    if not candidates:
        return [0, 0]

    if self_role == "evader":
        # Maximize distance; also prefer moving toward a corner.
        best = None
        for dx, dy, d, cb in candidates:
            score = (d, -cb, -(abs(dx) + abs(dy)))
            if best is None or score > best[0]:
                best = (score, dx, dy)
        return [int(best[1]), int(best[2])]

    # pursuer: minimize distance; small preference to keep initiative toward opponent and away from corners.
    best = None
    for dx, dy, d, cb in candidates:
        vx = ox - sx
        vy = oy - sy
        align = 0
        if vx != 0:
            align += 1 if (dx * vx) > 0 else (-1 if (dx * vx) < 0 else 0)
        if vy != 0:
            align += 1 if (dy * vy) > 0 else (-1 if (dy * vy) < 0 else 0)
        score = (-d, cb, -align, -(abs(dx) + abs(dy)))
        if best is None or score > best[0]:
            best = (score, dx, dy)
    return [int(best[1]), int(best[2])]