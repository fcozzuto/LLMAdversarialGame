def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    res = [(r[0], r[1]) for r in resources if inb(r[0], r[1]) and (r[0], r[1]) not in obs]
    if not res:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Score each resource by how much closer we are than the opponent; ignore those they are strictly closer to unless none better.
    scored = []
    best_gap = None
    for rx, ry in res:
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        gap = ds - do
        # Prefer nearer targets and those where we can reach with smaller gap; mild y-bias to reduce being swept vertically.
        val = (gap * 1000) + (ds * 3) + (abs(ry - (sy + (1 if ry > sy else -1 if ry < sy else 0))) * 1)
        scored.append((val, gap, rx, ry))
        if best_gap is None or gap < best_gap:
            best_gap = gap

    # Prefer resources where we are not worse (gap <= best_gap+0). If all worse, still take the least-worse.
    best = None
    for val, gap, rx, ry in scored:
        if best is None:
            best = (val, gap, rx, ry)
            continue
        bv, bg, bx, by = best
        # Primary: smallest gap; Secondary: smallest val; Tertiary: smallest ds
        ds = md(sx, sy, rx, ry)
        bds = md(sx, sy, bx, by)
        if gap < bg or (gap == bg and (val < bv or (val == bv and ds < bds))):
            best = (val, gap, rx, ry)

    _, _, tx, ty = best

    # Choose move that reduces distance to target, with diagonal preference and tie-break to maintain spacing from opponent.
    best_move = (0, 0)
    best_score = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        ds = md(nx, ny, tx, ty)
        # tie-break: keep opponent further from target (or at least not closer than us after move)
        do = md(ox, oy, tx, ty)
        # also avoid moving into "opponent next vicinity" by discouraging getting too aligned in same row toward opponent
        opp_dx = abs((nx - ox))
        opp_dy = abs((ny - oy))
        score = (ds * 10000) + (do * 0) + (opp_dx + opp_dy) + (0 if (dx != 0 and dy != 0) else 0.25)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]