def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        try:
            obs.add((p[0], p[1]))
        except Exception:
            pass

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        try:
            res.append((p[0], p[1]))
        except Exception:
            pass

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def score_cell(x, y):
        if (x, y) in obs:
            return -10**9
        s = 0
        if res:
            ds = min(man((x, y), r) for r in res)
            do = min(man((ox, oy), r) for r in res)
            s += 30 - ds
            s += 10 if ds <= do else 0
        else:
            s += -(man((x, y), (0, 0)) if (ox + oy) > (sx + sy) else man((x, y), (w - 1, h - 1)))
        return s

    best = None
    best_s = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            sc = score_cell(nx, ny)
            if sc > best_s or (sc == best_s and (dx, dy) < best):
                best_s = sc
                best = (dx, dy)
    return list(best if best is not None else (0, 0))