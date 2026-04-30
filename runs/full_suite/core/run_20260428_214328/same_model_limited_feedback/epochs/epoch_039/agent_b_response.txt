def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx*dx + dy*dy

    if resources:
        # Choose target: closest resource; tie-break lexicographically
        target = min(resources, key=lambda p: (dist2((sx, sy), p), p[1], p[0]))
        tx, ty = target
    else:
        target = (cx, cy)
        tx, ty = target

    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        # Prefer reducing distance to target; also avoid opponent slightly
        ndt = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        ndo = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        score = (ndt, -ndo, abs(dx) + abs(dy), dy, dx)
        if best is None or score < best[0]:
            best = (score, [dx, dy])

    return best[1] if best is not None else [0, 0]