def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def to_set(x):
        s = set()
        if not x:
            return s
        for p in x:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                try:
                    s.add((int(p[0]), int(p[1])))
                except:
                    pass
        return s

    obs = to_set(observation.get("obstacles", []))
    res = to_set(observation.get("resources", []))
    un = to_set(observation.get("unclaimed_cells", observation.get("unclaimed", [])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    man = lambda x1, y1, x2, y2: abs(x1 - x2) + abs(y1 - y2)

    best = None
    best_score = -10**18

    targets = list(res) if res else []
    if not targets and un:
        targets = list(un)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        score = 0
        if targets:
            md = min(man(nx, ny, tx, ty) for tx, ty in targets)
            score += 1000 - md * 10
            if (nx, ny) in res:
                score += 500
        else:
            score += 100 - man(nx, ny, ox, oy) * 2
        if (nx, ny) == (ox, oy):
            score -= 10000
        if best is None or score > best_score or (score == best_score and (dx, dy) < best):
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]