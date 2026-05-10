def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    try:
        x = int(x); y = int(y); ox = int(ox); oy = int(oy)
    except:
        x = 0; y = 0; ox = 0; oy = 0

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                res.append((rx, ry))

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    bestv = -10**18
    if not res:
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        self_here = (nx, ny)
        # Race heuristic: pick resource maximizing (opp_dist - self_dist), tie-break by self_dist
        v = -10**18
        for r in res:
            sd = man(self_here, r)
            od = man((ox, oy), r)
            cand = (od - sd) * 1000 - sd
            if cand > v:
                v = cand
        # Mild preference to drift toward center early to reduce stalemates
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_pen = (abs(nx - cx) + abs(ny - cy)) * (0.02 if observation.get("turns_remaining", 0) > 0 else 0.0)
        v -= center_pen
        if v > bestv:
            bestv = v
            best = [dx, dy]

    return best if best is not None else [0, 0]