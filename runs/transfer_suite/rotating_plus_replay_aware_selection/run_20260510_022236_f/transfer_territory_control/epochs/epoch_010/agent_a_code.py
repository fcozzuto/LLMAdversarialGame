def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(v):
        s = set()
        if not v:
            return s
        for p in v:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = to_set(observation.get("obstacles"))
    resources = list(to_set(observation.get("resources")).union())
    unclaimed = list(to_set(observation.get("unclaimed_cells") or observation.get("unclaimed") or []))
    resources = [p for p in resources if 0 <= p[0] < w and 0 <= p[1] < h]
    unclaimed = [p for p in unclaimed if 0 <= p[0] < w and 0 <= p[1] < h]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    target = None
    if resources:
        target = min(resources, key=lambda p: (man(sx, sy, p[0], p[1]), p[0], p[1]))
    elif unclaimed:
        target = min(unclaimed, key=lambda p: (man(sx, sy, p[0], p[1]), p[0], p[1]))
    else:
        target = (ox, oy)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    tx, ty = target
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = man(nx, ny, tx, ty)
        near_opp = man(nx, ny, ox, oy)
        val = -d + 0.1 * near_opp
        cand = (val, -d, -near_opp, dx, dy)
        if best is None or cand > best:
            best = cand
    if best is None:
        return [0, 0]
    return [int(best[3]), int(best[4])]