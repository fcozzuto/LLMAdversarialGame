def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                res.append((rx, ry))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def manh(ax, ay, bx, by):
        d1 = ax - bx
        if d1 < 0:
            d1 = -d1
        d2 = ay - by
        if d2 < 0:
            d2 = -d2
        return d1 + d2

    def best_res_dist(px, py):
        if not res:
            return 10**9
        best = 10**9
        for rx, ry in res:
            d = manh(px, py, rx, ry)
            if d < best:
                best = d
        return best

    def cell_value(px, py):
        if not res:
            return 0
        # Encourage nearing our best resource and pulling away from opponent's best.
        sd = 10**9
        od = 10**9
        for rx, ry in res:
            ds = manh(px, py, rx, ry)
            if ds < sd:
                sd = ds
            do = manh(ox, oy, rx, ry)
            if do < od:
                od = do
        # Slightly prefer capturing sooner: exact resource cell is best.
        on_res = 1 if (px, py) in res else 0
        return (od - sd) + 0.25 * on_res - 0.02 * (sd + od)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**30

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        # Prefer moves that reduce our distance to resources, and improve relative position.
        sd0 = best_res_dist(x, y)
        sd1 = best_res_dist(nx, ny)
        cap_bonus = 0
        if (nx, ny) in res:
            cap_bonus = 5.0
        score = 3.0 * (sd0 - sd1) + cell_value(nx, ny) + cap_bonus
        # Deterministic tie-break: deterministic ordering by dx,dy
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]