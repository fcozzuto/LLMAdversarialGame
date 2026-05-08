def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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
                try:
                    s.add((int(p[0]), int(p[1])))
                except:
                    pass
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    resources = toset(observation.get("resources"))
    if not unclaimed and resources:
        unclaimed = set(resources)
    myT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))

    if not unclaimed:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    tx, ty = None, None
    bestd = None
    for (x, y) in unclaimed:
        if (x, y) in obstacles:
            continue
        d = md(sx, sy, x, y)
        if bestd is None or d < bestd or (d == bestd and (x, y) < (tx, ty)):
            bestd = d
            tx, ty = x, y
    if tx is None:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    bestmove = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nd = md(nx, ny, tx, ty)
        safety = -md(nx, ny, ox, oy)
        opp_touch = 0
        for ax in (-1, 0, 1):
            for by in (-1, 0, 1):
                if (nx + ax, ny + by) in oppT:
                    opp_touch += 1
        on_my = 1 if (nx, ny) in myT else 0
        on_un = 1 if (nx, ny) in unclaimed else 0
        score = (-nd) + (0.6 * safety) + (2.0 * on_un) + (0.2 * on_my) - (1.5 * opp_touch)
        key = (score, -nd, -safety, -on_un, on_my, nx, ny)
        if best is None or key > best:
            best = key
            bestmove = [dx, dy]
    return bestmove