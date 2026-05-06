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

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def risk(x, y):
        rr = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if (nx, ny) in obs_set:
                        rr += 1
        return rr

    best_r = None
    best_v = -10**18
    for rx, ry in res_list:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        v = (do - ds) * 10 - ds - 0.5 * risk(rx, ry)
        if v > best_v:
            best_v = v
            best_r = (rx, ry)

    rx, ry = best_r
    dx = 0 if rx == sx else (1 if rx > sx else -1)
    dy = 0 if ry == sy else (1 if ry > sy else -1)

    nx, ny = sx + dx, sy + dy
    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
        return [dx, dy]

    # Fallback: choose the best among allowed deltas that move toward target without hitting obstacles.
    candidates = []
    for ddx in (-1, 0, 1):
        for ddy in (-1, 0, 1):
            if ddx == 0 and ddy == 0:
                continue
            px, py = sx + ddx, sy + ddy
            if 0 <= px < w and 0 <= py < h and (px, py) not in obs_set:
                candidates.append((man(px, py, rx, ry), ddx, ddy, risk(px, py)))
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (t[0], t[3]))
    return [candidates[0][1], candidates[0][2]]