def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for a in obstacles:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            obs.add((int(a[0]), int(a[1])))
        elif isinstance(a, dict) and "x" in a and "y" in a:
            obs.add((int(a["x"]), int(a["y"])))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
        elif isinstance(r, dict) and "x" in r and "y" in r:
            x, y = int(r["x"]), int(r["y"])
        else:
            continue
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
            res.append((x, y))
    if not res:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def min_obs_dist(x, y):
        if not obs:
            return 9
        m = 99
        for ox1, oy1 in obs:
            d = abs(x - ox1) + abs(y - oy1)
            if d < m:
                m = d
        return m if m != 99 else 9

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue

        # obstacle-aware: stay farther from obstacles unless it helps reaching a resource advantage
        safety = min_obs_dist(nx, ny)

        # from this hypothetical position, greedily pick a resource with advantage + tie-break on safety
        best_res_score = None
        for rx, ry in res:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd  # >0 means we are closer
            # prefer taking nearer resources when advantages are equal; discourage stepping near obstacles
            sc = (adv, -sd, safety)
            if best_res_score is None or sc > best_res_score:
                best_res_score = sc

        # map tuple score to scalar ordering for determinism
        final_sc = (best_res_score[0], best_res_score[1], best_res_score[2] + safety)
        if best_score is None or final_sc > best_score:
            best_score = final_sc
            best = [dx, dy]

    return best if best is not None else [0, 0]