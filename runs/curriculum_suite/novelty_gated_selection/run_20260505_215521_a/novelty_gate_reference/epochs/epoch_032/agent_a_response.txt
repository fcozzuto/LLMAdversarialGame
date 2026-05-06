def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    resources = observation.get("resources", []) or []
    res_list = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs_set:
                res_list.append((x, y))
    if not res_list:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def risk(x, y):
        rr = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    if (x + dx, y + dy) in obs_set:
                        rr += 1
        return rr

    best = None
    best_val = None
    for cx, cy in res_list:
        sd = man(sx, sy, cx, cy)
        od = man(ox, oy, cx, cy)
        tie = 0 if (cx == sx or cy == sy) else 0.2  # slight preference toward same row/col
        val = (sd - 0.85 * od) + 0.06 * sd + 0.35 * risk(cx, cy) + tie
        if best_val is None or val < best_val:
            best_val = val
            best = (cx, cy)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # If blocked, choose best alternative among legal deltas (still deterministic).
    candidates = [(dx, dy), (dx, 0), (0, dy), (0, 0), (dx, -dy), (-dx, dy), (-dx, 0), (0, -dy), (-dx, -dy)]
    for cdx, cdy in candidates:
        nx, ny = sx + cdx, sy + cdy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
            # Prefer moves that reduce distance to chosen target and avoid giving opponent a big advantage.
            nsd = man(nx, ny, tx, ty)
            nod = man(nx, ny, ox, oy)
            # nod unused magnitude but keeps stable preference; small tie-break on risk.
            val = nsd + 0.02 * nod + 0.2 * risk(nx, ny)
            if best_val is None:
                best_val = val
            return [int(cdx), int(cdy)]

    return [0, 0]