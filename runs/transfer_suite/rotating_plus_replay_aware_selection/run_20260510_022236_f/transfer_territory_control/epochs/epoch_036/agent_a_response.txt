def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    my_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    opp_positions = list(opp_terr) if opp_terr else []
    if not opp_positions:
        ap = observation.get("opponent_position") or (w - 1, h - 1)
        opp_positions = [tuple(ap)]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs = sorted(dirs)  # deterministic tie-break

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def best_opp_dist(x, y):
        best = 10**9
        for ox, oy in opp_positions:
            d = man((x, y), (ox, oy))
            if d < best:
                best = d
        return best

    # Prefer moves that claim unclaimed, attack opponent territory, and reduce distance to their boundary.
    best_move = [0, 0]
    best_score = -10**18
    cur_opp_dist = best_opp_dist(sx, sy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        score = 0
        if (nx, ny) in opp_terr:
            score += 120  # flipping on entry
        if (nx, ny) in unclaimed:
            score += 35
        if (nx, ny) in my_terr:
            score += 10

        # Reduce distance to opponent territory
        nd = best_opp_dist(nx, ny)
        score += (cur_opp_dist - nd) * 6

        # Avoid getting too close to obstacles (simple local potential)
        near_obs = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                tx, ty = nx + ddx, ny + ddy
                if (tx, ty) in obs:
                    near_obs += 1
        score -= near_obs * 3

        # Encourage staying mobile early / not overly conservative late
        t = int(observation.get("turn_index") or 0)
        if (nx, ny) == (sx, sy):
            score -= (5 if t < 40 else 1)

        # Deterministic tie-break: higher score, then lexicographically smaller move
        if score > best_score or (score == best_score and [dx, dy] < best_move):
            best_score = score
            best_move = [dx, dy]

    return best_move