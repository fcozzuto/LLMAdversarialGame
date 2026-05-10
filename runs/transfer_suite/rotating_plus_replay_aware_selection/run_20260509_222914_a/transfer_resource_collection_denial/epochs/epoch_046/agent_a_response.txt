def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]
    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    x, y, ox, oy = int(x), int(y), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                res.append((rx, ry))
    if not res:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18
    dirs = [(0, -1), (-1, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obs:
            continue
        s_pos = (nx, ny)
        # Evaluate best resource at this next step by advantage (opponent further than us).
        # Tie-break toward shorter self distance deterministically.
        maxv = -10**18
        for r in res:
            sd = dist(s_pos, r)
            od = dist((ox, oy), r)
            v = (od - sd) * 1000 - sd
            if v > maxv:
                maxv = v
        # Secondary preference: avoid giving opponent immediate closer access by penalizing max negative advantage.
        # (Keep deterministic and cheap.)
        worst_pen = 0
        for r in res:
            sd = dist(s_pos, r)
            od = dist((ox, oy), r)
            if od < sd:
                worst_pen -= (sd - od)
        score = maxv + worst_pen
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]