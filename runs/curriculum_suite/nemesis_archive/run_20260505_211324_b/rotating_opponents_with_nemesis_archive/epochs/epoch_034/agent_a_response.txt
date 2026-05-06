def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = o[0], o[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    opp_target = min(res, key=lambda p: (dist((ox, oy), p), p[0], p[1]))
    opp_d = dist((ox, oy), opp_target)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        myd_opp = dist((nx, ny), opp_target)
        score = 0
        score += 12 * (opp_d - myd_opp)  # deny/contest opponent target

        for tx, ty in res:
            myd = abs(nx - tx) + abs(ny - ty)
            opd = abs(ox - tx) + abs(oy - ty)
            margin = opd - myd  # positive if we are closer
            if (tx, ty) == opp_target:
                score += 120 - 6 * myd
            else:
                # favor big margins, but also slightly penalize being far
                score += 18 * margin - 2 * myd
                # small preference for nearer reachable resources
                if myd <= 2:
                    score += 10

        if score > best_val or (score == best_val and (dx, dy) < best_move):
            best_val = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]