def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            obs.add((p[0], p[1]))

    resources = observation.get("resources") or []
    targets = []
    for p in resources:
        if p is not None and len(p) >= 2:
            targets.append((p[0], p[1]))

    if not targets:
        op = observation.get("opponent_position")
        if op is not None and len(op) >= 2:
            targets = [(op[0], op[1])]
        else:
            targets = [(sx, sy)]

    def best_score(x, y):
        best = None
        for tx, ty in targets:
            d = (x - tx) * (x - tx) + (y - ty) * (y - ty)
            if best is None or d < best:
                best = d
        if best is None:
            return 0
        return -best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = -10**18
    best_mv = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        sc = best_score(nx, ny)
        if sc > best:
            best = sc
            best_mv = (dx, dy)

    return [best_mv[0], best_mv[1]]