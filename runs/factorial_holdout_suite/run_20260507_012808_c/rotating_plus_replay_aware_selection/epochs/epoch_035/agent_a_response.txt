def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def clamp(dx, dy):
        nx, ny = sx + dx, sy + dy
        if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
            return [0, 0]
        if not (0 <= nx < w and 0 <= ny < h):
            return [0, 0]
        if (nx, ny) in obstacles:
            return [0, 0]
        return [dx, dy]

    def neigh_obst(x, y):
        p = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                if (x + ddx, y + ddy) in obstacles:
                    p += 1
        return p

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        targets = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = targets[0] if (sx <= w // 2) else targets[2]
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        for a in [(dx, dy), (dx, 0), (0, dy), (0, 0)]:
            m = clamp(a[0], a[1])
            if m != [0, 0] or (sx, sy) in obstacles:
                return m
        return [0, 0]

    best = None
    best_key = None
    self_near = neigh_obst(sx, sy)
    for rx, ry in resources:
        sd = man((sx, sy), (rx, ry))
        od = man((ox, oy), (rx, ry))
        if sd == 0:
            return [0, 0]
        # Prefer resources where we are closer than opponent (or at least not far behind).
        advantage = od - sd
        # Minor tie-break discouraging risky nearby obstacle adjacency.
        key = (-(advantage - 0.15 * self_near), sd, abs(rx - sx) + abs(ry - sy))
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = [(dx, dy), (dx, 0), (0, dy), (0, 0)]
    for cdx, cdy in candidates:
        mv = clamp(cdx, cdy)
        if mv != [0, 0] or cdx == 0 and cdy == 0:
            return mv
    return [0, 0]