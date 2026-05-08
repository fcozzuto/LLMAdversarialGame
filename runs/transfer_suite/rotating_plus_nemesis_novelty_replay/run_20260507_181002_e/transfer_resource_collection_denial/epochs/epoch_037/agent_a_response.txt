def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    def to_xy(v):
        if isinstance(v, (list, tuple)) and len(v) == 2:
            return int(v[0]), int(v[1])
        if isinstance(v, dict):
            p = v.get("position", v.get("pos", None))
            if isinstance(p, (list, tuple)) and len(p) == 2:
                return int(p[0]), int(p[1])
        return None

    p = to_xy(observation.get("self_position", [0, 0])) or (0, 0)
    o = to_xy(observation.get("opponent_position", [0, 0])) or (0, 0)
    sx, sy = p
    ox, oy = o

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for t in obstacles:
        xy = to_xy(t)
        if xy:
            x, y = xy
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        xy = to_xy(r)
        if xy:
            x, y = xy
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Counter sweep: prefer targets that are hard for the opponent to reach first,
    # and also prefer moves that increase separation from opponent if advantage is small.
    target = None
    best = None
    for rx, ry in res:
        self_d = abs(rx - sx) + abs(ry - sy)
        opp_d = abs(rx - ox) + abs(ry - oy)
        adv = opp_d - self_d  # positive means we can arrive sooner
        # Slightly bias toward upper-variance (not just shortest) to avoid row sweeps
        spread = (abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2)) * 0.01
        key = (adv + spread, -self_d, -opp_d)
        if best is None or key > best:
            best = key
            target = (rx, ry)

    tx, ty = target
    # Choose best feasible neighbor by one-step lookahead on that target with separation tie-break.
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        self_d = abs(tx - nx) + abs(ty - ny)
        opp_d = abs(tx - ox) + abs(ty - oy)
        cur_adv = opp_d - self_d
        sep = abs(ox - nx) + abs(oy - ny)
        # If we are not clearly ahead, prioritize separation to reduce opponent抢夺.
        score = (cur_adv, sep, -self_d)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]