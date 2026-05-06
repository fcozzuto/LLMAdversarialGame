def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    s = observation.get("self_position", [0, 0])
    o = observation.get("opponent_position", [0, 0])
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obstacles:
                resources.append((x, y))
    if not (0 <= sx < w and 0 <= sy < h) or not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def score_for_target(rx, ry):
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        return (ds - do, ds, rx, ry)

    opp_best = None
    opp_ds = None
    for rx, ry in resources:
        ds_o = man(ox, oy, rx, ry)
        if opp_ds is None or ds_o < opp_ds or (ds_o == opp_ds and (rx, ry) < opp_best):
            opp_ds = ds_o
            opp_best = (rx, ry)

    chosen = None
    best = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        if chosen is None:
            chosen = (rx, ry)
            best = score_for_target(rx, ry)
        else:
            # If opponent can reach opp_best very fast, prefer a resource where we are closer.
            if rx == opp_best[0] and ry == opp_best[1] and man(ox, oy, rx, ry) <= ds + 1:
                continue
            t = score_for_target(rx, ry)
            if t < best:
                best = t
                chosen = (rx, ry)
    if chosen is None:
        chosen = min(resources)

    tx, ty = chosen
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # Tie-break deterministically by dx,dy order by comparing tuple (val, dx, dy)
        val = man(nx, ny, tx, ty) - 0.5 * (man(nx, ny, ox, oy) < man(sx, sy, ox, oy))
        cand = (val, dx, dy)
        if best_val is None or cand < best_val:
            best_val = cand
            best_move = [dx, dy]
    return best_move