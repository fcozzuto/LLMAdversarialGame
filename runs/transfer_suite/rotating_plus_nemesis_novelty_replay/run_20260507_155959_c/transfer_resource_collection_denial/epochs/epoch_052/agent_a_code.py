def choose_move(observation):
    w = observation.get("grid_width", 0); h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    if (sx, sy) in obs:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None; bestv = -10**9
    res_set = set(res)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        if res:
            target = None; self_min = 10**9
            for rx, ry in res:
                d = md(nx, ny, rx, ry)
                if d < self_min:
                    self_min = d; target = (rx, ry)
            tx, ty = target
            self_d = md(nx, ny, tx, ty)
            opp_d = md(ox, oy, tx, ty)
            here = 1 if (nx, ny) in res_set else 0
            val = (here * 10**6) + (opp_d - self_d) * 1000 - self_d
        else:
            val = md(nx, ny, ox, oy)  # move away if no resources
        if val > bestv or (val == bestv and (dx, dy) < best):
            bestv = val; best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]