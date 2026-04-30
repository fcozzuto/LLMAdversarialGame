def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def obs_pen(x, y):
        p = 0
        for (ox2, oy2) in obstacles:
            dx = ox2 - x
            if dx < 0:
                dx = -dx
            dy = oy2 - y
            if dy < 0:
                dy = -dy
            if dx <= 1 and dy <= 1:
                if (ox2, oy2) == (x, y):
                    return 10**6
                p += 2 if dx == 0 and dy == 0 else 1
        return p

    # Pick target deterministically: min (distance + local penalties), tie-break by coordinates
    best = None
    for (rx, ry) in resources:
        score = cheb(sx, sy, rx, ry) * 3 + obs_pen(rx, ry)
        if best is None or score < best[0] or (score == best[0] and (rx, ry) < best[1]):
            best = (score, (rx, ry))
    tx, ty = best[1]

    # Choose best immediate move among valid deltas
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d_to_t = cheb(nx, ny, tx, ty)
            d_to_o = cheb(nx, ny, ox, oy)
            # Prefer reducing distance to target, avoid clutter, and don't walk too close to opponent
            val = d_to_t * 5 + obs_pen(nx, ny) * 2 - d_to_o
            # Tie-break deterministically
            candidates.append((val, dx, dy, nx, ny))
    if not candidates:
        return [0, 0]
    candidates.sort()
    _, dx, dy, _, _ = candidates[0]
    return [int(dx), int(dy)]