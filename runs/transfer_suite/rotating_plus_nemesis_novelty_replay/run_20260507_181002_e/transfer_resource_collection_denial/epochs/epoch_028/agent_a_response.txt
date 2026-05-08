def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def to_xy(v):
        if isinstance(v, (list, tuple)) and len(v) == 2:
            return int(v[0]), int(v[1])
        if isinstance(v, dict):
            p = v.get("position", v.get("pos", None))
            if isinstance(p, (list, tuple)) and len(p) == 2:
                return int(p[0]), int(p[1])
        return None

    sp = to_xy(observation.get("self_position", [0, 0])) or (0, 0)
    op = to_xy(observation.get("opponent_position", [0, 0])) or (0, 0)
    sx, sy = sp
    ox, oy = op

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for o in obstacles:
        t = to_xy(o)
        if t:
            x, y = t
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        t = to_xy(r)
        if t:
            x, y = t
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def man(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Target selection: prefer resources we can reach strictly sooner; if none, minimize opponent advantage.
    if res:
        best = None
        for cell in res:
            sd = man((sx, sy), cell)
            od = man((ox, oy), cell)
            safe = 1 if sd < od else 0
            threat = 1 if od <= sd else 0
            # Primary: safe margin; secondary: smaller sd; tertiary: reduce od.
            key = (safe, (od - sd), -sd, -od, cell[0] * 10 + cell[1])
            if best is None or key > best[0]:
                best = (key, cell)
        target = best[1]
    else:
        target = (sx, sy)

    # One-step decision with obstacle-aware scoring.
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        self_d = man((nx, ny), target)
        opp_d = man((ox, oy), target)
        safe_bonus = 1 if self_d < opp_d else 0
        # If currently threatened by opponent (at equal/closer), add slight repulsion from their position.
        opp_rep = -(man((nx, ny), (ox, oy)))
        score = (safe_bonus, (opp_d - self_d), -self_d, opp_rep, -(abs(nx - ox) + abs(ny - oy)))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]