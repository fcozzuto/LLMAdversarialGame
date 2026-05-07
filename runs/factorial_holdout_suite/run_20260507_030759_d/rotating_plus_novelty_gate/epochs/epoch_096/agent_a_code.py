def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    if (sx, sy) in obs:
        return [0, 0]

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            r = (p[0], p[1])
            if r not in obs:
                res.append(r)
    if not res:
        return [0, 0]
    if (sx, sy) in res:
        return [0, 0]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    best_key = None
    for rx, ry in res:
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        # Strongly prefer resources where we arrive earlier; break ties by smaller ds and then coordinate.
        key = (ds - do, ds, do, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    legal_moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or ny < 0 or nx >= w or ny >= h:
                continue
            if (nx, ny) in obs:
                continue
            new_ds = md(nx, ny, tx, ty)
            new_adv = new_ds - md(ox, oy, tx, ty)
            # Prefer reaching target faster; slight preference for collecting nearer resources.
            collectible = 0
            if (nx, ny) in res:
                collectible = -1000
            # Penalize moving adjacent to obstacles (avoid tight spots).
            adj_pen = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    px, py = nx + ax, ny + ay
                    if (px, py) in obs:
                        adj_pen += 1
            key = (new_adv, new_ds, adj_pen, collectible, dx, dy)
            legal_moves.append((key, dx, dy))
    if not legal_moves:
        return [0, 0]
    legal_moves.sort(key=lambda t: t[0])
    _, dx, dy = legal_moves[0]
    return [int(dx), int(dy)]