def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        for p in (v or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    targets = toset(observation.get("unclaimed_cells"))
    if not targets:
        targets = toset(observation.get("resources"))
    if not targets:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dt = 10**9
        for tx, ty in targets:
            d = abs(nx - tx) + abs(ny - ty)
            if d < dt:
                dt = d
        do = abs(nx - ox) + abs(ny - oy)
        cand = (dt, -do, dx, dy)
        if best is None or cand < best:
            best = cand

    if best is None:
        return [0, 0]
    return [best[2], best[3]]