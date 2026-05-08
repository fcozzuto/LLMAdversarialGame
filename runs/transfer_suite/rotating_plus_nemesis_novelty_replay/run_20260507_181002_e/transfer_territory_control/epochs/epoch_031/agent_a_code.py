def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        if v:
            for p in v:
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    x, y = int(p[0]), int(p[1])
                    s.add((x, y))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    resources = toset(observation.get("resources"))
    if not unclaimed and resources:
        unclaimed = set(resources)

    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def score_cell(x, y):
        if (x, y) in obstacles:
            return -10**9
        s = 0
        if (x, y) in unclaimed:
            s += 120
        if (x, y) in resources:
            s += 40
        if (x, y) in oppT:
            s -= 80
        if (x, y) in selfT:
            s += 10
        md = abs(x - ox) + abs(y - oy)
        s += md * 3
        cx, cy = (w - 1) // 2, (h - 1) // 2
        s -= (abs(x - cx) + abs(y - cy)) * 1
        return s

    best = None
    best_sc = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sc = score_cell(nx, ny)
        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best