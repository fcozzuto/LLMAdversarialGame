def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obst = observation.get("obstacles", []) or []
    obstacles = set(tuple(p) for p in obst)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a + b

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if resources:
        target = min(resources, key=lambda r: (md(sx, sy, r[0], r[1]), -md(ox, oy, r[0], r[1]), r[0], r[1]))
        tx, ty = target[0], target[1]
    else:
        tx = w - 1 if ox < w // 2 else 0
        ty = h - 1 if oy < h // 2 else 0

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d1 = md(nx, ny, tx, ty)
        d2 = md(nx, ny, ox, oy)
        cur2 = md(sx, sy, ox, oy)
        closer = 1 if d2 < cur2 else 0
        key = (d1, -d2, closer, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]