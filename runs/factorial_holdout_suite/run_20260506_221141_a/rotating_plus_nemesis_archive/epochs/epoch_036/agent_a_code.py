def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [7, 7])
    resources = observation.get("resources", []) or []
    obstacles_raw = observation.get("obstacles", []) or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and inb(x, y):
                obs.add((x, y))

    if not (isinstance(sx, int) and isinstance(sy, int) and inb(sx, sy)):
        return [0, 0]
    if not (isinstance(ox, int) and isinstance(oy, int) and inb(ox, oy)):
        ox, oy = w - 1, h - 1

    rlist = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and inb(x, y) and (x, y) not in obs:
                rlist.append((x, y))
    if not rlist:
        return [0, 0]

    cand = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if inb(sx + dx, sy + dy) and (sx + dx, sy + dy) not in obs]
    if not cand:
        return [0, 0]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    best_score = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        move_score = None
        for tx, ty in rlist:
            sd = md(nx, ny, tx, ty)
            od = md(ox, oy, tx, ty)
            adv = od - sd  # positive means we are closer than opponent
            # Prefer increasing advantage, then shorter distance
            score = (adv, -sd)
            if move_score is None or score > move_score:
                move_score = score
        if best_score is None or move_score > best_score:
            best_score = move_score
            best = (dx, dy)
    return [int(best[0]), int(best[1])]