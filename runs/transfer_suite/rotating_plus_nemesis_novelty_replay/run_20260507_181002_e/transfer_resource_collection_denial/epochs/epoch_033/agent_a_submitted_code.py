def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position", [0, 0]) or [0, 0]
    o = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for it in obstacles:
        if isinstance(it, (list, tuple)) and len(it) >= 2:
            x, y = int(it[0]), int(it[1])
        elif isinstance(it, dict):
            p = it.get("position", it.get("pos", None))
            if not (isinstance(p, (list, tuple)) and len(p) >= 2):
                continue
            x, y = int(p[0]), int(p[1])
        else:
            continue
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for it in resources:
        if isinstance(it, (list, tuple)) and len(it) >= 2:
            x, y = int(it[0]), int(it[1])
        elif isinstance(it, dict):
            p = it.get("position", it.get("pos", None))
            if not (isinstance(p, (list, tuple)) and len(p) >= 2):
                continue
            x, y = int(p[0]), int(p[1])
        else:
            continue
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
            res.append((x, y))

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        if res:
            d_self = min(manh((nx, ny), r) for r in res)
            d_opp = min(manh((ox, oy), r) for r in res)
            score = (1000 - d_self) - (500 - d_opp)
        else:
            score = -man((nx, ny), (ox, oy)) - man((nx, ny), (w // 2, h // 2))
        if score > best_score:
            best_score = score
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]