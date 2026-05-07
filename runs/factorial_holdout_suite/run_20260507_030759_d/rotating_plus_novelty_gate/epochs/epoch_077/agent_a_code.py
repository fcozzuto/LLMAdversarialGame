def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]
    if (sx, sy) in set(res):
        return [0, 0]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    opp = (ox, oy)

    def best_adv(pos):
        best = None
        for r in res:
            dm = md(pos, r)
            do = md(opp, r)
            adv = do - dm  # positive means we are closer
            key = (adv, -dm, -r[1], -r[0])  # deterministic tie-break
            if best is None or key > best:
                best = key
        return best

    legal = []
    for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            legal.append((dx, dy))

    # If we can grab the closest resource immediately, do it.
    cur_best = None
    for r in res:
        dm = md((sx, sy), r)
        if dm == 0:
            return [0, 0]
        if cur_best is None or (dm, r[0], r[1]) < cur_best:
            cur_best = (dm, r[0], r[1])
    # Evaluate one-step lookahead to maximize reaching advantage.
    best_move = None
    best_score = None
    for dx, dy in legal:
        pos = (sx + dx, sy + dy)
        score = best_adv(pos)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]