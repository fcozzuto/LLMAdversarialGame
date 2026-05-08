def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        if not v:
            return s
        for p in v:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    res = toset(observation.get("resources"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))

    if not unclaimed and res:
        unclaimed = set(res)
    targets = unclaimed | res
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    cand_targets = list(targets) if targets else []
    if not cand_targets:
        cand_targets = [(ox, oy)]
    best = None
    bestv = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        dmin = min(dist(nx, ny, tx, ty) for (tx, ty) in cand_targets)
        v = -dmin
        if (nx, ny) in unclaimed:
            v += 6
        if (nx, ny) in res:
            v += 4
        if (nx, ny) in selfT:
            v += 1
        if (nx, ny) in oppT:
            v += 2
        if dx == 0 and dy == 0:
            v -= 1
        if best is None or v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = [dx, dy]

    if best is not None:
        return best
    return [0, 0]