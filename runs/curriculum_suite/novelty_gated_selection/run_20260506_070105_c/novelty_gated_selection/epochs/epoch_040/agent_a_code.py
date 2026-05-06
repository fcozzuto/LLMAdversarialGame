def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def pos(v, default):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            x, y = int(v[0]), int(v[1])
        elif isinstance(v, dict):
            x = v.get("x", v.get("X", v.get("col", v.get("cx", default[0]))))
            y = v.get("y", v.get("Y", v.get("row", v.get("cy", default[1]))))
            x, y = int(x), int(y)
        else:
            return default
        if 0 <= x < w and 0 <= y < h:
            return (x, y)
        return default

    sx, sy = pos(observation.get("self_position", None), (0, 0))
    ox, oy = pos(observation.get("opponent_position", None), (w - 1, h - 1))

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        p = pos(o, None)
        if p is not None:
            obstacles.add(p)

    res = []
    for r in (observation.get("resources", []) or []):
        p = pos(r, None)
        if p is not None and p not in obstacles:
            res.append(p)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None

    def score_to(tx, ty):
        dme = abs(sx - tx) + abs(sy - ty)
        dop = abs(ox - tx) + abs(oy - ty)
        return (dop - dme, -dme)

    target = None
    if res:
        target = min(res, key=lambda p: (abs(sx - p[0]) + abs(sy - p[1]), abs(ox - p[0]) + abs(oy - p[1])))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        if target is not None:
            sc1 = score_to(target[0], target[1])
        else:
            sc1 = (0, -(abs(nx - ox) + abs(ny - oy)))
        sc = (sc1[0], sc1[1], -abs(nx - ox) - abs(ny - oy), -abs(nx - (w - 1)) - abs(ny - (h - 1)))
        if best_score is None or sc > best_score:
            best_score = sc
            best = (dx, dy)

    if best is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    return [best[0], best[1]]