def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position", (None, None))
    ox = int(ox) if ox is not None else None
    oy = int(oy) if oy is not None else None

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, dict):
            if "position" in r:
                rr = r["position"]
                if isinstance(rr, (list, tuple)) and len(rr) >= 2:
                    res.append((int(rr[0]), int(rr[1])))
            elif "x" in r and "y" in r:
                res.append((int(r["x"]), int(r["y"])))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))

    def manhattan(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not res:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best_s = -10**18
        best = (0, 0)
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            d = manhattan(nx, ny, cx, cy)
            s = -d
            if s > best_s or (s == best_s and (dx, dy) < best):
                best_s, best = s, (dx, dy)
        return [best[0], best[1]]

    best_s = -10**18
    best = (0, 0)
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        d1 = 10**18
        d2 = 10**18
        for tx, ty in res:
            d = manhattan(nx, ny, tx, ty)
            if d < d1:
                d1 = d
            if ox is not None and oy is not None:
                do = manhattan(ox, oy, tx, ty)
                if do < d2:
                    d2 = do
        if ox is None or oy is None:
            s = -d1
        else:
            s = (-d1) + (0.1 * d2)
        if s > best_s or (s == best_s and (dx, dy) < best):
            best_s, best = s, (dx, dy)
    return [best[0], best[1]]