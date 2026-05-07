def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not res:
        tx, ty = w // 2, h // 2
    else:
        best = None
        for x, y in res:
            myd = md(sx, sy, x, y)
            opd = md(ox, oy, x, y)
            adv = opd - myd  # positive means we're closer
            # Encourage closer targets and stronger advantage
            key = (-adv, myd, abs(x - (w - 1)), abs(y - (h - 1)))
            if best is None or key < best[0]:
                best = (key, (x, y))
        tx, ty = best[1]

    best_move = (0, 0)
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        dist = md(nx, ny, tx, ty)
        tx_change = abs(nx - tx) + abs(ny - ty)
        key = (dist, tx_change, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]