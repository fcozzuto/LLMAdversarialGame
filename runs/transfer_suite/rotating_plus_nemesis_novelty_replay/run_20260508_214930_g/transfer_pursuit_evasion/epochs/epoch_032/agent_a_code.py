def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs_list = observation.get("obstacles", []) or []
    obs = set()
    for b in obs_list:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res_list = observation.get("resources", []) or []
    targets = []
    for r in res_list:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h:
                targets.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = -10**18
    opp_dist_now = abs(sx - ox) + abs(sy - oy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        val = 0
        if targets:
            dmin = None
            for tx, ty in targets:
                d = abs(nx - tx) + abs(ny - ty)
                if dmin is None or d < dmin:
                    dmin = d
            val += 1000 - 30 * dmin
        if opp_dist_now <= 2:
            val -= 120 * (abs(nx - ox) + abs(ny - oy))  # run from opponent if close
        else:
            val += 10 * (abs(nx - ox) + abs(ny - oy))  # keep some distance
        if (nx, ny) == (ox, oy):
            val -= 2000
        if best is None or val > best_val or (val == best_val and (dx, dy) < best):
            best = (dx, dy)
            best_val = val
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]