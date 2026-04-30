def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [w - 1, h - 1]))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def d2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    if (sx, sy) in obs:
        sx, sy = sx, sy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_key = (-10**18, -10**18)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy
        if not res:
            # fallback: move towards center while avoiding obstacles
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            key = (-(d2(nx, ny, cx, cy)), 0)
        else:
            # choose best resource for this move by "lead"
            max_lead = -10**18
            min_selfdist = 10**18
            for tx, ty in res:
                selfdist = d2(nx, ny, tx, ty)
                oppdist = d2(ox, oy, tx, ty)
                lead = oppdist - selfdist
                if lead > max_lead or (lead == max_lead and selfdist < min_selfdist):
                    max_lead = lead
                    min_selfdist = selfdist
            # prefer moves that increase lead; tie-break by getting closer
            key = (max_lead, -min_selfdist)
        if key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]