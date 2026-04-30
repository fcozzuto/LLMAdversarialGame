def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def dist(a, b):
        ax, ay = a; bx, by = b
        return abs(ax - bx) + abs(ay - by)

    neighbors = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        nx = clamp(nx, 0, w - 1); ny = clamp(ny, 0, h - 1)
        if (nx, ny) in obstacles:
            for ddx, ddy in sorted(neighbors, key=lambda t: (abs((sx + t[0]) - tx) + abs((sy + t[1]) - ty))):
                px, py = clamp(sx + ddx, 0, w - 1), clamp(sy + ddy, 0, h - 1)
                if (px, py) not in obstacles:
                    return [ddx, ddy]
        return [dx, dy]

    best = None
    for r in resources:
        if r in obstacles:
            continue
        dself = dist((sx, sy), r)
        dopp = dist((ox, oy), r)
        val = dopp - dself  # prefer resources opponent is less able to reach soon
        key = (val, -dself, r[0], r[1])
        if best is None or key > best[0]:
            best = (key, r)

    target = best[1]
    tx, ty = target
    want_dx = 0 if tx == sx else (1 if tx > sx else -1)
    want_dy = 0 if ty == sy else (1 if ty > sy else -1)

    def move_ok(ddx, ddy):
        nx, ny = clamp(sx + ddx, 0, w - 1), clamp(sy + ddy, 0, h - 1)
        return (nx, ny) not in obstacles

    ordered = sorted(neighbors, key=lambda t: (
        (t[0] != want_dx or t[1] != want_dy),  # prefer aligning with direct delta
        dist((clamp(sx + t[0], 0, w - 1), clamp(sy + t[1], 0, h - 1)), (tx, ty))
    ))
    for ddx, ddy in ordered:
        if move_ok(ddx, ddy):
            return [ddx, ddy]
    return [0, 0]