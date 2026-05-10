def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    def norm_pos(p):
        try:
            x, y = p
            return int(x), int(y)
        except Exception:
            return None

    sp = norm_pos(observation.get("self_position"))
    op = norm_pos(observation.get("opponent_position"))
    if sp is None:
        return [0, 0]
    sx, sy = sp

    obstacles = set()
    obs = observation.get("obstacles") or []
    for o in obs:
        q = norm_pos(o)
        if q is not None:
            obstacles.add(q)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    resources = observation.get("resources") or []
    respos = []
    for r in resources:
        q = norm_pos(r)
        if q is not None:
            respos.append(q)
    if not respos:
        if op is not None:
            ox, oy = op
        else:
            ox, oy = sx, sy

        best = None
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            dist = abs(nx - ox) + abs(ny - oy)
            score = -dist  # maximize distance from opponent => minimize -dist
            if best_score is None or score < best_score:
                best_score = score
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dmin = None
        for rx, ry in respos:
            d = abs(nx - rx) + abs(ny - ry)
            if dmin is None or d < dmin:
                dmin = d
        score = dmin if dmin is not None else 10**9
        if best_score is None or score < best_score:
            best_score = score
            best = (dx, dy)
    return [best[0], best[1]] if best is not None else [0, 0]