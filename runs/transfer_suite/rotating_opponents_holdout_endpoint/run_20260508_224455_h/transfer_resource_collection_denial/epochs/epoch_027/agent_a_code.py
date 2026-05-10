def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Pick a resource where we can arrive earlier (or at least not later), and break ties by closeness.
    best = None
    for rx, ry in resources:
        st = cheb(sx, sy, rx, ry)
        ot = cheb(ox, oy, rx, ry)
        # "Ahead" is negative; we prefer ahead, then self closeness, then coordinate determinism.
        key = (st - ot, st, ry, rx)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    rx, ry = best[1]

    # Choose next step that avoids moving into obstacles and advances toward target.
    target_dx = 0 if rx == sx else (1 if rx > sx else -1)
    target_dy = 0 if ry == sy else (1 if ry > sy else -1)

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            d = cheb(nx, ny, rx, ry)
            # Encourage moves that align with desired direction; deterministic tie-break by dx,dy.
            align = -((dx - target_dx) * (dx - target_dx) + (dy - target_dy) * (dy - target_dy))
            # Also slightly prefer staying if already optimal (deterministic).
            stay_pen = 0 if (dx != 0 or dy != 0) else 0.01
            key = (d, stay_pen, -(align), dy, dx)
            candidates.append((key, [dx, dy]))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: t[0])
    return candidates[0][1]