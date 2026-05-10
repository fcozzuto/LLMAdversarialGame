def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    scores = observation.get("scores", None)
    self_score = 0
    opp_score = 0
    if isinstance(scores, (list, tuple)) and len(scores) >= 2:
        try:
            self_score = float(scores[0])
            opp_score = float(scores[1])
        except:
            pass
    elif isinstance(scores, dict):
        for k in ("self", "me", "player", "agent"):
            if k in scores:
                try:
                    self_score = float(scores[k])
                except:
                    pass
        for k in ("opponent", "opp", "enemy"):
            if k in scores:
                try:
                    opp_score = float(scores[k])
                except:
                    pass

    evade = self_score >= opp_score

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs):
            continue
        # primary: move toward nearest resource if any (or stay if none)
        if res:
            mind = 10**18
            for rx, ry in res:
                ddx, ddy = nx - rx, ny - ry
                d = ddx * ddx + ddy * ddy
                if d < mind:
                    mind = d
            # prefer smaller distance to resources
            val = -mind * 1000
        else:
            val = 0

        # secondary: decide pursue/evade based on score
        ddx, ddy = nx - ox, ny - oy
        d2 = ddx * ddx + ddy * ddy
        if evade:
            val += d2
        else:
            val -= d2

        # tiny deterministic tie-breaker
        val += (dx == 0 and dy == 0) * (-1)
        if best is None or val > best_val:
            best = [dx, dy]
            best_val = val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]