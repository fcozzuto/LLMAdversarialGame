def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(v):
        s = set()
        for p in v or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obs = to_set(observation.get("obstacles"))
    un = to_set(observation.get("unclaimed_cells", observation.get("unclaimed")))
    res = to_set(observation.get("resources"))
    st = to_set(observation.get("self_territory"))
    ot = to_set(observation.get("opponent_territory"))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_obstacle(x, y):
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if (x + ax, y + ay) in obs:
                    return True
        return False

    def score_cell(x, y):
        if (x, y) in obs:
            return -10**9
        d_opp = abs(x - ox) + abs(y - oy)
        risk = 3 if adj_obstacle(x, y) else 0
        s = 0
        if (x, y) in res:
            s += 18
        if (x, y) in un:
            s += 14
        if (x, y) in ot:
            s += 9
        if (x, y) in st:
            s += 2
        # Intercept: prefer moving closer to opponent early, but avoid being on top of them
        s += 6 * (8 - min(d_opp, 8))
        if d_opp <= 1:
            s -= 6
        s -= risk
        return s

    best_dx, best_dy, best_sc = 0, 0, -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        sc = score_cell(nx, ny)
        # slight tie-break: prefer diagonal/forward-ish towards center
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        tie = -((nx - cx) ** 2 + (ny - cy) ** 2) * 1e-6
        sc += tie
        if sc > best_sc:
            best_sc, best_dx, best_dy = sc, dx, dy

    return [int(best_dx), int(best_dy)]